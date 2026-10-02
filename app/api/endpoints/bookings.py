from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from uuid import UUID
from datetime import datetime

from app.db.session import get_db
from app.schemas.schemas import BookingCreate, BookingResponse
from app.models.models import Booking, BookingStatus, CentreTest, User
from app.api.dependencies import get_current_user

router = APIRouter()

@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_in: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Ensure appointment time is in the future
    if booking_in.appointment_time.tzinfo is None:
        if booking_in.appointment_time < datetime.utcnow():
            raise HTTPException(status_code=400, detail="Appointment time must be in the future")
    else:
        if booking_in.appointment_time < datetime.now(booking_in.appointment_time.tzinfo):
            raise HTTPException(status_code=400, detail="Appointment time must be in the future")

    # Check if the centre offers this test
    result = await db.execute(
        select(CentreTest).filter(
            CentreTest.centre_id == booking_in.centre_id,
            CentreTest.test_id == booking_in.test_id,
            CentreTest.is_available == True
        )
    )
    centre_test = result.scalars().first()
    if not centre_test:
        raise HTTPException(status_code=400, detail="This test is not available at the selected centre")

    new_booking = Booking(
        user_id=current_user.id,
        centre_id=booking_in.centre_id,
        test_id=booking_in.test_id,
        appointment_time=booking_in.appointment_time,
        amount=centre_test.price,
        status=BookingStatus.PENDING
    )
    db.add(new_booking)
    await db.commit()
    await db.refresh(new_booking)
    return new_booking

@router.get("/", response_model=List[BookingResponse])
async def list_user_bookings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Booking).filter(Booking.user_id == current_user.id))
    return result.scalars().all()

@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Booking).filter(Booking.id == booking_id, Booking.user_id == current_user.id))
    booking = result.scalars().first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

@router.patch("/{booking_id}/cancel", response_model=BookingResponse)
async def cancel_booking(
    booking_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Booking).filter(Booking.id == booking_id, Booking.user_id == current_user.id))
    booking = result.scalars().first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    if booking.status != BookingStatus.PENDING:
        raise HTTPException(status_code=400, detail="Only pending bookings can be cancelled")
    
    booking.status = BookingStatus.CANCELLED
    await db.commit()
    await db.refresh(booking)
    return booking
