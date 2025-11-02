# 🩺 GlucoSense - AI-Powered Health Monitoring Platform

> **An intelligent health monitoring system that combines wearable device data with AI analysis to provide personalized health insights and disease risk assessment.**

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg?style=for-the-badge&logo=python)](https://www.python.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-4EA94B?style=for-the-badge&logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![Google AI](https://img.shields.io/badge/Google_Gemini-8E75B2?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)

---

## 🌟 Overview

**GlucoSense** is a comprehensive health monitoring platform designed for diabetic and at-risk patients. It integrates with wearable devices to collect health metrics and uses Google's Gemini AI to provide:

- 📊 **Real-time Health Analysis** - Daily check-ins with device data integration
- 🤖 **AI-Powered Insights** - Personalized health evaluations and recommendations
- ⚕️ **Disease Risk Assessment** - Predictive analysis for Type 2 Diabetes, TB, and CVD
- 👨‍⚕️ **Doctor Dashboard** - Healthcare provider interface for patient monitoring
- 📈 **Trend Tracking** - Long-term health metric visualization

---

## 🚀 Live Deployment

**🌐 API Endpoint:** `https://your-deployed-endpoint.com`  
**📚 Interactive API Docs:** `https://your-deployed-endpoint.com/docs`

### Demo Credentials

**Doctor Account:**
- Email: `doctor@example.com`
- Password: `doctorpass`

**Patient Account:**
- Sign up via `/api/v1/auth/signup` endpoint

---

## 🏗️ Architecture

```
GlucoSense/
├── server/                 # FastAPI Backend
│   ├── routes/            # API Endpoints
│   │   ├── auth.py       # Authentication
│   │   ├── patient.py    # Patient operations
│   │   └── doctor.py     # Doctor operations
│   ├── models.py         # Pydantic schemas
│   ├── database.py       # MongoDB connection
│   ├── ai_service.py     # Gemini AI integration
│   ├── health_service.py # Health data processing
│   └── main.py           # FastAPI app
├── models/                # AI Analysis Logic
│   ├── evaluator.py      # Health evaluation
│   ├── recommander.py    # Recommendation engine
│   ├── diseseas_specific.py  # Disease risk analysis
│   └── prompt.py         # AI prompts
├── mock_server.py        # Mock device data server
├── requirements.txt      # Python dependencies
└── .env                  # Environment variables
```

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** - High-performance async API framework
- **Motor** - Async MongoDB driver
- **Pydantic** - Data validation
- **Passlib** - Password hashing

### AI & ML
- **Google Gemini 2.5 Pro** - Advanced LLM for health analysis
- Custom prompts for medical evaluation and recommendations

### Database
- **MongoDB Atlas** - Cloud NoSQL database
- Collections: `users`, `daily_records`

### Security
- **Bcrypt** - Password hashing
- **Bearer Token Authentication**
- Role-based access control (Patient/Doctor)

---

## 📦 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- MongoDB Atlas account (or local MongoDB)
- Google Gemini API key

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/pratyushanand26/GlucoSense.git
cd GlucoSense
```

### 2️⃣ Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Environment Variables

Create a `.env` file in the root directory:

```env
MONGO_CONNECTION_STRING=mongodb+srv://username:password@cluster.mongodb.net/?appName=Cluster0
GEMINI_API_KEY=your_gemini_api_key_here
```

**Get your credentials:**
- MongoDB: [cloud.mongodb.com](https://cloud.mongodb.com)
- Gemini API: [ai.google.dev](https://ai.google.dev)

### 5️⃣ Run the Server

```bash
python -m server.main
```

The API will start on `http://127.0.0.1:8000`

**Access interactive docs:** `http://127.0.0.1:8000/docs`

---

## 🎯 Key Features

### 1. Patient Features

#### Daily Check-in
```bash
POST /api/v1/user/checkin
```
Combines manual inputs (weight, symptoms, mood) with device data (heart rate, sleep, steps)

#### AI Health Analysis
```bash
GET /api/v1/user/analyze
```
Comprehensive evaluation of health trends and patterns

#### Personalized Recommendations
```bash
GET /api/v1/user/recommend
```
Actionable lifestyle suggestions and medical advice

#### Disease Risk Assessment
```bash
GET /api/v1/user/disease-specific
```
Risk percentages for Type 2 Diabetes, TB, and Cardiovascular Disease

### 2. Doctor Features

#### Patient Management
```bash
GET /api/v1/doctor/patients
GET /api/v1/doctor/patients/search
```
View and search patient records

#### Patient Analysis
```bash
GET /api/v1/doctor/patients/{patient_id}/analyze
GET /api/v1/doctor/patients/{patient_id}/recommend
```
Access AI-powered analysis for any patient

#### Health Timeline
```bash
GET /api/v1/doctor/patients/{patient_id}/timeline
```
Visualize patient health trends over time

#### Dashboard Statistics
```bash
GET /api/v1/doctor/dashboard
```
Overview of practice metrics

---

## 📊 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/signup` | Register new patient |
| POST | `/api/v1/auth/login` | Login (patient/doctor) |

### Patient Operations
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/user/profile` | Get profile |
| PUT | `/api/v1/user/profile` | Update profile |
| POST | `/api/v1/user/checkin` | Submit daily check-in |
| GET | `/api/v1/user/checkins` | View check-in history |
| GET | `/api/v1/user/summary` | Get health summary |
| GET | `/api/v1/user/analyze` | AI health analysis |
| GET | `/api/v1/user/recommend` | AI recommendations |
| GET | `/api/v1/user/disease-specific` | Disease risk analysis |

### Doctor Operations
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/doctor/patients` | List all patients |
| GET | `/api/v1/doctor/patients/search` | Search patients |
| GET | `/api/v1/doctor/patients/{id}/profile` | View patient profile |
| GET | `/api/v1/doctor/patients/{id}/checkins` | View patient check-ins |
| GET | `/api/v1/doctor/patients/{id}/analyze` | Analyze patient |
| GET | `/api/v1/doctor/patients/{id}/recommend` | Get recommendations |
| GET | `/api/v1/doctor/patients/{id}/timeline` | View health timeline |
| GET | `/api/v1/doctor/dashboard` | Dashboard stats |

---

## 🧪 Testing the API

### 1. Using Swagger UI
Navigate to `http://127.0.0.1:8000/docs` for interactive API testing

### 2. Using cURL

**Sign Up:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "patient@test.com",
    "password": "password123",
    "age": 45,
    "height_cm": 170,
    "sex": "Male",
    "medical_history": {
      "chronic_conditions": ["Type 2 Diabetes"],
      "current_medications": ["Metformin"]
    },
    "family_history": {
      "diabetes": true
    },
    "lifestyle_factors": {
      "smoking_status": "Non-smoker",
      "alcohol_consumption": "Occasional",
      "exercise_habits": "Moderate"
    }
  }'
