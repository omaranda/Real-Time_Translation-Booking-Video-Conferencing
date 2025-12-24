from sqlalchemy import Column, String, Enum as SQLEnum, Boolean, ForeignKey, Table, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
import uuid
import enum
from datetime import datetime

from app.db.session import Base

class UserRole(str, enum.Enum):
    TRANSLATOR = "TRANSLATOR"
    EMPLOYEE = "EMPLOYEE"
    COMPANY_ADMIN = "COMPANY_ADMIN"
    ADMIN = "ADMIN"

class Language(str, enum.Enum):
    SPANISH = "SPANISH"
    FRENCH = "FRENCH"
    GERMAN = "GERMAN"

# Association table for translator languages
translator_languages = Table(
    'translator_languages',
    Base.metadata,
    Column('translator_id', UUID(as_uuid=True), ForeignKey('users.id')),
    Column('language', SQLEnum(Language))
)

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.EMPLOYEE)

    # Translator-specific fields
    languages = Column(ARRAY(String), nullable=True)  # For translators
    is_available = Column(Boolean, default=True)
    hourly_rate = Column(String, nullable=True)  # For translators

    # Employee-specific fields
    company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id'), nullable=True)

    # Email verification fields
    is_email_verified = Column(Boolean, default=False, nullable=False)
    email_verification_token = Column(String, nullable=True)
    email_verification_token_expires = Column(DateTime, nullable=True)

    # Relationships
    company = relationship("Company", back_populates="employees")
    translator_bookings = relationship("Booking", foreign_keys="[Booking.translator_id]", back_populates="translator")
    employee_bookings = relationship("Booking", foreign_keys="[Booking.employee_id]", back_populates="employee")

class Company(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    contact_email = Column(String, unique=True, nullable=False)
    contact_phone = Column(String, nullable=True)
    address = Column(Text, nullable=True)

    # Relationships
    employees = relationship("User", back_populates="company")
