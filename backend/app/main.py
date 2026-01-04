from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.chat import router as chat_router
from app.middleware.session import SessionMiddleware

app = FastAPI(title="Chat API", version="1.0.0")

# CORS middleware to allow requests from frontend (must be first)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,  # Required for cookies
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session middleware - creates session automatically on first request
app.add_middleware(SessionMiddleware)

# Include routes
app.include_router(chat_router)


@app.get("/")
async def root():
    return {"message": "Chat API is running"}


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}
