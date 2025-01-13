from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.utils.decorators import admin_only
from src.constants.constants import http_status_code
from src.database.database import Department, db


department = Blueprint('department', __name__, url_prefix='/api/v1/department')


# @department.post()