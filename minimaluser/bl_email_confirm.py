from flask import (
    Blueprint, url_for, flash, redirect
)
from flask_login import login_user

from .user_model import User

from .layoutUtils import *
from .db_auth import *
import os


bp = Blueprint('bl_email_confirm', __name__)


@bp.route('/emailconfirmationhtml/<email_link_token>')
def emailconfirmationhtml(email_link_token):

    error, aut_id = db_check_email_link_token(email_link_token, os.environ["JWT_SECRET_HTML"])
    if error==0:
        user_row = db_get_user_data(aut_id)
        user = User.from_db_row(user_row)
        login_user(user)
        db_set_user_confirmed(user_row)
        flash('Your email is confirmed, have fun')
    else:
        flash('Problems with your confirmation email')
    
    return redirect(url_for('bl_photoalbum.list'))
 
