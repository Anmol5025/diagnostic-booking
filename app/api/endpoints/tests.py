from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.schemas.schemas import TestCreate, TestResponse
from app.models.models import DiagnosticTest

router = APIRouter()

@router.post("/", response_model=TestResponse, status_code=status.HTTP_201_CREATED)
async def create_test(test_in: TestCreate, db: AsyncSession = Depends(get_db)):
    new_test = DiagnosticTest(**test_in.dict())
    db.add(new_test)
    await db.commit()
    await db.refresh(new_test)
    return new_test

@router.get("/", response_model=List[TestResponse])
async def list_tests(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DiagnosticTest))
    return result.scalars().all()
