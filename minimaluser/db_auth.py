from psycopg2.extras import RealDictCursor
from flask import current_app, g, session
from werkzeug.security import check_password_hash, generate_password_hash
from .db import get_db
from .s3_operations import *
import jwt
import os
import random
import re
import string
import secrets
import requests
import uuid


#************************************
#  USER STATE WITH GLOBAL VARIABLE  *
#            AND SESSION            *
#               START               *
#************************************

def reset_g():
    #DEFAULTS
    g.user_id = None
    g.user_email = ''
    g.user_name = ''
    g.user_is_logged = False
    g.user_confirmed = False
    g.missing_token = True #Becaomes False only if the JWT token is present
    g.invalid_token = False #Becaomes True only if token EXISTS but is not valid
    g.user_token = '' #Used for API that may return Guest token
    

def set_g_for_guest_token(secret):
    token = build_guest_token(secret)

    g.user_id = 0
    g.user_email = 'guest@variancedigital.com'
    g.user_name = 'guest'
    g.user_is_logged = False #<--- the user is NOT logged in
    g.user_confirmed = False
    g.missing_token = False 
    g.invalid_token = False #The token exists, is valid, and contains the GUEST user's data.
    g.user_token = token


def db_set_g_from_token(token,secret):
    
    if not token or len(token)==0:
        #token is missing, g will contain default values
        return 

    #DECODE 
    jwt_secret = secret
    aut_id = ''
    aut_email = ''

    try:
        decoded = jwt.decode(token, jwt_secret, algorithms=['HS256'])
        aut_id = decoded['aut_id']
        aut_email = decoded['aut_email']
    except jwt.DecodeError:
        g.user_id = None
        g.user_email = ''
        g.user_name = ''
        g.user_is_logged = False 
        g.user_confirmed = False
        g.missing_token = False
        g.invalid_token = True
        g.user_token = ''
        # something is wrong with existing token
        return
        
    if aut_id==0:
        #USER IS GUEST!
        g.user_id = 0
        g.user_email = 'guest@variancedigital.com'
        g.user_name = 'guest'
        g.user_is_logged = False #<--- the user is NOT logged in
        g.user_confirmed = False
        g.missing_token = False 
        g.invalid_token = False #The token exists, is valid, and contains the GUEST user's data.
        g.user_token = token
    else:
        #USER SHOULD EXIST        
        db = get_db()
        cur = db.cursor(cursor_factory=RealDictCursor)

        #CHECK IF USER IS STILL VALID
        cur.execute("""SELECT *
                        FROM minimaluser.tbl_auth
                        WHERE aut_id = %s AND aut_email= %s AND aut_isvalid=true""", (aut_id, aut_email,)
        )

        user = cur.fetchone()

        cur.close()

        if user is None:
            #THE USER IS NOT IN THE DB!
            g.user_id = None
            g.user_email = ''
            g.user_name = ''
            g.user_is_logged = False #<--- the user is NOT logged in
            g.user_confirmed = False
            g.missing_token = False 
            g.invalid_token = True #Token exists but is invalid!
            g.user_token = ''
        else:
            g.user_id = user['aut_id']
            g.user_email = user['aut_email']
            g.user_name = user['aut_name']
            g.user_is_logged = True #<--- the user IS logged in
            g.user_confirmed = user['aut_confirmed']
            g.missing_token = False 
            g.invalid_token = False #The token exists, is valid and contains the specific user's data
            g.user_token = token


def build_guest_token(secret):

    payloadJWT={}
    payloadJWT["aut_id"] =0
    payloadJWT["aut_email"]='guest@variancedigital.com'
    payloadJWT["rand"] = create_random_access_key() #add random value to stir things up

    #Convert payload into JWT token
    return jwt.encode(payloadJWT, secret, algorithm='HS256')


def promote_user_to_guest(secret):

    set_g_for_guest_token(secret)

    session["ut"] = g.user_token #this will unlock partial functionality
    session['show_users_images_only']=False


def build_user_token(user, secret):
        
    payloadJWT={}
    payloadJWT["aut_id"]=user['aut_id']
    payloadJWT["aut_email"]=user['aut_email']
    payloadJWT["rand"]=random.random()

    #Convert payload into JWT token
    return jwt.encode(payloadJWT, secret, algorithm='HS256')


