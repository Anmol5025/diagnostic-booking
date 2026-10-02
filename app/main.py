from fastapi import FastAPI
from app.api.endpoints import auth, centres, tests, bookings, payments
from app.db.session import engine
from app.models.models import Base

app = FastAPI(title="Diagnostic Booking Service")

@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(centres.router, prefix="/centres", tags=["centres"])
app.include_router(tests.router, prefix="/tests", tags=["tests"])
app.include_router(bookings.router, prefix="/bookings", tags=["bookings"])
app.include_router(payments.router, prefix="/payments", tags=["payments"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Diagnostic Booking Service API"}
