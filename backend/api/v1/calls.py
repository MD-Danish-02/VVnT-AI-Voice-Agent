from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user, get_db
from crud.calls import create_call, get_call_by_id, list_calls_by_lead
from crud.leads import get_lead_by_id
from models.user import User
from schemas.call import CallCreate, CallResponse


router = APIRouter(tags=["calls"])


def _owner_id_for_user(current_user: User) -> UUID | None:
    return None if current_user.role == "admin" else current_user.id


@router.post("/calls", response_model=CallResponse, status_code=status.HTTP_201_CREATED)
async def create_call_endpoint(
    call_data: CallCreate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CallResponse:
    owner_id = _owner_id_for_user(current_user)
    lead = await get_lead_by_id(session, call_data.lead_id, owner_id=owner_id)
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")

    return await create_call(
        session,
        lead_id=lead.id,
        status=call_data.status,
        started_at=call_data.started_at,
        ended_at=call_data.ended_at,
        duration=call_data.duration,
        transcript=call_data.transcript,
        summary=call_data.summary,
    )


@router.get("/calls/{call_id}", response_model=CallResponse, status_code=status.HTTP_200_OK)
async def get_call_endpoint(
    call_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CallResponse:
    call = await get_call_by_id(session, call_id)
    if call is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Call not found")

    lead = await get_lead_by_id(
        session, call.lead_id, owner_id=_owner_id_for_user(current_user)
    )
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Call not found")

    return call


@router.get(
    "/leads/{lead_id}/calls",
    response_model=list[CallResponse],
    status_code=status.HTTP_200_OK,
)
async def list_calls_for_lead_endpoint(
    lead_id: UUID,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[CallResponse]:
    lead = await get_lead_by_id(
        session, lead_id, owner_id=_owner_id_for_user(current_user)
    )
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")

    return await list_calls_by_lead(session, lead.id, skip=skip, limit=limit)