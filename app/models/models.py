import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from app.db.session import Base

class BookingStatus(str, enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    bookings = relationship("Booking", back_populates="user")

class DiagnosticCentre(Base):
    __tablename__ = "diagnostic_centres"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    tests = relationship("CentreTest", back_populates="centre")
    bookings = relationship("Booking", back_populates="centre")

class DiagnosticTest(Base):
    __tablename__ = "diagnostic_tests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    centres = relationship("CentreTest", back_populates="test")
    bookings = relationship("Booking", back_populates="test")

class CentreTest(Base):
    __tablename__ = "centre_tests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    centre_id = Column(UUID(as_uuid=True), ForeignKey("diagnostic_centres.id"), nullable=False)
    test_id = Column(UUID(as_uuid=True), ForeignKey("diagnostic_tests.id"), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    is_available = Column(Boolean, default=True)

    centre = relationship("DiagnosticCentre", back_populates="tests")
    test = relationship("DiagnosticTest", back_populates="centres")

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    centre_id = Column(UUID(as_uuid=True), ForeignKey("diagnostic_centres.id"), nullable=False)
    test_id = Column(UUID(as_uuid=True), ForeignKey("diagnostic_tests.id"), nullable=False)
    appointment_time = Column(DateTime, nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING, nullable=False)
    payment_reference = Column(String, nullable=True, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="bookings")
    centre = relationship("DiagnosticCentre", back_populates="bookings")
    test = relationship("DiagnosticTest", back_populates="bookings")
