from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from src.utils.decorators import admin_only, prevent_mod_on_deleted_employee
from src.constants.constants import http_status_code
from src.database.database import User, db, Attendance, Employee
from datetime import datetime, date
from flasgger import swag_from


attendance = Blueprint('attendance', __name__, url_prefix='/api/v1/attendance')

@attendance.post("/checkin")
@jwt_required()
@swag_from("../../docs/attendance/checkin.yaml")
def checkin():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user or not user.employee_id:
        return jsonify({"msg": "Only employees can check in"}), http_status_code.HTTP_403_FORBIDDEN

    today = date.today()
    
    existing = Attendance.query.filter_by(employee_id=user.employee_id, date=today).first()
    if existing:
        return jsonify({"msg": "Already checked in today"}), http_status_code.HTTP_400_BAD_REQUEST

    new_attendance = Attendance(
        employee_id=user.employee_id,
        check_in_time=datetime.now().time(),
        check_out_time=None,
        status="present"
    )
    new_attendance.date = today
    db.session.add(new_attendance)
    db.session.commit()

    return jsonify({"msg": "Checked in successfully"}), http_status_code.HTTP_201_CREATED


@attendance.post("/checkout")
@jwt_required()
@swag_from("../../docs/attendance/checkout.yaml")
def checkout():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user or not user.employee_id:
        return jsonify({"msg": "Only employees can check out"}), http_status_code.HTTP_403_FORBIDDEN

    today = date.today()
    record = Attendance.query.filter_by(employee_id=user.employee_id, date=today).first()

    if not record:
        return jsonify({"msg": "You haven't checked in today"}), http_status_code.HTTP_400_BAD_REQUEST

    if record.check_out_time:
        return jsonify({"msg": "Already checked out today"}), http_status_code.HTTP_400_BAD_REQUEST

    record.check_out_time = datetime.now().time()
    db.session.commit()

    return jsonify({"msg": "Checked out successfully"}), http_status_code.HTTP_200_OK

@attendance.post("/get_attendances")
@jwt_required()
@swag_from("../../docs/attendance/get_attendances.yaml")
def get_attendance():
    role = get_jwt().get("role")
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"msg": "User not found"}), http_status_code.HTTP_403_FORBIDDEN

    data = request.form
    page = int(data.get("page", 1))
    per_page = int(data.get("per_page", 10))
    sort_order = data.get("sort", "desc").lower()
    sort_by = data.get("sort_by", "date")
    keyword = data.get("keyword", "")

    sort_fields = {
        "date": Attendance.date,
        "check_in_time": Attendance.check_in_time,
        "check_out_time": Attendance.check_out_time,
        "status": Attendance.status
    }

    order_column = sort_fields.get(sort_by, Attendance.date)
    order_by = order_column.desc() if sort_order == "desc" else order_column.asc()

    query = db.session.query(Attendance).join(Employee, Attendance.employee_id == Employee.id)

    if keyword:
        keyword_filter = f"%{keyword}%"
        query = query.filter(
            db.or_(
                Employee.first_name.ilike(keyword_filter),
                Employee.last_name.ilike(keyword_filter)
            )
        )

    if role == "employee":
        if not user.employee_id:
            return jsonify({"msg": "Invalid employee"}), http_status_code.HTTP_403_FORBIDDEN
        query = query.filter(Attendance.employee_id == user.employee_id)

    pagination = query.order_by(order_by).paginate(page=page, per_page=per_page, error_out=False)

    records = pagination.items
    result = []
    for att in records:
        result.append({
            "id": att.id,
            "employee": {
                "employee_id": att.employee.id if att.employee else None,
                "first_name": att.employee.first_name if att.employee else None,
                "last_name": att.employee.last_name if att.employee else None,
                "position": att.employee.position if att.employee else None,
                "department": att.employee.department.name if att.employee and att.employee.department else None
            },
            "date": att.date.isoformat(),
            "check_in_time": att.check_in_time.isoformat() if att.check_in_time else None,
            "check_out_time": att.check_out_time.isoformat() if att.check_out_time else None,
            "status": att.status
        })

    return jsonify({
        "data": result,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total_records": pagination.total,
        "total_pages": pagination.pages,
        "has_next": pagination.has_next,
        "has_prev": pagination.has_prev
    }), http_status_code.HTTP_200_OK



def get_employee_id_from_attendance():
    attendance_id = request.form.get("id")
    attendance = Attendance.query.get(attendance_id)
    if attendance:
        return attendance.employee_id
    return None

@attendance.delete("/delete_attendance")
@admin_only
@jwt_required()
@prevent_mod_on_deleted_employee(get_employee_id_from_attendance)
@swag_from("../../docs/attendance/delete_attendance.yaml")
def delete_attendance():
    attendance_id = request.form.get("id")
    record = Attendance.query.get(attendance_id)
    
    if not record:
        return jsonify({"msg": "Attendance not found"}), http_status_code.HTTP_404_NOT_FOUND
    
    db.session.delete(record)
    db.session.commit()
    
    return jsonify({"msg": "Attendance deleted successfully"}), http_status_code.HTTP_200_OK
    
    