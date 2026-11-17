from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.limiter import limiter
from app.core.config import settings
from app.routers import auth, github, analysis

app = FastAPI(title=settings.APP_NAME, version="1.0.0", debug=settings.DEBUG)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# for request dadta
app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(github.router, prefix="/api/v1")
app.include_router(analysis.router, prefix="/api/v1")

@app.get("/")
def home():
    return {"message": "GitHub Code Analyzer API", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy"}
