# ECOIN - Smart Waste Reward System

ECOIN is a comprehensive web-based platform for monitoring and managing smart waste bins, incentivizing proper disposal through a gamified student points system.

## 🚀 Features

### **Student Portal**
- **Personalized Dashboard:** Dynamic frosted glass UI with real-time greetings and avatar initials.
- **Bin Syncing:** Establish a network link with smart bins using MAC IDs.
- **QR Scanning:** Integrated high-speed QR code scanner for instant bin connection.
- **Reward System:** Earn "ECOIN" credits for proper waste disposal.
- **Performance Registry:** Track your balance, daily streaks, and campus ranking.

### **Gamification**
- **Global Rankings:** View the "Top 3" champions on a stylized podium and see the full campus leaderboard.
- **Streak Tracking:** Build and maintain daily streaks to multiply your rewards.

## ⚙️ Local Setup

### **1. Prerequisites**
- Python 3.8+
- MongoDB (Running locally on `localhost:27017`)
- PowerShell (Windows)

### **2. Backend Setup**
1. Open a terminal and navigate to the backend directory:
   ```powershell
   cd backend
   ```
2. Create and activate a virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
4. Configure environment variables (Create a `.env` file in `backend/`):
   ```env
   MONGO_URI=mongodb://localhost:27017/smart-waste
   PORT=5001
   SECRET_KEY=dev-secret-key-123
   JWT_SECRET_KEY=dev-jwt-secret-key-456
   ```
5. Run the server:
   ```powershell
   python app.py
   ```

### **3. Frontend Setup**
1. Open a **second terminal** and navigate to the frontend directory:
   ```powershell
   cd frontend
   ```
2. Start a simple local server:
   ```powershell
   python -m http.server 3000
   ```
3. Open `http://localhost:3000` in your browser.

## 🛠️ Development Mode
To instantly test the system without a backend, open `frontend/js/mock-login.js` and set:
```javascript
const MOCK_ENABLED = true;
```

---

## 👥 Admin Access
Default credentials for the initial run:
- **Username:** `admin`
- **Password:** `admin123`
