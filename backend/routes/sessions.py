import os
import uuid
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.db import bins_collection, bin_sessions_collection, disposals_collection

sessions_bp = Blueprint('sessions', __name__)

@sessions_bp.route('/start', methods=['POST'])
@jwt_required()
def start_session():
    student_id = get_jwt_identity()
    data = request.json
    bin_code = data.get('bin_code')

    if not bin_code:
        return jsonify({"error": "Bin code is required"}), 400

    # 1. Find bin by code
    bin_doc = bins_collection.find_one({"bin_code": bin_code})
    if not bin_doc:
        return jsonify({"error": "Invalid bin code. Please check the number on the bin."}), 404
    
    if not bin_doc.get('is_active', True):
        return jsonify({"error": "This bin is currently offline."}), 400

    bin_id = bin_doc['bin_id']

    # 2. Check if student already has an active session
    active_student_session = bin_sessions_collection.find_one({
        "student_id": student_id,
        "status": "active"
    })
    if active_student_session:
        return jsonify({"error": "You already have an active session. Please wait for it to end or disconnect manually."}), 409

    # 3. Check if bin already has an active session (Critical Edge Case)
    active_bin_session = bin_sessions_collection.find_one({
        "bin_id": bin_id,
        "status": "active"
    })
    if active_bin_session:
        return jsonify({"error": "This bin is currently in use by another student."}), 409

    # 4. Create new session
    # PRD 5.3: Generate session_id = str(uuid.uuid4())[:10]
    session_id = str(uuid.uuid4())[:10]
    new_session = {
        "session_id": session_id,
        "student_id": student_id,
        "bin_id": bin_id,
        "bin_code": bin_code,
        "status": "active",
        "started_at": datetime.utcnow(),
        "last_activity": datetime.utcnow(),
        "ended_at": None,
        "items_thrown": 0,
        "points_earned": 0
    }
    
    bin_sessions_collection.insert_one(new_session)

    return jsonify({
        "session_id": session_id,
        "bin_id": bin_id,
        "location": bin_doc.get('location', 'Unknown'),
        "message": "Connected"
    }), 201

@sessions_bp.route('/active/<student_id>', methods=['GET'])
@jwt_required()
def get_active_session(student_id):
    current_user = get_jwt_identity()
    if current_user != student_id:
        return jsonify({"error": "Unauthorized"}), 403

    session = bin_sessions_collection.find_one({
        "student_id": student_id,
        "status": "active"
    }, {'_id': 0})

    if not session:
        return jsonify({"status": "none"}), 200

    # Check for 30s inactivity expiry (PRD 4.3)
    now = datetime.utcnow()
    last_activity = session['last_activity']
    seconds_inactive = int((now - last_activity).total_seconds())

    # Default timeout 30s (can be env var)
    timeout = int(os.getenv("SESSION_TIMEOUT_SECONDS", 30))

    if seconds_inactive >= timeout:
        # Expire session (PRD 4.3)
        bin_sessions_collection.update_one(
            {"session_id": session['session_id']},
            {"$set": {
                "status": "expired",
                "ended_at": now
            }}
        )
        # PRD 5.3: Return { status: 'expired', summary: { items_thrown, points_earned, duration_seconds } }
        return jsonify({
            "status": "expired",
            "summary": {
                "items_thrown": session['items_thrown'],
                "points_earned": session['points_earned'],
                "duration_seconds": int((now - session['started_at']).total_seconds())
            }
        }), 200

    # Return active state (PRD 5.3)
    return jsonify({
        "status": "active",
        "session_id": session['session_id'],
        "bin_id": session['bin_id'],
        "location": bins_collection.find_one({"bin_id": session['bin_id']}).get('location', 'Unknown'),
        "items_thrown": session['items_thrown'],
        "points_earned": session['points_earned'],
        "seconds_inactive": seconds_inactive
    }), 200

@sessions_bp.route('/end', methods=['POST'])
@jwt_required()
def end_session():
    student_id = get_jwt_identity()
    data = request.json
    session_id = data.get('session_id')

    session = bin_sessions_collection.find_one({"session_id": session_id})
    if not session:
        return jsonify({"error": "Session not found"}), 404
    
    if session['student_id'] != student_id:
        return jsonify({"error": "Unauthorized"}), 403

    if session['status'] != 'active':
        return jsonify({"error": "Session already ended"}), 400

    now = datetime.utcnow()
    bin_sessions_collection.update_one(
        {"session_id": session_id},
        {"$set": {
            "status": "manually_ended",
            "ended_at": now
        }}
    )

    return jsonify({
        "summary": {
            "items_thrown": session['items_thrown'],
            "points_earned": session['points_earned'],
            "duration_seconds": int((now - session['started_at']).total_seconds())
        }
    }), 200

# --- ADMIN ENDPOINTS (PRD 5.6) ---

@sessions_bp.route('/all', methods=['GET'])
@jwt_required()
def get_all_sessions():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 50))
    status = request.args.get('status')

    query = {}
    if status:
        query['status'] = status

    total = bin_sessions_collection.count_documents(query)
    
    # Use aggregation to join student name and bin location
    pipeline = [
        {"$match": query},
        {"$sort": {"started_at": -1}},
        {"$skip": (page - 1) * limit},
        {"$limit": limit},
        {
            "$lookup": {
                "from": "students",
                "localField": "student_id",
                "foreignField": "student_id",
                "as": "student_info"
            }
        },
        {
            "$lookup": {
                "from": "bins",
                "localField": "bin_id",
                "foreignField": "bin_id",
                "as": "bin_info"
            }
        },
        {
            "$project": {
                "_id": 0,
                "session_id": 1,
                "student_id": 1,
                "bin_id": 1,
                "status": 1,
                "started_at": 1,
                "ended_at": 1,
                "items_thrown": 1,
                "points_earned": 1,
                "student_name": {"$arrayElemAt": ["$student_info.name", 0]},
                "bin_location": {"$arrayElemAt": ["$bin_info.location", 0]}
            }
        }
    ]
    
    sessions = list(bin_sessions_collection.aggregate(pipeline))
    
    return jsonify({
        "sessions": sessions,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit
    }), 200

@sessions_bp.route('/force-end', methods=['POST'])
@jwt_required()
def force_end_session():
    # Admin only check
    student_id = get_jwt_identity()
    from models.db import students_collection
    admin_user = students_collection.find_one({"student_id": student_id, "role": "admin"})
    if not admin_user:
        return jsonify({"error": "Unauthorized. Admin access required."}), 403

    data = request.json
    session_id = data.get('session_id')

    if not session_id:
        return jsonify({"error": "session_id is required"}), 400

    result = bin_sessions_collection.update_one(
        {"session_id": session_id, "status": "active"},
        {"$set": {
            "status": "manually_ended",
            "ended_at": datetime.utcnow()
        }}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Active session not found"}), 404

    return jsonify({"message": "Session terminated"}), 200
