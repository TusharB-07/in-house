from flask import Blueprint, request, jsonify
from models.db import students_collection, disposals_collection, bin_sessions_collection

students_bp = Blueprint('students', __name__)

@students_bp.route('/all', methods=['GET'])
def get_all_students():
    # Admin view with pagination and search
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 50))
    search = request.args.get('search')

    query = {}
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"student_id": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}}
        ]

    total = students_collection.count_documents(query)
    students = list(students_collection.find(query, {'_id': 0, 'password': 0})
                    .sort("points", -1)
                    .skip((page - 1) * limit)
                    .limit(limit))
    
    return jsonify({
        "students": students,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit
    }), 200

@students_bp.route('/<student_id>', methods=['GET'])
def get_student_profile(student_id):
    student = students_collection.find_one({"student_id": student_id}, {'_id': 0, 'password': 0})
    if not student:
        return jsonify({"error": "Student not found"}), 404
    
    # Calculate rank
    rank = students_collection.count_documents({"points": {"$gt": student.get('points', 0)}}) + 1
    
    # Fetch last 10 disposals
    history = list(disposals_collection.find({"student_id": student_id}, {'_id': 0})
                   .sort("timestamp", -1)
                   .limit(10))
    
    # Fetch last 5 completed sessions (PRD 4.5)
    session_history = list(bin_sessions_collection.find({
        "student_id": student_id,
        "status": {"$ne": "active"}
    }, {'_id': 0}).sort("ended_at", -1).limit(5))
    
    return jsonify({
        "student": student,
        "rank": rank,
        "disposals": history,
        "session_history": session_history
    }), 200

@students_bp.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    # PRD says top 20
    limit = int(request.args.get('limit', 20))
    
    leaderboard = list(students_collection.find({}, 
        {'_id': 0, 'password': 0, 'email': 0, 'qr_code': 0})
        .sort("points", -1)
        .limit(limit))
    
    # Add rank field
    for i, student in enumerate(leaderboard):
        student['rank'] = i + 1
        
    return jsonify(leaderboard), 200

@students_bp.route('/award', methods=['POST'])
def award_points():
    data = request.json
    student_id = data.get('student_id')
    points = data.get('points', 0)

    if not student_id:
        return jsonify({"error": "student_id is required"}), 400

    students_collection.update_one(
        {"student_id": student_id},
        {"$inc": {"points": points}},
        upsert=True
    )

    return jsonify({"message": f"{points} points awarded successfully"}), 200
