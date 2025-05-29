from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from src.database.database import db, Performance, User
from src.utils.decorators import admin_only, prevent_mod_on_deleted_employee
from src.constants import http_status_code
from flasgger import swag_from

performance = Blueprint("performance", __name__, url_prefix="/api/v1/performance")

@performance.post("/create_performance")
@jwt_required()
@admin_only
@swag_from("../../docs/performance/create_performance.yaml")
def create_performance():
    data = request.form
    employee_id = data.get("employee_id")
    rating = data.get("rating")
    feedback = data.get("feedback")

    try:
        rating = int(rating)
    except (TypeError, ValueError):
        return jsonify({"msg": "Rating must be an integer"}), http_status_code.HTTP_400_BAD_REQUEST

    if not employee_id or rating is None:
        return jsonify({"msg": "Missing required fields"}), http_status_code.HTTP_400_BAD_REQUEST

    performance = Performance(employee_id=employee_id, rating=rating, feedback=feedback)
    db.session.add(performance)
    db.session.commit()

    return jsonify({"msg": "Performance record created"}), http_status_code.HTTP_201_CREATED


@performance.post("/get_list")
@jwt_required()
@swag_from("../../docs/performance/get_list.yaml")
def get_performance_list():
    user_id = get_jwt_identity()
    claims = get_jwt()
    user = User.query.get(user_id)

    data = request.form
    page = int(data.get("page", 1))
    per_page = int(data.get("per_page", 10))
    sort_by = data.get("sort_by", "created_at")
    sort_order = data.get("sort_order", "desc").lower()
    keyword = data.get("keyword", "").strip().lower()

    valid_sort_fields = {
        "created_at": Performance.created_at,
        "rating": Performance.rating,
        "review_date": Performance.review_date,
    }
    sort_column = valid_sort_fields.get(sort_by, Performance.created_at)
    sort_clause = sort_column.asc() if sort_order == "asc" else sort_column.desc()

    if claims.get("role") == "admin":
        query = Performance.query
    else:
        if not user or not user.employee_id:
            return jsonify({"msg": "Unauthorized access"}), http_status_code.HTTP_403_FORBIDDEN
        query = Performance.query.filter_by(employee_id=user.employee_id)

    if keyword:
        query = query.filter(
            db.or_(
                Performance.feedback.ilike(f"%{keyword}%"),
                Performance.employee_id.ilike(f"%{keyword}%")
            )
        )

    paginated = query.order_by(sort_clause).paginate(page=page, per_page=per_page, error_out=False)

    results = []
    for record in paginated.items:
        results.append({
            "id": record.id,
            "employee": {
                "employee_id": record.employee.id if record.employee else None,
                "first_name": record.employee.first_name if record.employee else None,
                "last_name": record.employee.last_name if record.employee else None,
                "position": record.employee.position if record.employee else None,
                "department": record.employee.department.name if record.employee and record.employee.department else None
            },
            "review_date": record.review_date.isoformat(),
            "rating": record.rating,
            "feedback": record.feedback,
            "created_at": record.created_at.isoformat() if record.created_at else None,
            "updated_at": record.updated_at.isoformat() if record.updated_at else None
        })

    return jsonify({
        "items": results,
        "total": paginated.total,
        "page": paginated.page,
        "pages": paginated.pages,
        "has_next": paginated.has_next,
        "has_prev": paginated.has_prev
        
    }), http_status_code.HTTP_200_OK


def get_employee_id_from_performance():
    perforamnce_id = request.form.get("performance_id")
    performance_data = Performance.query.get(perforamnce_id)
    if performance_data:
        return performance_data.employee_id
    return None

@performance.put("/edit_performance")
@jwt_required()
@admin_only
@prevent_mod_on_deleted_employee(get_employee_id_from_performance)
@swag_from("../../docs/performance/edit_performance.yaml")
def update_performance():
    data = request.form
    performance_id = data.get("performance_id")
    record = Performance.query.get(performance_id)

    if not record:
        return jsonify({"msg": "Record not found"}), http_status_code.HTTP_404_NOT_FOUND

    if "rating" in data:
        try:
            record.rating = int(data.get("rating"))
        except ValueError:
            return jsonify({"msg": "Invalid rating"}), http_status_code.HTTP_400_BAD_REQUEST

    if "feedback" in data:
        record.feedback = data.get("feedback")

    db.session.commit()
    return jsonify({"msg": "Performance record updated"}), http_status_code.HTTP_200_OK


@performance.delete("/delete_performance")
@jwt_required()
@admin_only
@prevent_mod_on_deleted_employee(get_employee_id_from_performance)
@swag_from("../../docs/performance/delete_performance.yaml")
def delete_performance():
    data = request.form
    performance_id = data.get("performance_id")
    record = Performance.query.get(performance_id)

    if not record:
        return jsonify({"msg": "Record not found"}), http_status_code.HTTP_404_NOT_FOUND

    db.session.delete(record)
    db.session.commit()
    return jsonify({"msg": "Performance record deleted"}), http_status_code.HTTP_200_OK
