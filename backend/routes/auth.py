import hashlib
import time
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.db import students_collection

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()

def is_admin():
    """Helper to check if the current user is an admin."""
    # Assuming student_id is the identity
    student_id = get_jwt_identity()
    user = students_collection.find_one({"student_id": student_id})
    return user and user.get('role') == 'admin'

@auth_bp.route('/register', methods=['POST'])
@jwt_required()
def register():
    # Admin only check (PRD 5.1)
    if not is_admin():
        return jsonify({"error": "Unauthorized. Admin access required."}), 403
    
    data = request.json
    return _create_user(data)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    # Public self-registration
    data = request.json
    data['role'] = 'student' # Force role to student for public signup
    return _create_user(data)

def _create_user(data):
    student_id = data.get('student_id')
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    role = data.get('role', 'student')

    if not all([student_id, email, password, name]):
        return jsonify({"error": "Missing required fields"}), 400

    if students_collection.find_one({"$or": [{"student_id": student_id}, {"email": email}]}):
        return jsonify({"error": "Student ID or email already exists"}), 409

    hashed_password = bcrypt.generate_password_hash(password, 12).decode('utf-8')
    
    student_data = {
        "student_id": student_id,
        "email": email,
        "password": hashed_password,
        "name": name,
        "role": role,
        "points": 0,
        "total_disposals": 0,
        "correct_disposals": 0,
        "streak_days": 0,
        "last_correct_date": None,
        "is_active": True,
        "created_at": datetime.utcnow()
    }
    
    students_collection.insert_one(student_data)
    return jsonify({"message": "Account created", "student_id": student_id}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    student_id = data.get('student_id')
    password = data.get('password')

    if not student_id or not password:
        return jsonify({"error": "Invalid student ID or password"}), 401

    # PRD 5.1: find one where student_id matches AND is_active = true
    user = students_collection.find_one({"student_id": student_id, "is_active": True})
    
    if user and bcrypt.check_password_hash(user['password'], password):
        # Generate JWT: payload = { student_id, role, name, exp: now + 24 hours }
        # PRD 5.1: Include additional claims
        additional_claims = {"role": user.get('role', 'student'), "name": user.get('name')}
        access_token = create_access_token(identity=student_id, additional_claims=additional_claims)
        return jsonify({
            "token": access_token,
            "role": user.get('role', 'student'),
            "name": user.get('name')
        }), 200

    # PRD 5.1: generic error (do not reveal whether the ID or password was wrong)
    return jsonify({"error": "Invalid student ID or password"}), 401