def promote_user_to_logged(user_obj, secret):

    token = build_user_token(user_obj, secret)

    session["ut"] = token #this will unlock full functionality
    session['show_users_images_only']=False


def user_login(user, secret):
        
    token = build_user_token(user, secret)

    session["ut"] = token #this will unlock full functionality
    session['show_users_images_only']=False
    

def user_logout(secret):
    #log off user, user becomes GUEST
    promote_user_to_guest(secret)
    session['show_users_images_only']=False
    session['show_favs_only']=False

#************************************
#  USER STATE WITH GLOBAL VARIABLE  *
#            AND SESSION            *
#               END                 *
#************************************



#**********************************
#  ACCESS KEY AND OTP UTILITIES   *
#            START                *
#**********************************

def create_random_access_key():

    alphabet = string.ascii_letters + string.digits
    access_key = ''.join(secrets.choice(alphabet) for i in range(10))
    return access_key


def create_numeric_otp():
    alphabet = string.digits
    otp = ''.join(secrets.choice(alphabet) for i in range(6))
    return otp


def db_save_otp_for_user_with_email(email, otp):
    db = get_db()
    cur = db.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
                    UPDATE minimaluser.tbl_auth
	                set aut_otp=%s
	                WHERE aut_email=%s
                    """, 
                    (otp, email, )
    )
    
    db.commit()

    #GET USER ID TO RETURN
    cur.execute("""SELECT aut_id
                    FROM minimaluser.tbl_auth
                    WHERE aut_email = %s""", 
                    (email,)
    )

    user = cur.fetchone()

    cur.close()

    return user['aut_id']


def db_update_user_key(aut_id, access_key):
    db = get_db()
    cur = db.cursor(cursor_factory=RealDictCursor)
    hash = generate_password_hash(access_key, "sha256")
    cur.execute("""
                    UPDATE minimaluser.tbl_auth
	                set aut_key=%s, aut_key_temp=%s
	                WHERE aut_id=%s
                    """, 
                    (hash, access_key, aut_id, )
    )
    
    db.commit()
    cur.close()


def db_reset_user_otp(aut_id):
    db = get_db()
    cur = db.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
                    UPDATE minimaluser.tbl_auth
	                set aut_otp=null
	                WHERE aut_id=%s
                    """, 
                    (aut_id, )
    )

    db.commit()
    cur.close()

#**********************************
#  ACCESS KEY AND OTP UTILITIES   *
#              END                *
#**********************************



#*******************************
#     VALIDATION FUNCTIONS     *
#            START             *
#*******************************

def db_check_user(form_data):
    email = form_data['email']
    key = form_data['key']

    db = get_db()
    cur = db.cursor(cursor_factory=RealDictCursor)
    #Check for VALID user
    cur.execute("""
                SELECT * FROM minimaluser.tbl_auth 
                WHERE aut_email=%s AND aut_isvalid=true 
                """ , 
                (email,)
    )

    user = cur.fetchone()

    cur.close()

    if user:
        if check_password_hash(user['aut_key'], key):
            return user

    return None


regex = r'^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'


def check_email(email):
    error = 0
    if email is None:
        error = 101 #Email/Login non valida
    elif len(email)>100:
        error = 101 #Email/Login non valida
    elif not (re.search(regex,email)):  
        error = 101 #Email/Login non valida

    return error


def db_check_if_email_exists(email):
    error = 0

    db = get_db()
    cur = db.cursor(cursor_factory=RealDictCursor)

    cur.execute(
        'SELECT * FROM minimaluser.tbl_auth WHERE aut_email=%s', (email,)
    )

    user = cur.fetchone()
    cur.close()
    
    if not user is None:
        error = 102 #Email already there 

    return error   


def validate_sign_up(record):
    error=0
    email=record['email']
    error = check_email(email)
    if error == 0:
        error = db_check_if_email_exists(email)
    return error


