from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.utils.decorators import admin_only
import validators
from src.constants.constants import http_status_code
from src.database.database import User, Employee, db
from werkzeug.security import generate_password_hash
from sqlalchemy import or_


user = Blueprint('user', __name__, url_prefix='/api/v1/user')


@user.post('admin/create_user')
@jwt_required()
@admin_only
def create_user():
    data = request.form
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    phone = data.get('phone')
    hire_date = data.get('hire_date')
    position = data.get('position')
    salary = data.get('salary')
    status = data.get('status')
    department_id= data.get('department_id')
    role = data.get('role')
    
    if not username or not email or not password or not first_name:
        return jsonify({
            'message' : 'Missing required fields',
        }), http_status_code.HTTP_400_BAD_REQUEST
    
    if len(password) < 6:
        return jsonify({
            'message' : 'Password must be at least 6 characters'
        }), http_status_code.HTTP_400_BAD_REQUEST
        
    if len(username) < 3:
        return jsonify({
            'message' : 'Username must be at least 3 characters'
        }), http_status_code.HTTP_400_BAD_REQUEST
    
    if not username.isalnum() or " " in username:
        return jsonify({
            'message': 'Username should be a valid alpha numeric and no spaces'
        }), http_status_code.HTTP_400_BAD_REQUEST
        
    if not validators.email(email):
        return jsonify({
            'message': 'Your email address is invalid'
        }), http_status_code.HTTP_400_BAD_REQUEST
        
    if User.query.filter_by(email=email).first() is not None:
        return jsonify({
            'message': 'Email address is already in use'
        }), http_status_code.HTTP_409_CONFLICT
        
    if User.query.filter_by(username=username).first() is not None:
        return jsonify({
            'message': 'Username is already in use'
        }), http_status_code.HTTP_409_CONFLICT
        
        
    employee = Employee(
        first_name = first_name,
        last_name = last_name,
        email = email,
        phone = phone,
        position = position,
        salary = salary,
        status = status,
        hire_date =hire_date,
        department_id = department_id
    )
    
    db.session.add(employee)
    db.session.commit()
    
    user = User(
        username=username,
        password_hash=generate_password_hash(password), 
        employee_id = employee.id,
        email=email,
        role=role)
    db.session.add(user)
    db.session.commit()
    
    # employee_data = Employee.query.filter(or_(User.email==email, User.username==username)).first()
    employee_data = Employee.query.join(User, Employee.id == User.employee_id).filter(or_(User.email==email, User.username==username)).first()
    return jsonify({
        "message": "Employee and User account created successfully!",
        "data": employee_data.serialize
    }), http_status_code.HTTP_201_CREATED
    
    
@user.put('/admin/edit_user')
@user.patch('/admin/edit_user')
@jwt_required()
@admin_only
def edit_user_admin():
    try:
        data = request.form
        user_id = data.get('id')
        
        result = (   
                db.session.query(User, Employee)
                .outerjoin(Employee, User.employee_id == Employee.id) 
                .filter(User.id == user_id)
                .first()
        )  
        
        if result is None:
            return jsonify({
                "message" : "User not found"
            }), http_status_code.HTTP_404_NOT_FOUND
            
            
        user_data, employe_data = result
        if employe_data is None:
            return jsonify({
                "message" : "This user does not have Employee data"
            }), http_status_code.HTTP_404_NOT_FOUND
        
        
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        phone = data.get('phone')
        hire_date = data.get('hire_date')
        position = data.get('position')
        salary = data.get('salary')
        status= data.get('status')
        department_id= data.get('department_id')
        role= data.get('role')
        
        user_data.role = role
        employe_data.first_name = first_name
        employe_data.last_name = last_name
        employe_data.phone = phone
        employe_data.hire_date = employe_data.hire_date if hire_date == "" or hire_date is None else hire_date
        employe_data.position = position
        employe_data.salary = salary
        employe_data.status = status
        employe_data.department_id = department_id
        
        db.session.commit()
        
        return jsonify({
            "message" : "updated",
            "data" : {
                "user_id" : user_id,
                "role" : role,
                "first_name" : first_name,
                "last_name" : last_name,
                "phone" : phone,
                "hire_date" : hire_date,
                "position" : position,
                "salary" : salary,
                "status" : status,
                "department_id" : department_id,
                "created_at" : employe_data.created_at,
                "updated_at" : employe_data.updated_at
            }
        
        }), http_status_code.HTTP_201_CREATED
        
    except Exception as e:
        print(e)
        return jsonify({
            'message': 'Unable to process'
        }), http_status_code.HTTP_400_BAD_REQUEST
        
       
@user.put('/edit_user')
@user.patch('/edit_user')
@jwt_required()
def edit_user():
    try:
        data = request.form
        user_id = get_jwt_identity()
        
        result = (   
                db.session.query(User, Employee)
                .outerjoin(Employee, User.employee_id == Employee.id) 
                .filter(User.id == user_id)
                .first()
        )  
        
        if result is None:
            return jsonify({
                "message" : "User not found"
            }), http_status_code.HTTP_404_NOT_FOUND
            
            
        user_data, employe_data = result
        if employe_data is None:
            return jsonify({
                "message" : "This user does not have Employee data"
            }), http_status_code.HTTP_404_NOT_FOUND
        
        
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        phone = data.get('phone')
        
        
        
        employe_data.first_name = first_name
        employe_data.last_name = last_name
        employe_data.phone = phone
        
        db.session.commit()
        
        return jsonify({
            "message" : "updated",
            "data" : {
                "user_id" : user_id,
                "role" : user_data.role,
                "first_name" : first_name,
                "last_name" : last_name,
                "phone" : phone,
                "hire_date" : employe_data.hire_date,
                "position" : employe_data.position,
                "salary" : employe_data.salary,
                "status" : employe_data.status,
                "department_id" : employe_data.department_id,
                "created_at" : employe_data.created_at,
                "updated_at" : employe_data.updated_at
            }
        
        }), http_status_code.HTTP_201_CREATED
        
    except Exception as e:
        return jsonify({
            'message': 'Unable to process'
        }), http_status_code.HTTP_400_BAD_REQUEST
        
    
@user.delete("/admin/delete_user")
@jwt_required()
@admin_only
def delete_user():
    try:
        data = request.form
        user_id = data.get("id")
        
        result = User.query.filter_by(id=user_id).first()
        
        if result is None:
            return jsonify({
                "message" : "User not found"
            }), http_status_code.HTTP_404_NOT_FOUND
        
        db.session.delete(result)
        db.session.commit()
        
        return jsonify({
            'message': "User and associated employee deleted successfully"
        }),http_status_code.HTTP_200_OK
        
    except Exception as e:
        return jsonify({
            'message': 'Unable to process'
        }), http_status_code.HTTP_400_BAD_REQUEST
        
# @user.get("/admin/get_all_user")
# @jwt_required()
# @admin_only
# def get_all_user():
    
    
        
        
    
    
    