from pydantic import BaseModel, EmailStr
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.models.models import BookingStatus

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[str] = None

class CentreCreate(BaseModel):
    name: str
    location: str

class CentreResponse(BaseModel):
    id: UUID
    name: str
    location: str
    created_at: datetime

    class Config:
        from_attributes = True

class TestCreate(BaseModel):
    name: str
    description: Optional[str] = None

class TestResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class CentreTestCreate(BaseModel):
    test_id: UUID
    price: float

class CentreTestResponse(BaseModel):
    id: UUID
    centre_id: UUID
    test_id: UUID
    price: float
    is_available: bool

    class Config:
        from_attributes = True

class BookingCreate(BaseModel):
    centre_id: UUID
    test_id: UUID
    appointment_time: datetime

class BookingResponse(BaseModel):
    id: UUID
    user_id: UUID
    centre_id: UUID
    test_id: UUID
    appointment_time: datetime
    amount: float
    status: BookingStatus
    payment_reference: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class PaymentRequest(BaseModel):
    booking_id: UUID
    amount: float
    simulate_status: str  # 'SUCCESS' or 'FAILED'

class PaymentResponse(BaseModel):
    booking_id: UUID
    status: BookingStatus
    payment_reference: str

class WebhookPayload(BaseModel):
    transaction_id: str
    booking_id: UUID
    status: str
