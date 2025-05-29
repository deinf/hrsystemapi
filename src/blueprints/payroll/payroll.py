from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from src.utils.decorators import admin_only, prevent_mod_on_deleted_employee
from src.constants.constants import http_status_code
from src.database.database import Payroll, Employee, Department, User, db
from datetime import datetime
from flasgger import swag_from


payroll = Blueprint('payroll', __name__, url_prefix='/api/v1/payroll')

@payroll.post("/add_payroll")
@jwt_required()
@admin_only
@swag_from("../../docs/payroll/add_payroll.yaml")
def add_payroll():
    
    data = request.form 
    employee_id = data.get("employee_id")
    base_salary = data.get("base_salary")
    bonus = data.get("bonus")
    deductions = data.get("deductions")
    net_salary = data.get("net_salary")
    pay_date = data.get("pay_date")
    
    print(employee_id)
    if not employee_id:
        return jsonify({
            "message" : "Missing required fields"
        }), http_status_code.HTTP_400_BAD_REQUEST
        
    datetime_object = datetime.strptime(pay_date, '%Y-%m-%d')
    
    
    payroll_data = Payroll(employee_id=employee_id, base_salary=base_salary, bonus=bonus, deductions=deductions, net_salary=net_salary, pay_date=datetime_object)
    
    
    db.session.add(payroll_data)
    db.session.commit()
    
    return jsonify({
        "message" : "Data Created",
        "data" : {
            "id" : payroll_data.id,
            "employee_id" : payroll_data.employee_id,
            "base_salary" : payroll_data.base_salary,
            "bonus" : payroll_data.bonus,
            "deductions" : payroll_data.deductions,
            "net_salary" : payroll_data.net_salary,
            "pay_date" : payroll_data.pay_date
        }
    })
    
def get_employee_id_from_payroll():
    payroll_id = request.form.get("payroll_id")
    if not payroll_id:
        return None
    payroll = Payroll.query.filter_by(id=payroll_id).first()
    return payroll.employee_id if payroll else None
    
@payroll.delete("/delete_payroll")
@jwt_required()
@admin_only
@prevent_mod_on_deleted_employee(get_employee_id_from_payroll)
@swag_from("../../docs/payroll/delete_payroll.yaml")
def delete_payroll():
    
    data = request.form
    id_payroll = data.get("payroll_id")
    
    payroll_data = Payroll.query.filter_by(id=id_payroll).first()
    
    if payroll_data is None:
        return jsonify({
            "message" : "Payroll data is not found"
        }), http_status_code.HTTP_404_NOT_FOUND
        
    db.session.delete(payroll_data)
    db.session.commit()
    
    return jsonify({
        "message" : "Data deleted"
    }), http_status_code.HTTP_200_OK
    
    
@payroll.post("/get_payroll")
@jwt_required()
@swag_from("../../docs/payroll/get_payroll.yaml")
def get_all_payroll():
    role = get_jwt().get("role")  
    user_id = get_jwt_identity()  
    data = request.form
    page = int(data.get("page", 1))
    per_page = int(data.get("per_page", 10)) 
    sort_order = data.get("sort", "desc").lower()
    sort_by = data.get("sort_by", "pay_date")
    keyword = data.get("keyword", "")  

    sort_fields = {
        "pay_date": Payroll.pay_date,
        "base_salary": Payroll.base_salary,
        "bonus": Payroll.bonus,
        "deductions": Payroll.deductions,
        "net_salary": Payroll.net_salary,
        "created_at": Payroll.created_at,
        "department": Department.name,
        "position": Employee.position,
    }

    sort_column = sort_fields.get(sort_by, Payroll.pay_date)
    order_by = sort_column.desc() if sort_order == "desc" else sort_column.asc()

    query = db.session.query(Payroll, Employee, Department) \
        .join(Employee, Payroll.employee_id == Employee.id) \
        .outerjoin(Department, Employee.department_id == Department.id)

    if keyword:
        keyword_filter = f"%{keyword}%"
        query = query.filter(
            db.or_(
                Employee.first_name.ilike(keyword_filter),
                Employee.last_name.ilike(keyword_filter),
                Employee.position.ilike(keyword_filter),
                Department.name.ilike(keyword_filter)
            )
        )

    if role == "employee":
        user = User.query.filter_by(id=user_id).first()
        if user and user.employee:
            query = query.filter(Payroll.employee_id == user.employee.id)

    result = query.order_by(order_by).paginate(page=page, per_page=per_page, error_out=False)

    payroll_data = [
        {
            "payroll_id": payroll.id,
            "employee": {
                "employee_id": employee.id,
                "first_name": employee.first_name,
                "last_name": employee.last_name,
                "position": employee.position,
                "department": department.name if department else None
            },
            "base_salary": payroll.base_salary,
            "bonus": payroll.bonus,
            "deductions": payroll.deductions,
            "net_salary": payroll.net_salary,
            "pay_date": payroll.pay_date.isoformat() if payroll.pay_date else None,
            "created_at": payroll.created_at.isoformat() if payroll.created_at else None
        }
        for payroll, employee, department in result.items
    ]

    return jsonify({
        "payrolls": payroll_data,
        "total": result.total,
        "page": result.page,
        "pages": result.pages,
        "has_next": result.has_next,
        "has_prev": result.has_prev
    }), http_status_code.HTTP_200_OK



