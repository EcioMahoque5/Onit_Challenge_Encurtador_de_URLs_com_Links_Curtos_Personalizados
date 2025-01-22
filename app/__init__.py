from flask import Flask
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import logging

bcrypt = Bcrypt()
jwt = JWTManager()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)


def create_app():
    app = Flask(__name__)
    
    load_dotenv()
    
    app.config.from_object('app.configs.Config')
    app.json.sort_keys = False
    
    bcrypt.init_app(app)
    jwt.init_app(app)
    
    from .routes import auth_bp, app_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(app_bp, url_prefix='/api')
    
    return app