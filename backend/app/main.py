from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, calls, queue, translators, bookings, companies
from app.db.session import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Translation Platform API",
    description="API for translation booking and call center management",
    version="2.0.0"
)

# CORS middleware - Allow both domain and IP-based access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://app.interpretation-service.com:3000",
        "http://meet.interpretation-service.com:8443",
        "http://192.168.2.134:3000",  # IP-based access for network devices
        "http://192.168.2.134:8443",  # Jitsi IP access
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(calls.router)
app.include_router(queue.router)
app.include_router(translators.router)
app.include_router(bookings.router)
app.include_router(companies.router)

@app.get("/")
async def root():
    return {"message": "Call Center API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
