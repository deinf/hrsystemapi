from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from src.utils.decorators import admin_only, prevent_mod_on_deleted_employee
import validators
from src.constants.constants import http_status_code
from src.database.database import User, Employee, db
from werkzeug.security import generate_password_hash
from sqlalchemy import or_
from flasgger import swag_from

user = Blueprint('user', __name__, url_prefix='/hrsystemapi/api/v1/user')


@user.post('/admin/create_user')
@jwt_required()
@admin_only
@swag_from("../../docs/user/create_user.yaml")
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
@jwt_required()
@admin_only
@swag_from("../../docs/user/admin_edit_user.yaml")
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
@jwt_required()
@swag_from("../../docs/user/self_edit_user.yaml")
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
@swag_from("../../docs/user/delete_user.yaml")
def delete_user():
    try:
        data = request.form
        user_id = data.get("id")
        
        result = User.query.filter_by(id=user_id).first()
        
        if result is None:
            return jsonify({
                "message" : "User not found"
            }), http_status_code.HTTP_404_NOT_FOUND
        
        if result.employee:
            result.employee.status = "deleted"
        
        db.session.delete(result)
        db.session.commit()
        
        return jsonify({
            'message': "User deleted successfully"
        }),http_status_code.HTTP_200_OK
        
    except Exception as e:
        return jsonify({
            'message': 'Unable to process'
        }), http_status_code.HTTP_400_BAD_REQUEST
        
@user.get("/get_user")
@jwt_required()
@swag_from("../../docs/user/get_users.yaml")
def get_all_user():
    role = get_jwt().get("role")  
    user_id = get_jwt_identity() 
    data = request.form
    page = int(data.get("page", 1))  
    per_page = int(data.get("per_page", 10))  
    sort_order = data.get("sort", "desc").lower()
    sort_by = data.get("sort_by", "created_at")
    search_term = data.get("search", "")  

    sort_fields = {
        "username": User.username,
        "email": User.email,
        "created_at": User.created_at,
        "id": User.id
    }
    sort_column = sort_fields.get(sort_by, User.created_at)
    order_by = sort_column.desc() if sort_order == "desc" else sort_column.asc()

    query = (
        db.session.query(User, Employee)
        .outerjoin(Employee, User.employee_id == Employee.id)
    )

    if search_term:
        search_filter = f"%{search_term}%"
        query = query.filter(
            db.or_(
                User.email.ilike(search_filter),
                User.username.ilike(search_filter),
                Employee.first_name.ilike(search_filter),
                Employee.last_name.ilike(search_filter)
            )
        )

    if role == "admin":
        result = query.order_by(order_by).paginate(page=page, per_page=per_page, error_out=False)

        user_data = [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "employee": employee.serialize if employee else []
            }
            for user, employee in result.items
        ]

        return jsonify({
            "users": user_data,
            "total": result.total,
            "page": result.page,
            "pages": result.pages,
            "has_next": result.has_next,
            "has_prev": result.has_prev
        }), http_status_code.HTTP_200_OK

    elif role == "employee":
        result = query.filter(User.id == user_id).first()

        if not result:
            return jsonify({"error": "User not found"}), http_status_code.HTTP_404_NOT_FOUND

        user, employee = result
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "employee": employee.serialize if employee else []
        }

        return jsonify(user_data), http_status_code.HTTP_200_OK

    return jsonify({"error": "Unauthorized access"}), http_status_code.HTTP_403_FORBIDDEN
