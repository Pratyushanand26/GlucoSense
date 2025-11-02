<div align="center">

# 🩺 **GlucoSense Health App**
### _AI-Powered Health Monitoring for comman Diseas Patients_

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-6.0+-4DB33D?style=for-the-badge&logo=mongodb&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

</div>

---

## 🌟 Overview

**GlucoSense** is an **AI-powered health monitoring platform** built for **comman diseas patients and doctors**.  
It allows patients to log daily health data (like glucose levels, sleep, heart rate, and more) and helps doctors analyze trends using integrated **AI models** (Gemini / ML models) to provide personalized insights and recommendations.

---

## 🧱 Project Structure
```bash
glucosense/
├── Readme.md
├── mock_server.py # Local mock API for testing
├── requirements.txt
│
├── frontend/ # React frontend
│ ├── package.json
│ └── src/
│ ├── App.jsx
│ ├── components/
│ │ ├── Button.jsx
│ │ ├── ChartCard.jsx
│ │ ├── Input.jsx
│ │ └── Loader.jsx
│ ├── context/
│ │ └── AuthContext.jsx
│ ├── hooks/
│ │ └── useAuth.jsx
│ ├── pages/
│ │ ├── Dashboard.jsx
│ │ ├── Login.jsx
│ │ └── Register.jsx
│ ├── services/
│ │ └── api.js
│ ├── styles/
│ │ └── theme.css
│ └── utils/
│ └── constants.js
│
├── models/ # AI & health model logic
│ ├── diseseas_specific.py
│ ├── evaluator.py
│ ├── prompt.py
│ ├── recommander.py
│ ├── uitls.py
│ └── .env.example
│
└── server/ # FastAPI backend
├── init.py
├── ai_service.py
├── auth.py
├── config.py
├── database.py
├── health_service.py
├── main.py # Entry point
├── models.py
└── routes/
├── init.py
├── auth.py
├── doctor.py
└── patient.py

```
---

## ⚙️ Setup Instructions

Follow these steps to run **GlucoSense** locally.  
Everything below works on **Windows, macOS, and Linux**.  

---

### 🧩 1. Clone the Repository
```bash
git clone https://github.com/pratyushanand26/GlucoSense.git
```
```bash
cd GlucoSense
```
Windows
```bash
python -m venv venv
venv\Scripts\activate
```
macOS/Linux
```bash
python3 -m venv venv
source venv/bin/activate
```
```bash
pip install -r requirements.txt
```
Configure Environment Variables

Create a .env file inside the models/ or root folder (based on your structure).
Use the following template
```bash
MONGO_CONNECTION_STRING=mongodb://localhost:27017/glucosense
GEMINI_API_KEY=your_gemini_api_key_here
```

Run the Main FastAPI Server

Once your .env is configured and MongoDB is running
```bash
python -m server.main
```

