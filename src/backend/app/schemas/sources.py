from pydantic import BaseModel


class SourceItem(BaseModel):
    id: str
    code: str
    name: str
    authority_type: str
    refresh_strategy: str
    status: str


class SourceListResponse(BaseModel):
    items: list[SourceItem]
    total: int
