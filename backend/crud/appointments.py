from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.appointment import Appointment
from schemas.appointment import AppointmentCreate, AppointmentUpdate


async def get_appointment_by_id(
    session: AsyncSession, appointment_id: UUID
) -> Appointment | None:
    result = await session.execute(
        select(Appointment).where(Appointment.id == appointment_id)
    )
    return result.scalar_one_or_none()


async def list_appointments_by_lead(
    session: AsyncSession, lead_id: UUID, skip: int = 0, limit: int = 100
) -> list[Appointment]:
    result = await session.execute(
        select(Appointment)
        .where(Appointment.lead_id == lead_id)
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def create_appointment(
    session: AsyncSession, appointment_data: AppointmentCreate
) -> Appointment:
    appointment = Appointment(**appointment_data.model_dump())
    session.add(appointment)
    await session.commit()
    await session.refresh(appointment)
    return appointment


async def update_appointment(
    session: AsyncSession,
    appointment_id: UUID,
    appointment_data: AppointmentUpdate,
) -> Appointment | None:
    appointment = await get_appointment_by_id(session, appointment_id)
    if appointment is None:
        return None

    for field, value in appointment_data.model_dump(exclude_unset=True).items():
        setattr(appointment, field, value)

    await session.commit()
    await session.refresh(appointment)
    return appointment
