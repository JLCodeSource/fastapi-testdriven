from typing import Optional

# fmt: off
from app.models.pydantic import (SummaryPayloadSchema,
                                 SummaryUpdatePayloadSchema)
# fmt: on
from app.models.tortoise import TextSummary


async def post(payload: SummaryPayloadSchema) -> int:
    summary = TextSummary(
        url=payload.url,
        summary="",
    )
    await summary.save()
    return summary.id


async def get_all() -> list:
    summaries = await TextSummary.all().values()
    return summaries


async def get(id: int) -> Optional[dict]:
    summary = await TextSummary.filter(id=id).first().values()
    if summary:
        return summary
    return None


async def delete(id: int) -> int:
    summary = await TextSummary.filter(id=id).delete()

    return summary


async def put(id: int, payload: SummaryUpdatePayloadSchema) -> Optional[dict]:
    summary = await TextSummary.filter(id=id).update(
        url=payload.url, summary=payload.summary
    )
    if not summary:
        return None

    updated_summary = await TextSummary.filter(id=id).first().values()
    return updated_summary
