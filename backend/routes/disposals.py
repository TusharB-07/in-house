import os
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from models.db import disposals_collection, students_collection, bins_collection, bin_sessions_collection

disposals_bp = Blueprint('disposals', __name__)

SERVICE_SECRET = os.getenv("SERVICE_SECRET", "ml-service-key-xyz")

@disposals_bp.route('/log', methods=['POST'])
def log_disposal():
    # Validate X-Service-Key header (PRD 5.4)
    service_key = request.headers.get('X-Service-Key')
    if service_key != SERVICE_SECRET:
        return jsonify({"error": "Unauthorized service"}), 401

    data = request.json
    bin_id = data.get('bin_id')
    waste_type = data.get('waste_type') # PRD: must be 'dry' or 'wet'
    confidence = data.get('confidence', 0)
    is_correct = data.get('is_correct', True)
    image_url = data.get('image_url', "")

    if waste_type not in ['dry', 'wet']:
        return jsonify({"error": "waste_type must be 'dry' or 'wet'"}), 400

    if not bin_id:
        return jsonify({"error": "bin_id is required"}), 400

    now = datetime.utcnow()
    points_awarded = 0
    student_id = None
    session_id = None

    # 1. Look up active session for this bin
    active_session = bin_sessions_collection.find_one({
        "bin_id": bin_id,
        "status": "active"
    })

    if active_session:
        # Check for inactivity expiry (PRD 5.4)
        last_activity = active_session['last_activity']
        timeout = int(os.getenv("SESSION_TIMEOUT_SECONDS", 30))
        if (now - last_activity).total_seconds() >= timeout:
            # Expire session
            bin_sessions_collection.update_one(
                {"session_id": active_session['session_id']},
                {"$set": {
                    "status": "expired",
                    "ended_at": now
                }}
            )
            active_session = None # Treat as no session
        else:
            student_id = active_session['student_id']
            session_id = active_session['session_id']

    # 2. Reward Logic (only if active session found)
    if student_id:
        student = students_collection.find_one({"student_id": student_id})
        if student:
            if is_correct:
                # Streak Logic (PRD 6.2)
                last_correct_date_str = student.get('last_correct_date') # 'YYYY-MM-DD'
                today_str = now.date().isoformat()
                
                streak_days = student.get('streak_days', 0)
                
                if not last_correct_date_str:
                    streak_days = 1
                    last_correct_date_str = today_str
                else:
                    # Parse dates to compute delta
                    last_date = datetime.strptime(last_correct_date_str, '%Y-%m-%d').date()
                    today_date = now.date()
                    delta = (today_date - last_date).days
                    
                    if delta == 0:
                        # Already disposed correctly today, streak unchanged
                        pass
                    elif delta == 1:
                        # Last correct disposal was yesterday, increment streak
                        streak_days += 1
                        last_correct_date_str = today_str
                    else:
                        # Missed one or more days, reset streak to 1
                        streak_days = 1
                        last_correct_date_str = today_str
                
                # Points Calculation (PRD 6.1)
                # Base 10, +5 bonus for 3-6 day streak, +10 bonus for 7+ day streak
                if streak_days >= 7:
                    points_awarded = 20
                elif streak_days >= 3:
                    points_awarded = 15
                else:
                    points_awarded = 10
                
                # Update student stats
                students_collection.update_one(
                    {"student_id": student_id},
                    {
                        "$inc": {
                            "points": points_awarded, 
                            "total_disposals": 1, 
                            "correct_disposals": 1
                        },
                        "$set": {
                            "streak_days": streak_days,
                            "last_correct_date": last_correct_date_str
                        }
                    }
                )

                # Update session stats
                bin_sessions_collection.update_one(
                    {"session_id": session_id},
                    {
                        "$set": {"last_activity": now},
                        "$inc": {
                            "items_thrown": 1,
                            "points_earned": points_awarded
                        }
                    }
                )
            else:
                # Incorrect disposal: Reset streak to 0 (PRD 6.2)
                students_collection.update_one(
                    {"student_id": student_id},
                    {
                        "$inc": {"total_disposals": 1},
                        "$set": {"streak_days": 0}
                    }
                )
                # Still update last activity in session
                bin_sessions_collection.update_one(
                    {"session_id": session_id},
                    {
                        "$set": {"last_activity": now},
                        "$inc": {"items_thrown": 1}
                    }
                )

    # 3. Update bin status
    bins_collection.update_one(
        {"bin_id": bin_id},
        {
            "$set": {"last_classification": waste_type, "last_updated": now},
            "$inc": {"total_disposals": 1}
        }
    )

    # 4. Log the disposal
    disposal_log = {
        "bin_id": bin_id,
        "session_id": session_id,
        "student_id": student_id, # Can be None (Anonymous)
        "waste_type": waste_type,
        "confidence": confidence,
        "is_correct": is_correct,
        "points_awarded": points_awarded,
        "image_url": image_url,
        "timestamp": now
    }
    
    result = disposals_collection.insert_one(disposal_log)
    
    return jsonify({
        "message": "Disposal logged successfully",
        "disposal_id": str(result.inserted_id),
        "student_id": student_id,
        "session_id": session_id,
        "points_awarded": points_awarded
    }), 201

@disposals_bp.route('/all', methods=['GET'])
def get_all_disposals():
    # Paginated list with filters
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 50))
    bin_id = request.args.get('bin_id')
    student_id = request.args.get('student_id')
    session_id = request.args.get('session_id')
    waste_type = request.args.get('waste_type') or request.args.get('type')
    date_str = request.args.get('date')
    anonymous_only = request.args.get('anonymous') == 'true'

    query = {}
    if bin_id:
        query['bin_id'] = bin_id
    if student_id:
        query['student_id'] = student_id
    if session_id:
        query['session_id'] = session_id
    if waste_type:
        query['waste_type'] = waste_type
    if anonymous_only:
        query['student_id'] = None
    if date_str:
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d')
            query['timestamp'] = {
                "$gte": target_date,
                "$lt": target_date + timedelta(days=1)
            }
        except ValueError:
            pass

    total = disposals_collection.count_documents(query)
    disposals = list(disposals_collection.find(query, {'_id': 0})
                     .sort("timestamp", -1)
                     .skip((page - 1) * limit)
                     .limit(limit))
    
    return jsonify({
        "disposals": disposals,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit
    }), 200