```

**Login:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "patient@test.com",
    "password": "password123"
  }'
```

**Submit Check-in:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/user/checkin" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "body_weight_kg": 75.5,
    "illness_symptoms": {
      "present": false
    },
    "energy_level": 7,
    "muscle_soreness": 3,
    "mood_state": 8
  }'
```

---

## 🤖 AI Analysis System

### Health Evaluation
Analyzes patient data using Google Gemini 2.5 Pro to identify:
- Health trends and patterns
- Areas of concern
- Positive indicators
- Actionable recommendations

### Disease Risk Assessment
Calculates risk percentages for:
- **Type 2 Diabetes** - Based on BMI, family history, lifestyle
- **Tuberculosis** - Exposure risk, location, symptoms
- **Cardiovascular Disease** - 10-year risk using clinical factors

### Recommendation Engine
Provides personalized advice on:
- Sleep optimization
- Physical activity
- Stress management
- Nutrition
- When to seek medical care

---

## 📱 Mock Device Server

The platform includes a mock wearable device server for testing:

```bash
python mock_server.py
```

Runs on `http://127.0.0.1:8001` and generates realistic health metrics:
- Heart Rate & HRV
- Sleep duration
- Activity (steps, calories)
- SpO₂ levels
- Skin temperature

---

## 🔐 Security Features

- **Password Hashing:** Bcrypt with salt
- **Token Authentication:** Bearer tokens with role validation
- **Role-Based Access:** Patient/Doctor permissions
- **Data Privacy:** Users can only access their own data
- **CORS Protection:** Configurable origins

---

## 📈 Database Schema

### Users Collection
```json
{
  "_id": "uuid",
  "email": "user@example.com",
  "hashed_password": "bcrypt_hash",
  "role": "patient|doctor",
  "age": 45,
  "height_cm": 170,
  "sex": "Male",
  "body_weight_kg": 75.5,
  "medical_history": {...},
  "family_history": {...},
  "lifestyle_factors": {...}
}
```

### Daily Records Collection
```json
{
  "_id": "uuid",
  "user_id": "user_uuid",
  "date": "2025-11-02",
  "checkin_data": {
    "body_weight_kg": 75.5,
    "illness_symptoms": {...},
    "energy_level": 7,
    "muscle_soreness": 3,
    "mood_state": 8
  },
  "device_data": {
    "heart_rate": {...},
    "hrv": {...},
    "sleep": {...},
    "activity": {...},
    "spo2": {...},
    "skin_temp": {...}
  }
}
```

---

## 🐛 Troubleshooting

### MongoDB Connection Issues
```bash
# Check connection string format
MONGO_CONNECTION_STRING=mongodb+srv://user:pass@cluster.mongodb.net/

# Verify network access in MongoDB Atlas
# Add your IP address to the whitelist
```

### Gemini API Errors
```bash
# Verify API key is valid
# Check quota at https://ai.google.dev/

# Rate limiting: The system retries failed requests
```

### Import Errors
```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt

# Check Python version
python --version  # Should be 3.8+
```

---

## 🚀 Deployment

### Environment Variables for Production
```env
MONGO_CONNECTION_STRING=your_production_mongodb_uri
GEMINI_API_KEY=your_production_api_key
SECRET_KEY=your_strong_secret_key
```

### Recommended Platforms
- **Backend:** Render, Railway, Fly.io, or AWS
- **Database:** MongoDB Atlas (Free tier available)
- **Frontend:** Vercel, Netlify (if you add a UI)

---

## 🤝 Contributing

This is a hackathon project. Feel free to fork and improve!

### Development Setup
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is open source and available under the MIT License.

---

## 👥 Team

- **Pratyush Anand** - [GitHub](https://github.com/pratyushanand26)

---

## 🙏 Acknowledgments

- Google Gemini AI for health analysis capabilities
- MongoDB Atlas for database hosting
- FastAPI framework for excellent async support
- All open-source contributors

---

## 📞 Support

For questions or issues:
- Open an issue on GitHub
- Check the `/docs` endpoint for API documentation
- Review error logs in the console

---

**Built with ❤️ for better health monitoring**
