from flask import Flask
from flask_bcrypt import Bcrypt
from app.config.config import Config
from datetime import timedelta
from app.db import create_app_db
from app.mail import create_app_mail
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config.from_pyfile("..\config.cfg")
app.config.from_object(Config)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_SECRET_KEY"] = "super-secret-key"
app.config["JWT_ACCESS_COOKIE_NAME"] = "Authorization"
bcrypt = Bcrypt(app)
create_app_db(app)
create_app_mail(app)
# create_app_gpt(app)


def create_blueprint():
    from app.accounts.views import accounts_bp
    app.register_blueprint(accounts_bp)


create_blueprint()
