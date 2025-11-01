"""Main FastAPI application"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import GEMINI_API_KEY
from .database import init_db
from .routes import auth, patient, doctor

app = FastAPI(
    title="GlucoSense Health API",
    description="AI-powered health monitoring for diabetic patients",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(patient.router)
app.include_router(doctor.router)

@app.on_event("startup")
async def startup():
    """Initialize on startup"""
    await init_db()
    print("✅ GlucoSense API started")
    print(f"✅ AI: {'Enabled' if GEMINI_API_KEY else 'Disabled'}")

@app.get("/", tags=["Health"])
async def root():
    """API health check"""
    return {"service": "GlucoSense", "status": "running", "version": "2.0.0"}

@app.get("/health", tags=["Health"])
async def health():
    """Detailed health check"""
    return {
        "api": "healthy",
        "ai_service": "enabled" if GEMINI_API_KEY else "disabled",
        "database": "connected"
    }

if __name__ == "__main__":
    print("=" * 60)
    print("🩺 GlucoSense Health API")
    print("=" * 60)
    print("📍 http://127.0.0.1:8000")
    print("📚 http://127.0.0.1:8000/docs")
    print("🔐 doctor@example.com / doctorpass")
    print("=" * 60)
    uvicorn.run("server.main:app", host="127.0.0.1", port=8000, reload=True)