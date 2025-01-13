import os
from flask import Flask, jsonify
from flask_migrate import Migrate
from src.database.database import db
from src.blueprints import blueprints
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
from src.constants import constants
from datetime import timedelta
from src.utils.decorators import CustomJSONProvider


load_dotenv()
migrate = None

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.json = CustomJSONProvider(app)
    
    if test_config is None:
        app.config.from_mapping(
            SQLALCHEMY_DATABASE_URI=os.getenv('db_path'),
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            JWT_SECRET_KEY=os.getenv('JWT_SECRET_KEY'),
            JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30),
            JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7),
        )
        
        global migrate
        migrate = Migrate(app, db)
    else:
        app.config.from_mapping(test_config)
        
    
        
    db.init_app(app)
    JWTManager(app)
    
    app.register_blueprint(blueprints.auth)
    app.register_blueprint(blueprints.user)
    
    
     # handle all error
     #!uncoment this if you want to show the error message
    @app.errorhandler(constants.http_status_code.HTTP_500_INTERNAL_SERVER_ERROR)
    def handle_500(e):
        return jsonify({
            'message': 'Something went wrong'
        }), constants.http_status_code.HTTP_500_INTERNAL_SERVER_ERROR
    
    return app
