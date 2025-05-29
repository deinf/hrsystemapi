from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from src.constants.constants import http_status_code
from src.database.database import User, db
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required, get_jwt
from dotenv import load_dotenv
from sqlalchemy import or_
from flasgger import swag_from

import os
load_dotenv()

auth = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

@auth.before_app_request
def create_admin_user():
    if not User.query.filter(or_(User.role=='admin', User.username=="admin")).first():
        admin = User(
            username='admin',
            email='admin@admin.com',
            role='admin',
            password_hash=generate_password_hash(os.getenv('admin_password'))
        )
        db.session.add(admin)
        db.session.commit()



@auth.post('/login')
@swag_from("../../docs/auth/login.yaml")
def login():
    identifier = ''
    password = ''
    # check if request if post body
    if request.form:
        identifier = request.form.get('identifier')
        password = request.form.get('password')

    # Check if request is raw JSON
    elif request.is_json:
        data = request.get_json()
        identifier = data.get('identifier')
        password = data.get('password')

    if not identifier or not password:
        return jsonify({
            "message" : "Both identifier and password are required"
        }), http_status_code.HTTP_400_BAD_REQUEST
        
    user = User.query.filter(or_(User.email==identifier, User.username==identifier)).first()

    if user:
        is_pass_correct = check_password_hash(user.password_hash, password)
        
        if is_pass_correct:
            refresh = create_refresh_token(identity=user.id, additional_claims={"role": user.role})
            access = create_access_token(identity=user.id, additional_claims={"role": user.role})
            
            return jsonify({
                'user': {
                    'username' : user.username,
                    'email' : user.email,
                    'role' : user.role,
                    'access_token' : access,
                    'refresh_token' : refresh,
                    
                }
            }),http_status_code. HTTP_200_OK
    return jsonify({
            'message': 'Invalid Username/Email or Password',
    }),http_status_code.HTTP_404_NOT_FOUND


@auth.post('/token/refresh')
@jwt_required(refresh=True)
@swag_from("../../docs/auth/refresh_token.yaml")
def refresh():
    claims = get_jwt() 
    role = claims.get("role")
    identity = get_jwt_identity()
    access_token = create_access_token(
        identity=identity,
        additional_claims={"role": role, "type": "access"}
    )
    # refresh = create_refresh_token(identity=identity, additional_claims=claims)
    
    return jsonify({
        'access_token' : access_token,
        # 'refresh_token' : refresh,
    }), http_status_code.HTTP_200_OK