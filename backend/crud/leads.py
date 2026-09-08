from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.lead import Lead
from schemas.lead import LeadCreate, LeadUpdate


async def get_lead_by_id(session: AsyncSession, lead_id: UUID) -> Lead | None:
    result = await session.execute(select(Lead).where(Lead.id == lead_id))
    return result.scalar_one_or_none()


async def list_leads(
    session: AsyncSession, skip: int = 0, limit: int = 100
) -> list[Lead]:
    result = await session.execute(select(Lead).offset(skip).limit(limit))
    return list(result.scalars().all())


async def create_lead(session: AsyncSession, lead_data: LeadCreate) -> Lead:
    lead = Lead(**lead_data.model_dump())
    session.add(lead)
    await session.commit()
    await session.refresh(lead)
    return lead


async def update_lead(
    session: AsyncSession, lead_id: UUID, lead_data: LeadUpdate
) -> Lead | None:
    lead = await get_lead_by_id(session, lead_id)
    if lead is None:
        return None

    for field, value in lead_data.model_dump(exclude_unset=True).items():
        setattr(lead, field, value)

    await session.commit()
    await session.refresh(lead)
    return lead
