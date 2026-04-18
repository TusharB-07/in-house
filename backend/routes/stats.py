from flask import Blueprint, jsonify
from models.db import bins_collection, disposals_collection, bin_sessions_collection, students_collection
from datetime import datetime, timedelta

stats_bp = Blueprint('stats', __name__)

@stats_bp.route('/summary', methods=['GET'])
def get_system_stats():
    # 1. Basic counts
    total_bins = bins_collection.count_documents({})
    full_bins = bins_collection.count_documents({"fill_level": {"$gte": 90}})
    active_sessions = bin_sessions_collection.count_documents({"status": "active"})
    
    # 2. Today's disposals
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    disposals_today = disposals_collection.count_documents({"timestamp": {"$gte": today_start}})
    
    # 3. Anonymous disposal % (PRD 5.6)
    total_disposals = disposals_collection.count_documents({})
    anonymous_disposals = disposals_collection.count_documents({"student_id": None})
    anonymous_percentage = round((anonymous_disposals / total_disposals * 100), 1) if total_disposals > 0 else 0
    
    # 4. Session stats
    past_sessions = list(bin_sessions_collection.find({"status": {"$ne": "active"}}))
    total_past = len(past_sessions)
    
    avg_items = 0
    avg_duration = 0
    if total_past > 0:
        total_items = sum(s.get('items_thrown', 0) for s in past_sessions)
        avg_items = round(total_items / total_past, 1)
        
        durations = []
        for s in past_sessions:
            if s.get('ended_at') and s.get('started_at'):
                durations.append((s['ended_at'] - s['started_at']).total_seconds())
        if durations:
            avg_duration = round(sum(durations) / len(durations), 0)

    # 5. Waste Distribution (Pie Chart)
    dry_count = disposals_collection.count_documents({"waste_type": "dry"})
    wet_count = disposals_collection.count_documents({"waste_type": "wet"})

    return jsonify({
        "total_bins": total_bins,
        "full_bins": full_bins,
        "active_sessions": active_sessions,
        "disposals_today": disposals_today,
        "anonymous_percentage": anonymous_percentage,
        "session_stats": {
            "avg_items_per_session": avg_items,
            "avg_session_duration_seconds": avg_duration,
            "total_completed_sessions": total_past
        },
        "waste_distribution": {
            "dry": dry_count,
            "wet": wet_count
        }
    }), 200
