from flask import (
    Blueprint, render_template, request, send_from_directory
)
from .layoutUtils import *
from .auth import *
from .db_photoalbum import *

bp = Blueprint('bl_home', __name__)

@bp.route('/',methods=('GET', 'POST'))
@manageCookiePolicy
def index():
    
    images = db_get_hp_images()
    record = db_get_user_data(g.user_id) #Can return None if user is not logged
    s3tileurl = os.environ["AWS_TILES_BUCKET_URL"]
    mc = set_menu("home") #to highlight menu option
    return render_template('home/index.html', mc=mc, 
                           images=images, record=record, s3tileurl=s3tileurl)


@bp.route('/about', methods=('GET', 'POST'))
@manageCookiePolicy
def about():

    mc = set_menu("about")
    return render_template('home/about.html', mc=mc)


@bp.route('/privacy-notice',methods=('GET', 'POST'))
def privacy():

    mc = set_menu("")
    return render_template('home/privacy-notice.html', mc=mc)


@bp.route('/terms-of-service',methods=('GET', 'POST'))
def termsofservice():
    mc = set_menu("")
    return render_template('home/terms-of-service.html', mc=mc)


#MANAGE sitemap and robots calls 
#These files are usually in root, but for Flask projects must
#be in the static folder
@bp.route('/robots.txt')
@bp.route('/sitemap.xml')
def static_from_root():
    return send_from_directory(current_app.static_folder, request.path[1:])

