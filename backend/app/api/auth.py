from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta, datetime

from app.core.config import settings
from app.core.security import (
    create_access_token,
    verify_password,
    get_password_hash,
    get_current_user
)
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import LoginRequest, Token, UserResponse, UserCreate
from app.services.email_service import (
    send_verification_email,
    send_welcome_email,
    generate_verification_token,
    get_verification_token_expiry
)

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Check if email is verified
    if not user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email address before logging in. Check your inbox for the verification link.",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    return current_user

@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Generate email verification token
    verification_token = generate_verification_token()
    token_expiry = get_verification_token_expiry()

    user = User(
        email=user_data.email,
        name=user_data.name,
        role=user_data.role,
        hashed_password=get_password_hash(user_data.password),
        is_email_verified=False,
        email_verification_token=verification_token,
        email_verification_token_expires=token_expiry
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Send verification email
    send_verification_email(user.email, user.name, verification_token)

    return user


@router.post("/verify-email")
async def verify_email(
    token: str,
    db: Session = Depends(get_db)
):
    """Verify user email with token"""
    # Find user with this token
    user = db.query(User).filter(User.email_verification_token == token).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token",
        )

    # Check if already verified
    if user.is_email_verified:
        return {
            "message": "Email already verified",
            "verified": True
        }

    # Check if token expired
    if user.email_verification_token_expires and user.email_verification_token_expires < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token has expired. Please request a new one.",
        )

    # Verify email
    user.is_email_verified = True
    user.email_verification_token = None
    user.email_verification_token_expires = None
    db.commit()

    # Send welcome email
    send_welcome_email(user.email, user.name)

    return {
        "message": "Email verified successfully! You can now log in.",
        "verified": True
    }


@router.post("/resend-verification")
async def resend_verification(
    email: str,
    db: Session = Depends(get_db)
):
    """Resend verification email"""
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.is_email_verified:
        return {
            "message": "Email already verified"
        }

    # Generate new token
    verification_token = generate_verification_token()
    token_expiry = get_verification_token_expiry()

    user.email_verification_token = verification_token
    user.email_verification_token_expires = token_expiry
    db.commit()

    # Resend verification email
    send_verification_email(user.email, user.name, verification_token)

    return {
        "message": "Verification email sent successfully. Please check your inbox."
    }
