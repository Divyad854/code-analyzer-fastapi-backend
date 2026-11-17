from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import RegisterRequest, UserResponse, TokenResponse
from app.utils.security import hash_password, verify_password, create_access_token
from app.core.config import settings
from app.limiter import limiter

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
# @limiter.limit("5/minute"): Allows up to five requests per minute under the configured SlowAPI rate-limit key.
@limiter.limit("5/minute")
def register(request: Request, payload: RegisterRequest, db: Session = Depends(get_db)):
    # the data received from the user through the API request body
    username = payload.username.strip()

    email = str(payload.email).lower()
    # case-insensitive matching
    existing = db.query(User).filter(or_(User.username.ilike(username), User.email == email)).first()
    if existing:
        raise HTTPException(status_code=409, detail="Username or email is already registered")
    user = User(username=username, email=email, hashed_password=hash_password(payload.password))
    db.add(user)
    try:
        db.commit()
        # undoes the failed transaction and resets the session so it can be used again.
        db.refresh(user)
    except IntegrityError:
        # 	Undo a failed transaction
        db.rollback()
        raise HTTPException(status_code=409, detail="Username or email is already registered")
    return user

@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
def login(request: Request, form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(or_(User.username == form.username, User.email == form.username.lower())).first()
    if not user or not verify_password(form.password, user.hashed_password) or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid username/email or password", headers={"WWW-Authenticate": "Bearer"})
    token = create_access_token(user.id)
    return {"access_token": token, "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60}

@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user
