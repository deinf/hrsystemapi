from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt, jwt_required
from src.constants import constants
from flask.json.provider import DefaultJSONProvider
from src.database.database import db, Employee

def admin_only(func):
    @wraps(func)
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt() 
        if claims.get("role") != "admin":
            return jsonify({"Message": "Access denied. Admins only."}), constants.http_status_code.HTTP_403_FORBIDDEN

        return func(*args, **kwargs)

    return wrapper

class CustomJSONProvider(DefaultJSONProvider):
    def dumps(self, obj, **kwargs):
        # Ensure sort_keys is False to prevent sorting of keys
        kwargs['sort_keys'] = False
        return super().dumps(obj, **kwargs)
    
def prevent_mod_on_deleted_employee(get_employee_id_func):
    def decorator(func):
        @wraps(func)
        @jwt_required()
        def wrapper(*args, **kwargs):
            employee_id = get_employee_id_func(*args, **kwargs)
            pass

            employee = Employee.query.get(employee_id)
            if employee and employee.status == 'deleted':
                return jsonify({"message": "Operation not allowed on deleted employee records."}), constants.http_status_code.HTTP_403_FORBIDDEN

            return func(*args, **kwargs)
        return wrapper
    return decorator
        