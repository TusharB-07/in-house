import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/smart-waste")
client = MongoClient(MONGO_URI)
db = client.get_database("smart-waste")
students_collection = db.students

def clean_duplicates():
    print(f"Checking for duplicates in {students_collection.name}...")
    
    # Find all student_ids
    all_students = list(students_collection.find({}, {"student_id": 1}))
    ids = [s['student_id'] for s in all_students]
    
    from collections import Counter
    counts = Counter(ids)
    duplicates = [id for id, count in counts.items() if count > 1]
    
    if not duplicates:
        print("No duplicates found.")
        return

    for dup_id in duplicates:
        print(f"Found duplicate student_id: {dup_id}. Keeping only the first one...")
        # Keep the first one, delete the rest
        docs = list(students_collection.find({"student_id": dup_id}).sort("_id", 1))
        keep_id = docs[0]['_id']
        delete_result = students_collection.delete_many({
            "student_id": dup_id,
            "_id": {"$ne": keep_id}
        })
        print(f"Deleted {delete_result.deleted_count} duplicates for {dup_id}.")

if __name__ == "__main__":
    clean_duplicates()
