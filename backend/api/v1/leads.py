from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user, get_db
from crud.leads import (
    create_lead,
    get_lead_by_id,
    list_leads,
    update_lead,
)
from models.user import User
from schemas.lead import LeadCreate, LeadResponse, LeadUpdate


router = APIRouter(prefix="/leads", tags=["leads"])


@router.post("", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead_endpoint(
    lead_data: LeadCreate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LeadResponse:
    return await create_lead(session, lead_data, owner_id=current_user.id)


@router.get("", response_model=list[LeadResponse], status_code=status.HTTP_200_OK)
async def list_leads_endpoint(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[LeadResponse]:
    owner_id = None if current_user.role == "admin" else current_user.id
    return await list_leads(
        session, skip=skip, limit=limit, owner_id=owner_id
    )


@router.get("/{lead_id}", response_model=LeadResponse, status_code=status.HTTP_200_OK)
async def get_lead_endpoint(
    lead_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LeadResponse:
    owner_id = None if current_user.role == "admin" else current_user.id
    lead = await get_lead_by_id(session, lead_id, owner_id=owner_id)
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    return lead


@router.patch("/{lead_id}", response_model=LeadResponse, status_code=status.HTTP_200_OK)
async def update_lead_endpoint(
    lead_id: UUID,
    lead_data: LeadUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LeadResponse:
    owner_id = None if current_user.role == "admin" else current_user.id
    lead = await update_lead(
        session, lead_id, lead_data, owner_id=owner_id
    )
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    return lead
