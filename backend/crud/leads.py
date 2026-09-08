from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.lead import Lead
from schemas.lead import LeadCreate, LeadUpdate


async def get_lead_by_id(
    session: AsyncSession, lead_id: UUID, owner_id: UUID | None = None
) -> Lead | None:
    query = select(Lead).where(Lead.id == lead_id)
    if owner_id is not None:
        query = query.where(Lead.owner_id == owner_id)

    result = await session.execute(query)
    return result.scalar_one_or_none()


async def list_leads(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    owner_id: UUID | None = None,
) -> list[Lead]:
    query = select(Lead)
    if owner_id is not None:
        query = query.where(Lead.owner_id == owner_id)

    result = await session.execute(query.offset(skip).limit(limit))
    return list(result.scalars().all())


async def create_lead(
    session: AsyncSession, lead_data: LeadCreate, owner_id: UUID | None = None
) -> Lead:
    lead = Lead(**lead_data.model_dump(), owner_id=owner_id)
    session.add(lead)
    await session.commit()
    await session.refresh(lead)
    return lead


async def update_lead(
    session: AsyncSession,
    lead_id: UUID,
    lead_data: LeadUpdate,
    owner_id: UUID | None = None,
) -> Lead | None:
    lead = await get_lead_by_id(session, lead_id, owner_id=owner_id)
    if lead is None:
        return None

    for field, value in lead_data.model_dump(exclude_unset=True).items():
        setattr(lead, field, value)

    await session.commit()
    await session.refresh(lead)
    return lead
