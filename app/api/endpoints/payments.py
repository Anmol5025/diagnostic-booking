from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from uuid import UUID
import uuid

from app.db.session import get_db
from app.schemas.schemas import PaymentRequest, PaymentResponse, WebhookPayload
from app.models.models import Booking, BookingStatus

router = APIRouter()

@router.post("/", response_model=PaymentResponse)
async def simulate_payment(
    payment_req: PaymentRequest,
    db: AsyncSession = Depends(get_db)
):
    # Retrieve the booking
    booking = await db.get(Booking, payment_req.booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.status != BookingStatus.PENDING:
        raise HTTPException(status_code=400, detail="Booking is not in a pending state")

    if float(booking.amount) != payment_req.amount:
        raise HTTPException(status_code=400, detail="Payment amount does not match booking amount")

    transaction_id = str(uuid.uuid4())
    
    if payment_req.simulate_status.upper() == 'SUCCESS':
        booking.status = BookingStatus.CONFIRMED
    else:
        booking.status = BookingStatus.FAILED
        
    booking.payment_reference = transaction_id
    await db.commit()
    await db.refresh(booking)

    return PaymentResponse(
        booking_id=booking.id,
        status=booking.status,
        payment_reference=transaction_id
    )

@router.post("/webhook/")
async def payment_webhook(
    payload: WebhookPayload,
    db: AsyncSession = Depends(get_db)
):
    """
    Idempotent Webhook for payment status updates.
    It expects payload with transaction_id, booking_id, and status ('SUCCESS' or 'FAILED').
    """
    # 1. Idempotency check
    result = await db.execute(select(Booking).filter(Booking.payment_reference == payload.transaction_id))
    existing_booking_by_ref = result.scalars().first()
    if existing_booking_by_ref:
        # We already processed this transaction_id, return 200 OK immediately
        return {"message": "Webhook already processed"}

    # 2. Process new event
    booking = await db.get(Booking, payload.booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # If it's already confirmed or cancelled by other means, we might want to ignore or handle
    if booking.status in [BookingStatus.CONFIRMED, BookingStatus.CANCELLED]:
        return {"message": f"Booking already {booking.status.value}"}

    # Apply update
    if payload.status.upper() == 'SUCCESS':
        booking.status = BookingStatus.CONFIRMED
    else:
        booking.status = BookingStatus.FAILED
    
    booking.payment_reference = payload.transaction_id
    await db.commit()
    
    return {"message": "Webhook processed successfully"}
