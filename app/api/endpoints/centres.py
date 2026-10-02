from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.schemas.schemas import CentreCreate, CentreResponse, CentreTestCreate, CentreTestResponse
from app.models.models import DiagnosticCentre, CentreTest, DiagnosticTest

router = APIRouter()

@router.post("/", response_model=CentreResponse, status_code=status.HTTP_201_CREATED)
async def create_centre(centre_in: CentreCreate, db: AsyncSession = Depends(get_db)):
    new_centre = DiagnosticCentre(**centre_in.dict())
    db.add(new_centre)
    await db.commit()
    await db.refresh(new_centre)
    return new_centre

@router.get("/", response_model=List[CentreResponse])
async def list_centres(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DiagnosticCentre))
    return result.scalars().all()

@router.get("/{centre_id}", response_model=CentreResponse)
async def get_centre(centre_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DiagnosticCentre).filter(DiagnosticCentre.id == centre_id))
    centre = result.scalars().first()
    if not centre:
        raise HTTPException(status_code=404, detail="Centre not found")
    return centre

@router.post("/{centre_id}/tests/", response_model=CentreTestResponse, status_code=status.HTTP_201_CREATED)
async def link_test_to_centre(centre_id: UUID, test_in: CentreTestCreate, db: AsyncSession = Depends(get_db)):
    # Check if centre exists
    centre = await db.get(DiagnosticCentre, centre_id)
    if not centre:
        raise HTTPException(status_code=404, detail="Centre not found")
    
    # Check if test exists
    test = await db.get(DiagnosticTest, test_in.test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    # Check if link already exists
    result = await db.execute(select(CentreTest).filter(CentreTest.centre_id == centre_id, CentreTest.test_id == test_in.test_id))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Test already linked to this centre")

    new_link = CentreTest(centre_id=centre_id, test_id=test_in.test_id, price=test_in.price)
    db.add(new_link)
    await db.commit()
    await db.refresh(new_link)
    return new_link

@router.get("/{centre_id}/tests/", response_model=List[CentreTestResponse])
async def list_tests_for_centre(centre_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CentreTest).filter(CentreTest.centre_id == centre_id, CentreTest.is_available == True))
    return result.scalars().all()
