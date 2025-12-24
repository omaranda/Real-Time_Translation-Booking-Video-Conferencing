from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.security import get_password_hash, get_current_user
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.translator import (
    TranslatorRegister,
    TranslatorResponse,
    TranslatorAvailability,
    TranslatorUpdate
)
from app.services.email_service import (
    send_verification_email,
    generate_verification_token,
    get_verification_token_expiry
)

router = APIRouter(prefix="/translators", tags=["translators"])

@router.post("/register", response_model=TranslatorResponse, status_code=status.HTTP_201_CREATED)
async def register_translator(
    translator_data: TranslatorRegister,
    db: Session = Depends(get_db)
):
    """Register a new translator"""
    # Check if translator already exists
    existing_user = db.query(User).filter(User.email == translator_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Validate languages
    valid_languages = ["SPANISH", "FRENCH", "GERMAN"]
    for lang in translator_data.languages:
        if lang not in valid_languages:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid language: {lang}. Must be one of: {', '.join(valid_languages)}",
            )

    # Generate email verification token
    verification_token = generate_verification_token()
    token_expiry = get_verification_token_expiry()

    # Create translator
    translator = User(
        email=translator_data.email,
        name=translator_data.name,
        hashed_password=get_password_hash(translator_data.password),
        role=UserRole.TRANSLATOR,
        languages=translator_data.languages,
        hourly_rate=translator_data.hourly_rate,
        is_available=True,
        is_email_verified=False,
        email_verification_token=verification_token,
        email_verification_token_expires=token_expiry
    )

    db.add(translator)
    db.commit()
    db.refresh(translator)

    # Send verification email
    send_verification_email(translator.email, translator.name, verification_token)

    return translator

@router.get("/", response_model=List[TranslatorResponse])
async def get_translators(
    language: str = None,
    available_only: bool = False,
    db: Session = Depends(get_db)
):
    """Get list of translators, optionally filtered by language and availability"""
    query = db.query(User).filter(User.role == UserRole.TRANSLATOR)

    if available_only:
        query = query.filter(User.is_available == True)

    if language:
        # Filter translators who have this language
        query = query.filter(User.languages.contains([language]))

    translators = query.all()
    return translators

@router.get("/{translator_id}", response_model=TranslatorResponse)
async def get_translator(
    translator_id: str,
    db: Session = Depends(get_db)
):
    """Get translator details"""
    translator = db.query(User).filter(
        User.id == translator_id,
        User.role == UserRole.TRANSLATOR
    ).first()

    if not translator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Translator not found"
        )

    return translator

@router.put("/{translator_id}/availability", response_model=TranslatorResponse)
async def update_availability(
    translator_id: str,
    availability: TranslatorAvailability,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update translator availability status"""
    # Check if current user is the translator or an admin
    if str(current_user.id) != translator_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this translator"
        )

    translator = db.query(User).filter(
        User.id == translator_id,
        User.role == UserRole.TRANSLATOR
    ).first()

    if not translator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Translator not found"
        )

    translator.is_available = availability.is_available
    db.commit()
    db.refresh(translator)

    return translator

@router.put("/{translator_id}", response_model=TranslatorResponse)
async def update_translator(
    translator_id: str,
    update_data: TranslatorUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update translator profile"""
    # Check if current user is the translator or an admin
    if str(current_user.id) != translator_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this translator"
        )

    translator = db.query(User).filter(
        User.id == translator_id,
        User.role == UserRole.TRANSLATOR
    ).first()

    if not translator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Translator not found"
        )

    # Update fields
    if update_data.name is not None:
        translator.name = update_data.name
    if update_data.languages is not None:
        translator.languages = update_data.languages
    if update_data.is_available is not None:
        translator.is_available = update_data.is_available
    if update_data.hourly_rate is not None:
        translator.hourly_rate = update_data.hourly_rate

    db.commit()
    db.refresh(translator)

    return translator
