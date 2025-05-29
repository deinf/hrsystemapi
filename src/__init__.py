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
from flasgger import Swagger
from src.config.swagger_config import swagger_template, swagger_config

from flask_cors import CORS


load_dotenv()
migrate = None

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.json = CustomJSONProvider(app)
    
    CORS(app)
    
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
    app.register_blueprint(blueprints.department)
    app.register_blueprint(blueprints.payroll)
    app.register_blueprint(blueprints.attendance)
    app.register_blueprint(blueprints.leave)
    app.register_blueprint(blueprints.performance)
    
    
    Swagger(app, template=swagger_template, config=swagger_config)
    
    
    # handle all error
    @app.errorhandler(constants.http_status_code.HTTP_500_INTERNAL_SERVER_ERROR)
    def handle_500(e):
        return jsonify({
            'message': 'Something went wrong'
        }), constants.http_status_code.HTTP_500_INTERNAL_SERVER_ERROR
    
    return app
