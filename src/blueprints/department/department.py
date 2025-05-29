from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from src.utils.decorators import admin_only
from src.constants.constants import http_status_code
from src.database.database import Department, db
from flasgger import swag_from

department = Blueprint('department', __name__, url_prefix='/api/v1/department')


@department.post("/add_department")
@jwt_required()
@admin_only
@swag_from("../../docs/department/add_department.yaml")
def add_department():
    
    data = request.form
    
    nama = data.get("nama_department")
    location = data.get("lokasi")
    
    
    if not nama:
        return jsonify({
            'message' : 'Missing department name fields',
        }), http_status_code.HTTP_400_BAD_REQUEST
        
    department_data = Department(name=nama, location=location)
    
    db.session.add(department_data)
    db.session.commit()
    
    return jsonify({
            'message' : 'Departement data created',
        }), http_status_code.HTTP_201_CREATED
    
    
@department.delete("/delete_department")
@jwt_required()
@admin_only
@swag_from("../../docs/department/delete_department.yaml")
def delete_department():
    
    data = request.form
    id_dep = data.get("id")
    
    result = Department.query.filter_by(id=id_dep).first()
        
    if result is None:
        return jsonify({
            "message" : "Departement not found"
        }), http_status_code.HTTP_404_NOT_FOUND
    
    db.session.delete(result)
    db.session.commit()
    
    return jsonify({
        "message" : "Data Deleted"
    }), http_status_code.HTTP_200_OK
    
    
@department.put("/edit_department")
@jwt_required()
@admin_only
@swag_from("../../docs/department/edit_department.yaml")
def edit_department():
    
    data = request.form
    dep_id = data.get("id")
    nama_dep = data.get("nama_department")
    lokasi = data.get("lokasi")
    
    department_data = Department.query.filter_by(id=dep_id).first()
    
    if department_data is None:
        return jsonify({
            "message" : f"Department with id {dep_id} is not found"
        }), http_status_code.HTTP_404_NOT_FOUND
        
    department_data.name = nama_dep
    department_data.location = lokasi
    
    db.session.commit()
    
    return jsonify({
        "message" : "Data Updated",
        "data" : {
            "id" : department_data.id,
            "nama": department_data.name,
            "lokasi" : department_data.location
        }
    }), http_status_code.HTTP_200_OK
    

@department.post("/get_departments")
@admin_only
@jwt_required()
@swag_from("../../docs/department/get_departments.yaml")
def get_departments():

    data = request.form
    page = int(data.get("page", 1))
    per_page = int(data.get("per_page", 10))
    sort_order = data.get("sort", "asc")

    if sort_order == "desc":
        order_by = Department.name.desc()
    else:
        order_by = Department.name.asc()

    query = Department.query.order_by(order_by)
    result = query.paginate(page=page, per_page=per_page, error_out=False)

    departments_data = [
        {
            "id": d.id,
            "name": d.name,
            "location": d.location,
            "created_at": d.created_at.isoformat() if d.created_at else None,
            "updated_at": d.updated_at.isoformat() if d.updated_at else None
        }
        for d in result.items
    ]

    return jsonify({
        "departments": departments_data if departments_data else [],
        "total": result.total,
        "page": result.page,
        "pages": result.pages,
        "has_next": result.has_next,
        "has_prev": result.has_prev
    }), http_status_code.HTTP_200_OK

    
    