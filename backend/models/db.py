import os
import certifi
import sys
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/smart-waste")

try:
    # Only use certifi for Atlas (mongodb+srv://)
    client_kwargs = {
        "serverSelectionTimeoutMS": 5000
    }
    if MONGO_URI.startswith("mongodb+srv://"):
        client_kwargs["tlsCAFile"] = certifi.where()
        
    client = MongoClient(MONGO_URI, **client_kwargs)
    # Trigger a quick connection test
    client.admin.command('ping')
    print(f"✅ MongoDB Connected: {MONGO_URI}")
except ServerSelectionTimeoutError as e:
    print("\n❌ DATABASE CONNECTION ERROR:")
    print("1. Check if your IP is whitelisted in MongoDB Atlas (Network Access).")
    print("2. Ensure you have a stable internet connection.")
    print(f"Error Details: {e}")
    # We don't exit here to allow the app to potentially use a local fallback if configured
except Exception as e:
    print(f"❌ Unexpected Database Error: {e}")

db = client.get_database("smart-waste")

# Collections
bins_collection = db.bins
disposals_collection = db.disposals
students_collection = db.students
bin_sessions_collection = db.bin_sessions

def setup_indexes():
    """Create all indexes specified in PRD 2.4."""
    try:
        # bins
        bins_collection.create_index("bin_code", unique=True)
        bins_collection.create_index("fill_level")
        
        # bin_sessions
        bin_sessions_collection.create_index([("student_id", 1), ("status", 1)])
        bin_sessions_collection.create_index([("bin_id", 1), ("status", 1)])
        bin_sessions_collection.create_index("last_activity")
        
        # disposals
        disposals_collection.create_index([("bin_id", 1), ("timestamp", 1)])
        disposals_collection.create_index([("student_id", 1), ("timestamp", 1)])
        
        # students
        students_collection.create_index("student_id", unique=True)
        students_collection.create_index([("points", -1)])
        
        print("✅ MongoDB Indexes Created/Verified")
    except Exception as e:
        print(f"❌ Error creating indexes: {e}")

# Call setup_indexes on import (or you could call it in app.py)
setup_indexes()
