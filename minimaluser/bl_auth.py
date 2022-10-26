from flask import (
    Blueprint, render_template, url_for, flash
)

from .auth import *
from .db_auth import *
from .layoutUtils import *


bp = Blueprint('bl_auth', __name__, url_prefix='/auth')

@bp.route('/signup',methods=('GET', 'POST'))
@manage_cookie_policy
def signup():
    mc = set_menu("signup")
    error = 0
    if request.method == 'POST':
        if 'btn_signup' in request.form:
            form_data = read_data_from_form()
            error = validate_sign_up(form_data)
            if error == 101:
                flash("Invalid email")
            elif error == 102:
                flash("Email already used for a subscription")
            elif error == 0:
                email = form_data['email']
                access_key = create_random_access_key()
                custom_name, custom_color = db_create_custom_name()
                new_id = db_create_user_entry(form_data['email'], access_key, custom_name)
                db_set_custom_tile(new_id,custom_color)
                #Prepare data for confirmation email
                email_link_token = create_email_link_token(new_id, email, os.environ["JWT_SECRET_HTML"])
                
                #Send confirmaton email with visible access key
                ext_send_email(email, access_key,'https://minimal-user.variancedigital.com/emailconfirmationhtml/', 'emailservice-usr','signup', email_link_token)

                #Promote user to logged!
                user_obj = {'aut_id':new_id, 'aut_email':email}
                promote_user_to_logged(user_obj, os.environ["JWT_SECRET_HTML"])

                #Notify user!
                flash("Wellcome to the 'Minimal+User' demo application.") 
                flash("We sent you an email containing a link: please click the link and confirm your subscription.") 
                flash("'Minimal+User' assigned you a user name: {}; you can change it using your profile.".format(custom_name)) 
                flash("'Minimal+User' gave you a small pretty icon: hope you like it.") 

                return redirect(url_for('bl_home.index'))

    return render_template('auth/signup_frm.html', mc=mc, error=error)
 

@bp.route('/login',methods=('GET', 'POST'))
@manage_cookie_policy
def login():
    mc = set_menu("login")
    if request.method == 'POST':
        if 'btn_unlock' in request.form:
            form_data = read_data_from_form()
            user = db_check_user(form_data)
            if user:
                user_login(user,os.environ["JWT_SECRET_HTML"]) #UNLOCK ALL FEATURES
                flash("You are logged in :)") 
                return redirect(url_for('bl_home.index'))
            else:
                user_logout(os.environ["JWT_SECRET_HTML"])
                flash("Could not login!")

    return render_template('auth/login_frm.html', mc=mc)


@bp.route('/logout')
@manage_cookie_policy
def logout():
    user_logout(os.environ["JWT_SECRET_HTML"])
    flash("See you soon!") 
    return redirect(url_for('bl_home.index'))


@bp.route('/userprofile',methods=('GET', 'POST'))
@login_required
@manage_cookie_policy
def userprofile():
    error = 0
    
    mc = set_menu("userprofile")
    if request.method == 'POST':
        
        if 'btn_save_username'  in request.form:
            form_data = read_data_from_form()
            user_name = form_data['username']
            error = db_check_username(user_name)
            if error == 120:
                flash("User name too short")
            elif error == 121:
                flash("User name too logn")
            elif error == 122:
                flash("User name already in use")
            else:
                db_update_user_name(g.user_id, user_name)
                #MUST UPADTE GLOBAL
                g.user_name = user_name
                flash("User name updated!")
        elif 'btn_changeaccesskey'  in request.form:
            form_data = read_data_from_form()
            confirm_access_key = form_data['confirmaccesskey']
            new_access_key = form_data['newaccesskey']
            current_access_key = form_data['accesskey']
            if new_access_key!=confirm_access_key:
                error = 106
            elif db_check_user({'email':g.user_email, 'key':current_access_key}) is None:
                #"recycling" check_user
                error = 105
            else:
                error = check_valid_key(new_access_key)
                if error == 0:
                    db_update_user_key(g.user_id, new_access_key)
                    flash("Access key updated!")
                else:
                    error = 107 #errors 108, 109, 110 -> 107

        elif 'btn_save_email' in request.form:
            form_data = read_data_from_form()
            
            error = validate_sign_up(form_data)
            if error == 101:
                flash("Invalid email")
            elif error == 102:
                flash("Email already used for a subscription")
            elif error == 0:
                email = form_data['email']
                access_key = create_random_access_key()
                db_update_user(g.user_id, email, access_key)
                
                #Prepare data for confirmation email
                email_link_token = create_email_link_token(g.user_id, email, os.environ["JWT_SECRET_HTML"])
                
                #Send confirmaton email with visible access key
                ext_send_email(email, access_key, 'https://minimal-user.variancedigital.com/emailconfirmationhtml/', 'emailservice-usr','change', email_link_token)

                #Notify user!
                flash("Your email has been updated.") 
                flash("We sent you a new email containing a link: please click the link and confirm your change.") 
                flash("WARNING: your access key has been changed!") 

                return redirect(url_for('bl_home.index'))             

    record = db_get_user_data(g.user_id)
    s3tileurl = os.environ["AWS_TILES_BUCKET_URL"]
    return render_template('auth/profile.html',
                                mc=mc,s3tileurl = s3tileurl,record=record, error=error )


