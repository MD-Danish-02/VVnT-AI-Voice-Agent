from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user, get_db
from crud.appointments import (
    create_appointment,
    get_appointment_by_id,
    list_appointments_by_lead,
    update_appointment,
)
from crud.leads import get_lead_by_id
from models.user import User
from schemas.appointment import (
    AppointmentCreate,
    AppointmentResponse,
    AppointmentUpdate,
)


router = APIRouter(tags=["appointments"])


def _owner_id_for_user(current_user: User) -> UUID | None:
    return None if current_user.role == "admin" else current_user.id


@router.post(
    "/appointments",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_appointment_endpoint(
    appointment_data: AppointmentCreate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AppointmentResponse:
    owner_id = _owner_id_for_user(current_user)
    lead = await get_lead_by_id(session, appointment_data.lead_id, owner_id=owner_id)
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")

    return await create_appointment(session, appointment_data)


@router.get(
    "/appointments/{appointment_id}",
    response_model=AppointmentResponse,
    status_code=status.HTTP_200_OK,
)
async def get_appointment_endpoint(
    appointment_id: UUID,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AppointmentResponse:
    appointment = await get_appointment_by_id(session, appointment_id)
    if appointment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")

    lead = await get_lead_by_id(
        session, appointment.lead_id, owner_id=_owner_id_for_user(current_user)
    )
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")

    return appointment


@router.get(
    "/leads/{lead_id}/appointments",
    response_model=list[AppointmentResponse],
    status_code=status.HTTP_200_OK,
)
async def list_appointments_for_lead_endpoint(
    lead_id: UUID,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[AppointmentResponse]:
    lead = await get_lead_by_id(
        session, lead_id, owner_id=_owner_id_for_user(current_user)
    )
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")

    return await list_appointments_by_lead(session, lead.id, skip=skip, limit=limit)


@router.patch(
    "/appointments/{appointment_id}",
    response_model=AppointmentResponse,
    status_code=status.HTTP_200_OK,
)
async def update_appointment_endpoint(
    appointment_id: UUID,
    appointment_data: AppointmentUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AppointmentResponse:
    appointment = await get_appointment_by_id(session, appointment_id)
    if appointment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")

    lead = await get_lead_by_id(
        session, appointment.lead_id, owner_id=_owner_id_for_user(current_user)
    )
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")

    updated = await update_appointment(session, appointment_id, appointment_data)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")

    return updated
