from flask import Flask, jsonify
from flask_cors import CORS
from routes.bins import bins_bp
from routes.disposals import disposals_bp
from routes.students import students_bp
from routes.auth import auth_bp, bcrypt
from routes.sessions import sessions_bp
from routes.stats import stats_bp
from flask_jwt_extended import JWTManager
import os

app = Flask(__name__)
# Configure CORS (PRD 9.2)
CORS_ORIGIN = os.getenv('CORS_ORIGIN', '*')
CORS(app, resources={r"/api/*": {"origins": CORS_ORIGIN}}, supports_credentials=True)

# JWT Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET', 'smartwaste-dev-secret-key-2026')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 86400 # 24 hours (PRD 5.1)

# Initialize extensions
bcrypt.init_app(app)
jwt = JWTManager(app)

# Register blueprints
app.register_blueprint(bins_bp, url_prefix='/api/bins')
app.register_blueprint(disposals_bp, url_prefix='/api/disposals')
app.register_blueprint(students_bp, url_prefix='/api/students')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(sessions_bp, url_prefix='/api/sessions')
app.register_blueprint(stats_bp, url_prefix='/api/stats')

# Create default admin (PRD 5.1)
with app.app_context():
    try:
        from models.db import students_collection
        if not students_collection.find_one({"role": "admin"}):
            admin_data = {
                "student_id": "admin",
                "email": "admin@srmist.edu.in",
                "password": bcrypt.generate_password_hash("admin123", 12).decode('utf-8'),
                "name": "System Administrator",
                "role": "admin",
                "points": 0,
                "total_disposals": 0,
                "correct_disposals": 0,
                "streak_days": 0,
                "is_active": True,
                "created_at": datetime.utcnow()
            }
            students_collection.insert_one(admin_data)
            print("✅ Default admin created: admin / admin123")
    except Exception as e:
        print(f"⚠️ Could not initialize admin data: {e}")

@app.route('/')
def home():
    return jsonify({"message": "Smart Waste Management API is running", "status": "active"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5001)