@bp.route('/forgotkey',methods=('GET', 'POST'))
@manage_cookie_policy
def forgotkey():

    mc = set_menu("forgotkey")
    error = 0    

    if request.method == 'POST':
        if 'btn_send_new_key' in request.form:
            form_data = read_data_from_form()
            email = form_data['email']
            nice_error = db_check_if_email_exists(email)
            if nice_error==102:
                #EMAIL EXISTS! IT'S WHAT WE WANT

                #Prepare data for "reset key" email

                otp = create_numeric_otp()
                aut_id = db_save_otp_for_user_with_email(email, otp)
                #db_save_otp_for_user_with_email returns the user id having "email" as email address

                email_link_token = create_email_link_token(aut_id, email, os.environ["JWT_SECRET_HTML"])
                
                #Send "reset key" email - SENDING OTP instead of access key
                ext_send_email(email, otp, 'email-link-not-used', 'emailservice-usr','resetkey', email_link_token)

                #Notify user!
                flash("We sent you an email. Use the OTP code inside to reset your access key.") 
                return redirect(url_for('bl_auth.resetkey',token=email_link_token ))
            else:
                flash("Email not found")

    return render_template('auth/forgot_frm.html', mc=mc, error = error)


@bp.route('/resetkey/<token>',methods=('GET', 'POST'))
@manage_cookie_policy
def resetkey(token):

    #SECURITY CHECK: DECODE OTP PASSED TO ENDPOINT
    try:
        decoded = jwt.decode(token, os.environ["JWT_SECRET_HTML"], algorithms=['HS256'])
        aut_id = decoded['aut_id']
    except jwt.DecodeError:
        return redirect(url_for('bl_home.index'))

    mc = set_menu("resetkey")
    error = 0    

    if request.method == 'POST':
        if 'btn_resetaccesskey' in request.form:            
            form_data = read_data_from_form()
            otp = form_data['otp']
            new_access_key = form_data['newaccesskey']
            confirm_access_key = form_data['confirmaccesskey']
            error = db_check_otp(aut_id, otp) #may give error 111
            if error==0:
                if new_access_key!=confirm_access_key:
                    error = 106
                else:
                    error = check_valid_key(new_access_key)
                    if error == 0:
                        db_update_user_key(aut_id, new_access_key)
                        db_reset_user_otp(aut_id)
                        flash("Access key updated!")
                        flash("Use your new access key to login")
                        return redirect(url_for('bl_home.index'))
                    else:
                        error = 107 #errors 108, 109, 110 -> 107    

    return render_template('auth/resetkey_frm.html', mc=mc, error = error)


@bp.route('/deleteaccount')
@login_required
def deleteaccount():
    
    tile_to_be_removed= db_delete_account(g.user_id)
    user_logout(os.environ["JWT_SECRET_HTML"])
    
    delete_file_from_s3(tile_to_be_removed, os.environ["AWS_TILES_BUCKET_NAME"])

    flash("Account deleted")

    return redirect(url_for('bl_home.index'))

