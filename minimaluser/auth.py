import functools
from flask import current_app
from flask import (
    Blueprint, g, redirect, request, session,flash, url_for
)
import os
from .db_auth import *
bp = Blueprint('auth', __name__, url_prefix='/auth')

#IMPORTANT! Called for every request
@bp.before_app_request
def pre_operations(): 

    #ALL STATIC REQUESTS BYPASS!!!
    if request.endpoint == 'static':
        return

    #REDIRECT http -> https in HEROKU
    if 'DYNO' in os.environ:
        current_app.logger.critical("DYNO ENV !!!!")
        if request.url.startswith('http://'):
            url = request.url.replace('http://', 'https://', 1)
            code = 301
            return redirect(url, code=code)

    #USER ACCESS MANAGEMENT
    reset_g()
    #if call comes from url, gets the token from session
    user_token = session.get('ut') #user token
    db_set_g_from_token(user_token,os.environ["JWT_SECRET_HTML"]) #sets g parameters from the token
    if g.missing_token or g.invalid_token:
        promote_user_to_guest(os.environ["JWT_SECRET_HTML"]) #function used in HTML version only
        if g.invalid_token:
            flash("Session expired")
            return redirect("bl_home.index") #this will relaod g

    g.policyCode = 0 #SET DEFAULT INDEPENDENTLY TO WRAPPER


#WRAPPER FOR COOKIE SETTINGS 
def manageCookiePolicy(view):

    @functools.wraps(view)
    def wrapped_view(**kwargs):

        if request.method == 'POST':
            if 'btnAgreeAll' in request.form:
                session['cookie-policy'] = 3
            elif 'btnAgreeEssential' in request.form:
                session['cookie-policy'] = 0
            elif 'btnSaveCookieSettings' in request.form:
                session['cookie-policy'] = 0 #default
                if 'checkboxAnalysis' in request.form:
                    session['cookie-policy'] = 1
                if 'checkboxPersonalization' in request.form:
                    session['cookie-policy'] = 2
                if 'checkboxPersonalization' in request.form and 'checkboxAnalysis' in request.form:
                    session['cookie-policy'] = 3

        policyCode = session.get("cookie-policy")
        #possible values Null -> no info, 0 -> minimal, 1 -> Analysis, 
        #                                 2 -> Personalization, 3 -> All
        g.policyCode = 0
        if policyCode !=None:
            g.policyCode = policyCode

        g.showCookieAlert = False #DEFAULT
        if policyCode == None:
            g.showCookieAlert = True

        return view(**kwargs)

    return wrapped_view


#Wrappers to secure endpoints
def login_required(view):

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not g.user_is_logged:
            return redirect(url_for('bl_home.index'))
        return view(**kwargs)

    return wrapped_view

def confirmation_required(view):

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not g.user_confirmed:
            return redirect(url_for('bl_home.index'))
        return view(**kwargs)

    return wrapped_view


def get_u_state_from_g():
    #POSSIBLE VALUES:
    #   0 => undefined state
    #   1 => guest
    #   2 => user NOT confirmed
    #   3 => user confirmed
    if g.user_confirmed:
        return 3
    elif g.user_is_logged:
        return 2
    elif not g.missing_token and not g.invalid_token:
        #if user is logged then cannot be "guest" :)
        #So, if the token is there, and is valid => user is "guest"!
        return 1

    return 0
