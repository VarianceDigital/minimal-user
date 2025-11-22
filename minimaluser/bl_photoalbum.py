from flask import (
    Blueprint, render_template, url_for, flash
)
from flask_login import login_required

from .layoutUtils import set_menu
from .auth import manage_cookie_policy, confirmation_required
from .db_photoalbum import db_get_all_images, db_get_image_details

bp = Blueprint('bl_photoalbum', __name__, url_prefix='/album')


@bp.route('/',methods=('GET', 'POST'))
@confirmation_required
@manage_cookie_policy
def list():
    mc = set_menu("list")

    images = db_get_all_images()
    return render_template('photoalbum/list_of_images.html', mc=mc, images=images)



@bp.route('/imagedetails/<int:img_id>',methods=('GET', 'POST'))
@login_required
@manage_cookie_policy
def imagedetails(img_id):
    mc = set_menu("imagedetails")

    image = db_get_image_details(img_id)
    return render_template('photoalbum/image_details.html', mc=mc, image=image)