def db_check_otp(aut_id, otp):
    error = 0

    db = get_db()
    cur = db.cursor(cursor_factory=RealDictCursor)

    cur.execute(
        'SELECT * FROM minimaluser.tbl_auth WHERE aut_id=%s AND aut_otp=%s', 
        (aut_id, otp,)
    )

    user = cur.fetchone()
    cur.close()
    
    if user is None:
        error = 111 #incorrect otp

    return error   


def check_if_key_contains_number(key):
    error = 0
    if not any(char.isdigit() for char in key):
        error = 110 #key does not contain any digit
    return error


def check_if_key_contains_letters(key):
    error = 0
    if not re.search('[a-zA-Z]',key):
        error = 110 #pwd does not contain any letter
    return error


def check_valid_key(key):
    error = 0
    #CRITERIO DI VALIDITA' DELLA PASSWORD
    if key is None:
        error = 108 #key too short
        return error

    if len(key)<8 or len(key)>100:
        error = 109 #pwd too short, too long
    else:
        error = check_if_key_contains_number(key)
        if error==0:
            error = check_if_key_contains_letters(key)
    return error


def db_check_username_unique(user_name):
    error = 0
    db = get_db()
    cur = db.cursor(cursor_factory=RealDictCursor)

    cur.execute("""SELECT * FROM minimaluser.tbl_auth
	                WHERE aut_name=%s
                    """, 
                    (user_name,)
    )
    user = cur.fetchone()

    cur.close()

    if user:
        error = 122 #There is a user with user_name. Error not unique!

    return error


def db_check_username(user_name):
    error = 0
    if len(user_name)<4:
        error = 120 #user name too short
    elif len(user_name)>99:
        error = 121 #user name too long
    else:
        error = db_check_username_unique(user_name)
    return error

#*******************************
#     VALIDATION FUNCTIONS     *
#              END             *
#*******************************



#******************************
#   Create Read Update USER   *
#           START             *
#******************************

def db_create_user_entry(email, access_key, custom_name, tile_filename):
    db = get_db()
    cur = db.cursor(cursor_factory=RealDictCursor)

    hash = generate_password_hash(access_key, "sha256")
    #CREATE NEW USER
    cur.execute("""
                    INSERT INTO minimaluser.tbl_auth(
	                aut_email, aut_key, aut_key_temp, aut_name, aut_tile)
	                VALUES (%s, %s, %s,%s,%s)
                    RETURNING aut_id;
                    """, 
                    (email, hash, access_key, custom_name, tile_filename,)
    )
    
    #GET THE NEWLY CREATED ID OF THE USER
    newId = cur.fetchone()
    #newid = newid[0] ho cambiato il tipo di cursore
    newId = newId['aut_id'] 

    db.commit()
    cur.close()

    return newId


def db_get_user_data(aut_id):
    db = get_db()
    cur = db.cursor(cursor_factory=RealDictCursor)

    #FIRST GET ALL IMAGES THAT SHOULD BE DELETED.
    #THE FILES IN THE S3 BUCKETS WILL BE DELETED "IN BACKGROUND"

    cur.execute("""SELECT * FROM minimaluser.tbl_auth
	                WHERE aut_id=%s
                    """, 
                    (aut_id,)
    )

    user_data = cur.fetchone()
    cur.close()

    return user_data


