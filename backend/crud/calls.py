from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.call import Call


async def get_call_by_id(session: AsyncSession, call_id: UUID) -> Call | None:
    result = await session.execute(select(Call).where(Call.id == call_id))
    return result.scalar_one_or_none()


async def list_calls_by_lead(
    session: AsyncSession, lead_id: UUID, skip: int = 0, limit: int = 100
) -> list[Call]:
    result = await session.execute(
        select(Call).where(Call.lead_id == lead_id).offset(skip).limit(limit)
    )
    return list(result.scalars().all())


async def create_call(
    session: AsyncSession,
    lead_id: UUID,
    status: str = "pending",
    started_at: Optional[datetime] = None,
    ended_at: Optional[datetime] = None,
    duration: Optional[int] = None,
    transcript: Optional[str] = None,
    summary: Optional[str] = None,
) -> Call:
    call = Call(
        lead_id=lead_id,
        status=status,
        started_at=started_at,
        ended_at=ended_at,
        duration=duration,
        transcript=transcript,
        summary=summary,
    )
    session.add(call)
    await session.commit()
    await session.refresh(call)
    return call
