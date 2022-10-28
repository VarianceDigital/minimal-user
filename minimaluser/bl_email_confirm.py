from flask import (
    Blueprint, url_for, flash, redirect
)

from .layoutUtils import *
from .db_auth import *
import os


bp = Blueprint('bl_email_confirm', __name__)


@bp.route('/emailconfirmationhtml/<email_link_token>')
def emailconfirmationhtml(email_link_token):

    error, aut_id = db_check_email_link_token(email_link_token, os.environ["JWT_SECRET_HTML"])
    if error==0:
        user = db_get_user_data(aut_id)
        db_set_user_confirmed(user,os.environ["JWT_SECRET_HTML"])
        flash('Your email is confirmed, have fun')
    else:
        flash('Problems with your confirmation email')
    
    return redirect(url_for('bl_photoalbum.list'))
 