def db_update_user_name(aut_id, aut_name):
    db = get_db()
    cur = db.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
                    UPDATE minimaluser.tbl_auth
	                set aut_name=%s
	                WHERE aut_id=%s
                    """, 
                    (aut_name, aut_id, )
    )

    db.commit()
    cur.close()


def db_update_user(aut_id, email, access_key):
    db = get_db()
    cur = db.cursor(cursor_factory=RealDictCursor)
    hash = generate_password_hash(access_key, "sha256")
    cur.execute("""
                    UPDATE minimaluser.tbl_auth
	                set aut_email=%s, aut_key=%s, aut_key_temp=%s, aut_confirmed=false
	                WHERE aut_id=%s
                    """, 
                    (email, hash, access_key, aut_id, )
    )
    
    db.commit()
    cur.close()

#******************************
#   Create Read Update USER   *
#            END              *
#******************************



#*********************************
#  CONFIRMATION EMAIL UTILITIES  *
#            START               *
#*********************************

def create_email_link_token(new_id, email, secret):

    payloadJWT={}
    payloadJWT["aut_id"]=new_id
    payloadJWT["aut_email"]=email
    payloadJWT["aut_random_key"]=create_random_access_key() #<-- stir things up

    #Convert payload into JWT token
    token = jwt.encode(payloadJWT, secret, algorithm='HS256')
    return token


def ext_send_email(user_email, user_aut_key_or_otp, email_link_url, email_blueprint, email_service, email_link_token):
    #PACK ALL INFO IN JWT TOKEN
    #FOR THIS DEMO WE SEND A KEY TO THE USER VIA EMAIL
    payloadJWT={}
    payloadJWT["user_email"]=user_email
    payloadJWT["user_aut_key_or_otp"]=user_aut_key_or_otp
    payloadJWT["email_link_url"]=email_link_url
    payloadJWT["email_link_token"]=email_link_token #PACKING AN ALREADY ENCODED TOKEN!

    mailersecret = os.environ["JWT_MAILER_SECRET"]
    #Convert payload into JWT token
    encoded_payload = jwt.encode(payloadJWT, mailersecret, algorithm='HS256')
    
    #CALL MAILER
    mailer_url = os.environ["MAILER_URL"] # complete url with final /
    r = requests.get(mailer_url+email_blueprint+'/'+email_service+'/'+encoded_payload)


def db_set_user_confirmed(aut_id):
    db = get_db()
    cur = db.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
                    UPDATE minimaluser.tbl_auth
	                set aut_confirmed=true
	                WHERE aut_id=%s
                    """, 
                    (aut_id,)
    )
    
    db.commit()
    cur.close()


def db_check_email_link_token(token,secret):
    
    if not token or len(token)==0:
        #token is missing, g will contain default values
        return 1,0

    #DECODE 
    jwt_secret = secret
    aut_id = ''
    aut_email = ''

    try:
        decoded = jwt.decode(token, jwt_secret, algorithms=['HS256'])
        aut_id = decoded['aut_id']
        aut_email = decoded['aut_email']
    except jwt.DecodeError:
        return 1,0
        
    
    #USER SHOULD EXIST        
    db = get_db()
    cur = db.cursor(cursor_factory=RealDictCursor)

    #CHECK IF USER IS STILL VALID
    cur.execute("""SELECT aut_id, aut_email
                    FROM minimaluser.tbl_auth
                    WHERE aut_id = %s AND aut_email= %s AND aut_isvalid=true""", (aut_id, aut_email,)
    )

    user = cur.fetchone()

    cur.close()

    if user is None:
        #THE USER IS NOT IN THE DB!
        return 1,0
    else:
        return 0, user['aut_id']

#*********************************
#  CONFIRMATION EMAIL UTILITIES  *
#             END                *
#*********************************



#*************************
#      DELETE USER       * 
#         START          *
#*************************

def db_delete_account(aut_id):
    db = get_db()
    cur = db.cursor(cursor_factory=RealDictCursor)


    #GET THE USER TILE
    cur.execute("""SELECT aut_tile FROM minimaluser.tbl_auth
	                WHERE aut_id=%s
                    """, 
                    (aut_id,)
    )
    tileToBeRemoved_rec = cur.fetchone()
    tileToBeRemoved = tileToBeRemoved_rec['aut_tile']

    cur.execute("""DELETE FROM minimaluser.tbl_auth
	                WHERE aut_id=%s
                    """, 
                    (aut_id,)
    )
    
    #RECORDS ALL OTHER RELATED ENTITIES ARE DELETED AUTOMATICALLY
    #DUE TO CONSTRAINTS
    
    db.commit()
    cur.close()

    return tileToBeRemoved

#*************************
#      DELETE USER       * 
#          END           *
#*************************



#*******************************
#  CUSTOM USER NAMES AND TILES *
#          START               *
#*******************************

