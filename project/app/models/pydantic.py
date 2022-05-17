from pydantic import BaseModel


class SummaryPayloadSchemas(BaseModel):
    url: str
