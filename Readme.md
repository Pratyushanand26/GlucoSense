# GlucoSense

## Project Structure

```
GlucoSense/
├── .env
├── requirements.txt
├── mock_server.py (unchanged)
├── README.md
│
├── server/
│   ├── __init__.py
│   ├── main.py              # Clean entry point
│   ├── config.py            # All configuration
│   ├── database.py          # MongoDB setup
│   ├── models.py            # All Pydantic models
│   ├── auth.py              # Authentication logic
│   ├── ai_service.py        # AI/LLM integration
│   ├── health_service.py    # Health data processing
│   └── routes/
│       ├── __init__.py
│       ├── auth.py          # Auth endpoints
│       ├── patient.py       # Patient endpoints
│       └── doctor.py        # Doctor endpoints
│
└── models/ (kept for reference, not used in server)
    ├── evaluator.py
    ├── recommender.py
    └── prompt.py
```

## Setup Instructions

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the mock server:
   ```bash
   python mock_server.py
   ```

3. Run the main server:
   ```bash
   python -m server.main
   ```

4. Access the API documentation:
   - Mock Server: [http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs)
   - Main Server: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Environment Variables

Ensure the `.env` file is configured with the following:
```
MONGO_CONNECTION_STRING=<your_mongo_connection_string>
GEMINI_API_KEY=<your_gemini_api_key>
```
