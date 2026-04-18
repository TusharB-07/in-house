import os
import random
import string
from flask import Blueprint, request, jsonify
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.db import bins_collection, disposals_collection, bin_sessions_collection

bins_bp = Blueprint('bins', __name__)

DEVICE_SECRET = os.getenv("DEVICE_SECRET", "iot-device-key-abc")

def generate_bin_code():
    return ''.join(random.choices(string.digits, k=6))

@bins_bp.route('/update', methods=['POST'])
def update_bin():
    # Validate X-Device-Key header (PRD 5.2)
    device_key = request.headers.get('X-Device-Key')
    if device_key != DEVICE_SECRET:
        return jsonify({"error": "Unauthorized device"}), 401

    data = request.json
    bin_id = data.get('bin_id')
    fill_level = data.get('fill_level')
    is_active = data.get('is_active', True)

    if not bin_id:
        return jsonify({"error": "bin_id is required"}), 400

    # Validate fill_level (PRD 5.2: 0-100)
    if fill_level is not None:
        try:
            fill_level = int(fill_level)
            if not (0 <= fill_level <= 100):
                return jsonify({"error": "fill_level must be between 0 and 100"}), 400
        except ValueError:
            return jsonify({"error": "fill_level must be an integer"}), 400

    update_data = {
        "last_updated": datetime.utcnow(),
        "is_active": is_active
    }
    
    if fill_level is not None:
        update_data["fill_level"] = fill_level
        update_data["is_full"] = fill_level >= 90

    bins_collection.update_one(
        {"bin_id": bin_id},
        {"$set": update_data},
        upsert=True
    )

    return jsonify({"message": "Updated"}), 200

@bins_bp.route('/all', methods=['GET'])
def get_all_bins():
    # PRD 5.2: sorted by fill_level descending
    bins = list(bins_collection.find({"is_active": True}, {'_id': 0}).sort("fill_level", -1))
    
    # Check for active sessions for each bin
    active_sessions = bin_sessions_collection.distinct("bin_id", {"status": "active"})
    
    for bin_doc in bins:
        bin_doc['has_active_session'] = bin_doc['bin_id'] in active_sessions
    
    return jsonify(bins), 200

@bins_bp.route('/<bin_id>', methods=['GET'])
def get_bin_detail(bin_id):
    # PRD 5.2: returns { bin: object, recent_disposals: array (last 20) }
    bin_doc = bins_collection.find_one({"bin_id": bin_id}, {'_id': 0})
    if not bin_doc:
        return jsonify({"error": "Bin not found"}), 404
    
    recent_disposals = list(disposals_collection.find({"bin_id": bin_id}, {'_id': 0})
                            .sort("timestamp", -1)
                            .limit(20))
    
    return jsonify({
        "bin": bin_doc,
        "recent_disposals": recent_disposals
    }), 200

# --- ADMIN ENDPOINTS (PRD 5.2) ---

@bins_bp.route('/register', methods=['POST'])
@jwt_required()
def register_bin():
    # Admin only check
    # We should use the is_admin helper if we move it to a shared place, 
    # but for now let's just do a quick check
    student_id = get_jwt_identity()
    from models.db import students_collection
    admin_user = students_collection.find_one({"student_id": student_id, "role": "admin"})
    if not admin_user:
        return jsonify({"error": "Unauthorized. Admin access required."}), 403

    data = request.json
    location = data.get('location')

    if not location:
        return jsonify({"error": "location is required"}), 400

    # Robust bin_id generation (incrementing)
    last_bin = bins_collection.find_one({"bin_id": {"$regex": "^BIN-"}}, sort=[("bin_id", -1)])
    if last_bin:
        try:
            last_num = int(last_bin['bin_id'].split("-")[1])
            new_id = f"BIN-{(last_num + 1):03d}"
        except (ValueError, IndexError):
            new_id = f"BIN-{random.randint(100, 999)}"
    else:
        new_id = "BIN-001"

    # Unique bin_code generation (PRD 5.2)
    def get_unique_code():
        for _ in range(10): # try 10 times
            code = ''.join(random.choices(string.digits, k=6))
            if not bins_collection.find_one({"bin_code": code}):
                return code
        return ''.join(random.choices(string.digits, k=6))

    new_bin = {
        "bin_id": new_id,
        "bin_code": get_unique_code(),
        "location": location,
        "fill_level": 0,
        "is_active": True,
        "is_full": False,
        "last_updated": datetime.utcnow(),
        "total_disposals": 0,
        "latitude": data.get('latitude'),
        "longitude": data.get('longitude')
    }
    
    bins_collection.insert_one(new_bin)
    return jsonify({
        "bin_id": new_id, 
        "bin_code": new_bin['bin_code'],
        "location": location
    }), 201

@bins_bp.route('/regenerate_code', methods=['POST'])
@jwt_required()
def regenerate_code():
    data = request.json
    bin_id = data.get('bin_id')

    if not bin_id:
        return jsonify({"error": "bin_id is required"}), 400

    new_code = generate_bin_code()
    result = bins_collection.update_one(
        {"bin_id": bin_id},
        {"$set": {"bin_code": new_code}}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Bin not found"}), 404

    return jsonify({"message": "Code regenerated", "bin_code": new_code}), 200
