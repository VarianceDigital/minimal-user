import os

from flask import Flask
from flask_login import LoginManager

from .jinjafilters import *
from .errorhandlers import *

login_manager = LoginManager()
login_manager.login_view = 'auth.login'          # name of your login view
login_manager.login_message_category = 'warning'

def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ['SESSION_SECRET'],
    )

    #ADDS HANDLER TO CLOSE DATABASE AT END OF SESSION!
    from . import db
    db.init_app(app)

    # Flask-Login
    login_manager.init_app(app)

    # user_loader must be defined *after* app + DB
    from .db_auth import db_get_user_by_id
    from .user_model import User

    @login_manager.user_loader
    def load_user(user_id: str):
        # Flask-Login gives you a string; convert to int if needed
        try:
            aut_id = int(user_id)
        except (TypeError, ValueError):
            return None

        row = db_get_user_by_id(aut_id)
        if row is None:
            return None
        return User.from_db_row(row)


    from . import bl_home
    app.register_blueprint(bl_home.bp)

    from . import bl_photoalbum
    app.register_blueprint(bl_photoalbum.bp)

    from . import bl_auth
    app.register_blueprint(bl_auth.bp)

    from . import bl_email_confirm
    app.register_blueprint(bl_email_confirm.bp)

    #Add other blueprints if needed

    from . import auth
    app.register_blueprint(auth.bp)

    #ADDS HANDLER FOR ERRORs
    app.register_error_handler(500, error_500)
    app.register_error_handler(404, error_404)

    #JINJA FILTERS
    app.jinja_env.filters['slugify'] = slugify
    app.jinja_env.filters['displayError'] = displayError 

    return app