def db_create_custom_tile(custom_color):
    
    db = get_db()
    cur = db.cursor(cursor_factory=RealDictCursor)

    #1. COUNT TILES
    cur.execute("SELECT COUNT(*) FROM namer.tbl_tile")

    count_col = cur.fetchone()
    num_tiles = count_col['count']

    #2. SELECT ONE TILE RANDOMLY
    tile_id_random = random.randint(1,num_tiles)

    cur.execute("""SELECT * FROM namer.tbl_tile WHERE tle_id=%s""",
                (tile_id_random,)
    )
    user_tile = cur.fetchone()

    cur.close()

    #3. CREATE AN UNIQUE FILENAME FOR THE CUSTOM TILE
    unique_filename = str(uuid.uuid4())+'.svg'
    
    #4. GET SVG TEXT OF TILE
    tile_text = user_tile['tle_svg']

    #5. FIND ALL THE COLORS OF THE TILE
    fills = re.findall(r'cls-\d+{fill:#\w+;}', tile_text)
    allcolors = list(map(lambda x: re.findall('#\w+;',x)[0], fills))
    
    #6. SUBSTITUTE ALL COLORS WITH RANDOM COLORS
    #   FIRST AND LAST COLORS ARE SPECIAL
    r = lambda: random.randint(0,255)
    for idx, c in enumerate(allcolors):
        #THE FIRST COLOR IS THE CUSTOM NICKNAME COLOR!
        if idx == 0:
            tile_text = tile_text.replace(c, custom_color)
        else:
            randomcolor = '#{:02x}{:02x}{:02x}'.format(r(), r(), r())
            tile_text = tile_text.replace(c,randomcolor)

    #7. CHOOSE A RANDOM FLUE COLOR
    fluecolors = ["#c71585","#ff1493","#dc1435","#00bfff","#ffda89","#477979","#f4a460"]
    fluerandomcolor = random.choice(fluecolors)

    #8. THE LAST OF THE TILES COLOR IS SUBSTITUTED WITH A FLUE COLO
    tile_text = tile_text.replace(randomcolor,fluerandomcolor)
    return unique_filename, tile_text
    

def db_create_custom_name():
    #0. Open db connection
    db = get_db()
    cur = db.cursor(cursor_factory=RealDictCursor)

    #1. GET MIN AND MAX ID FOR ADJECTIVES
    cur.execute("SELECT min(nou_id), max(nou_id) FROM namer.tbl_noun where nou_type=1")

    record = cur.fetchone()
    min_adj_id = record['min']    
    max_adj_id = record['max']
    #1a. CREATE RANDOM ID FOR ADJECTIVE   
    rnd_adj_id = random.randint(min_adj_id,max_adj_id) 

    #2. GET MIN AND MAX ID FOR ANIMALS
    cur.execute("SELECT min(nou_id), max(nou_id) FROM namer.tbl_noun where nou_type=2")

    record = cur.fetchone()
    min_animal_id = record['min']    
    max_animal_id = record['max']
    #2a. CREATE RANDOM ID FOR ANIMALS
    rnd_animal_id = random.randint(min_animal_id,max_animal_id)

    #3. GET MIN AND MAX ID FOR COLORS
    cur.execute("SELECT min(nou_id), max(nou_id) FROM namer.tbl_noun where nou_type=3")

    record = cur.fetchone()
    min_color_id = record['min']    
    max_color_id = record['max']
    #3a. CREATE RANDOM ID FOR COLOR
    rnd_color_id = random.randint(min_color_id,max_color_id)

    #4 GET ADJECTIVE, NAME and COLOR
    cur.execute("SELECT * FROM namer.tbl_noun where nou_id=%s",(rnd_adj_id,))
    record = cur.fetchone()
    rnd_adj = record['nou_noun']

    cur.execute("SELECT * FROM namer.tbl_noun where nou_id=%s",(rnd_animal_id,))
    record = cur.fetchone()
    rnd_animal = record['nou_noun']

    cur.execute("SELECT * FROM namer.tbl_noun where nou_id=%s",(rnd_color_id,))
    record = cur.fetchone()
    rnd_color_name = record['nou_noun']
    rnd_color = "#"+record['nou_color']

    cur.close()

    #GET RANDOM NUMBER
    rnd_number = create_numeric_otp()

    #CREATE CUSTOM NICKNAME
    custom_name = "{}-{}-{}-{}".format(rnd_adj,rnd_animal,rnd_number,rnd_color_name)
    
    return custom_name, rnd_color    

#*******************************
#  CUSTOM USER NAMES AND TILES *
#          END                 *
#*******************************
