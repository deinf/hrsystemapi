from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from src.database.database import db, Leave, User, Employee
from src.constants.constants import http_status_code
from datetime import datetime
from src.utils.decorators import admin_only, prevent_mod_on_deleted_employee
from flasgger import swag_from


leave = Blueprint("leave", __name__, url_prefix="/api/v1/leave")

@leave.post("/apply")
@jwt_required()
@swag_from("../../docs/leave/apply_leave.yaml")
def apply_leave():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user or not user.employee_id:
        return jsonify({"msg": "Only employees can apply for leave"}), http_status_code.HTTP_403_FORBIDDEN

    data = request.form
    leave_type = data.get("leave_type")
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    reason = data.get("reason")

    try:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    except Exception:
        return jsonify({"msg": "Invalid date format. Use YYYY-MM-DD."}), http_status_code.HTTP_400_BAD_REQUEST

    new_leave = Leave(
        employee_id=user.employee_id,
        leave_type=leave_type,
        start_date=start_date,
        end_date=end_date,
        reason=reason
    )

    db.session.add(new_leave)
    db.session.commit()

    return jsonify({"msg": "Leave request submitted"}), http_status_code.HTTP_201_CREATED

@leave.post("/list")
@jwt_required()
@swag_from("../../docs/leave/list_leaves.yaml")
def get_leaves():
    role = get_jwt().get("role")
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    data = request.form
    page = int(data.get("page", 1))
    per_page = int(data.get("per_page", 10))
    sort_order = data.get("sort", "desc").lower()
    sort_by = data.get("sort_by", "start_date")
    keyword = data.get("keyword", "")
    
    sort_fields = {
        "start_date": Leave.start_date,
        "end_date": Leave.end_date,
        "status": Leave.status,
        "leave_type": Leave.leave_type
    }
    order_column = sort_fields.get(sort_by, Leave.start_date)
    order_by = order_column.desc() if sort_order == "desc" else order_column.asc()
    query = db.session.query(Leave).join(Employee, Leave.employee_id == Employee.id)

    if keyword:
        keyword_filter = f"%{keyword}%"
        query = query.filter(
            db.or_(
                Employee.first_name.ilike(keyword_filter),
                Employee.last_name.ilike(keyword_filter)
            )
        )

    if role == "employee":
        if not user or not user.employee_id:
            return jsonify({"msg": "Invalid user"}), http_status_code.HTTP_403_FORBIDDEN
        query = query.filter(Leave.employee_id == user.employee_id)

    leaves = query.order_by(order_by).paginate(page=page, per_page=per_page, error_out=False)

    results = []
    for leave in leaves.items:
        results.append({
            "id": leave.id,
            "employee": {
                "employee_id": leave.employee.id if leave.employee else None,
                "first_name": leave.employee.first_name if leave.employee else None,
                "last_name": leave.employee.last_name if leave.employee else None,
                "position": leave.employee.position if leave.employee else None,
                "department": leave.employee.department.name if leave.employee and leave.employee.department else None
            },
            "leave_type": leave.leave_type,
            "start_date": leave.start_date.isoformat(),
            "end_date": leave.end_date.isoformat(),
            "status": leave.status,
            "reason": leave.reason,
            "reviewed_by": leave.reviewer.username if leave.reviewer else None
        })

    return jsonify({
        "data": results,
        "total": leaves.total,
        "page": leaves.page,
        "pages": leaves.pages,
        "has_next": leaves.has_next,
        "has_prev": leaves.has_prev
    }), http_status_code.HTTP_200_OK

def get_employee_id_from_leave():
    leave_id = request.form.get("leave_id")
    leave = Leave.query.get(leave_id)
    if leave:
        return leave.employee_id
    return None

@leave.put("/status")
@jwt_required()
@admin_only
@prevent_mod_on_deleted_employee(get_employee_id_from_leave)
@swag_from("../../docs/leave/update_leave_status.yaml")
def update_leave_status():
    data = request.form
    leave_id = data.get("leave_id")
    new_status = data.get("status")
    admin_user_id = get_jwt_identity()

    leave = Leave.query.get(leave_id)
    if not leave:
        return jsonify({"msg": "Leave request not found"}), http_status_code.HTTP_404_NOT_FOUND

    if new_status not in ["approved", "rejected"]:
        return jsonify({"msg": "Status must be 'approved' or 'rejected'"}), http_status_code.HTTP_400_BAD_REQUEST

    leave.status = new_status
    leave.reviewed_by = admin_user_id
    db.session.commit()

    return jsonify({
        "msg": f"Leave status updated to {new_status}", 
    }), http_status_code.HTTP_200_OK

@leave.delete("/delete")
@jwt_required()
@admin_only
@prevent_mod_on_deleted_employee(get_employee_id_from_leave)
@swag_from("../../docs/leave/delete_leave.yaml")
def delete_leave():
    data = request.form
    leave_id = data.get("leave_id")

    leave = Leave.query.get(leave_id)
    if not leave:
        return jsonify({"msg": "Leave record not found"}), http_status_code.HTTP_404_NOT_FOUND

    db.session.delete(leave)
    db.session.commit()

    return jsonify({"msg": "Leave record deleted successfully"}), http_status_code.HTTP_200_OK
