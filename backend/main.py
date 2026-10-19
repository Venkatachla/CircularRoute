import os
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.circular_routes import router as circular_router

# Load environment variables
load_dotenv()

app_name = os.getenv("APP_NAME", "CircularRoute Backend")
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")

app = FastAPI(
    title=app_name,
    description="Backend API for Circular Copy-to Section OCR & Recipient Extraction",
    version="1.0.0"
)

# Configure CORS to allow local dev origins (ports 8080, 5173, 3000, etc.)
origins = [
    "*",
    frontend_url,
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(circular_router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to CircularRoute Backend API",
        "docs": "/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host=host, port=port, reload=True)
