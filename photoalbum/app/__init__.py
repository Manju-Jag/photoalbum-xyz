from flask import Flask, request, current_app
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os

app = Flask(__name__)
db = SQLAlchemy(app)
app.config.from_object(Config)
migrate = Migrate(app, db)
login = LoginManager()
login.login_view = 'login'
login.login_message = ('Please log in to access this page.')
# with app.app_context():
    # db.create_all()

def create_app(config_class=Config):
    # app = Flask(__name__)
    # app.config.from_object(Config)
    # db.init_app(app)
    # migrate.init_app(app, db)
    login.init_app(app)
    # login.login_view = 'login'
    UPLOAD_FOLDER = 'C:/Users/Manju/Documents/internpro/photoalbum/app/static/uploads/'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    
    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)


    return app
    # if __name__ == '__main__':
    #     return(app.run(host='127.0.0.1', port=8080, debug=True))
from app import models
