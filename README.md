# Smart Waste Management System

A comprehensive web-based platform for monitoring and managing smart waste bins, incentivizing proper disposal through a gamified student points system.

## 🚀 Features

### **Student Portal**
- **User Authentication:** Secure signup and login using student credentials.
- **Smart Disposal:** Start sessions via Bin ID to log waste disposals.
- **Gamification:** Earn points for correct disposals and track your streak.
- **Leaderboard:** View top-performing students and track your rank.
- **Profile Management:** View personal stats, disposal history, and earned points.

### **Admin Dashboard**
- **Real-time Monitoring:** Track bin fill levels and system-wide stats.
- **Bin Management:** Register new bins and monitor their status (Online/Offline).
- **Analytics:** View total disposals, success rates, and active sessions.
- **Student Oversight:** Manage student records and award/deduct points manually if needed.

---

## 🛠 Tech Stack

- **Frontend:** HTML5, CSS3, JavaScript (Vanilla JS)
- **Backend:** Python (Flask)
- **Database:** MongoDB
- **Security:** JWT (JSON Web Tokens) for authentication, Bcrypt for password hashing
- **Environment:** Python 3.x, Flask-CORS for cross-origin resource sharing

---

## 📂 Project Structure

```text
in-house/
├── backend/            # Flask API server
│   ├── models/         # Database schemas and connection
│   ├── routes/         # API endpoint definitions (Blueprints)
│   ├── app.py          # Main entry point
│   └── requirements.txt# Backend dependencies
├── frontend/           # Web interface
│   ├── css/            # Stylesheets
│   ├── js/             # API integration and logic
│   └── *.html          # UI Pages
└── SmartWaste_PRD.docx # Project Requirements Document
```

---

## 📡 API Endpoints

### **Authentication** (`/api/auth`)
- `POST /register`: Register a new student.
- `POST /login`: Authenticate and receive a JWT.

### **Students** (`/api/students`)
- `GET /all`: Get all students (Admin only).
- `GET /<student_id>`: Get specific student details and stats.
- `GET /leaderboard`: Get top students by points.
- `POST /award`: Manually award points (Admin only).

### **Bins** (`/api/bins`)
- `GET /all`: List all registered smart bins.
- `GET /<bin_id>`: Get detailed status of a specific bin.
- `POST /register`: Add a new smart bin.
- `POST /update`: Update bin fill level or status.

### **Sessions & Disposals** (`/api/sessions`, `/api/disposals`)
- `POST /sessions/start`: Begin a disposal session.
- `POST /sessions/end`: Complete a disposal session.
- `POST /disposals/log`: Record a waste disposal event.
- `GET /disposals/all`: View disposal logs.

### **Statistics** (`/api/stats`)
- `GET /summary`: System-wide statistics (Total disposals, Bins active, etc.)

---

## ⚙️ Local Setup

### **1. Prerequisites**
- Python 3.8+
- MongoDB (Running locally or on Atlas)
- Git

### **2. Backend Setup**
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables (Create a `.env` file):
   ```env
   MONGO_URI=mongodb://localhost:27017/smartwaste
   JWT_SECRET=your_super_secret_key
   ```
5. Run the server:
   ```bash
   python app.py
   ```
   *The API will be available at `http://127.0.0.1:5001`.*

### **3. Frontend Setup**
1. The frontend consists of static files. You can serve them using any local server (e.g., Live Server in VS Code) or simply open `frontend/index.html` in your browser.
2. Ensure the `api.js` in `frontend/js/` points to your local backend URL.

---

## 👥 Admin Access
By default, the system initializes an admin account on the first run:
- **Username:** `admin`
- **Password:** `admin123`
