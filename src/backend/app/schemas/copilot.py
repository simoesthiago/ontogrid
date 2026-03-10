from pydantic import BaseModel, Field


class CopilotQueryRequest(BaseModel):
    question: str = Field(min_length=1)
    dataset_ids: list[str] = Field(default_factory=list)
    entity_ids: list[str] = Field(default_factory=list)
    start: str | None = None
    end: str | None = None
    locale: str = "pt-BR"


class CopilotCitation(BaseModel):
    source_code: str
    dataset_id: str
    version_id: str
    entity_id: str | None = None


class CopilotQueryResponse(BaseModel):
    answer: str
    citations: list[CopilotCitation]
    follow_up_questions: list[str]
