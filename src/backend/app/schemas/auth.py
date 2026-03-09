from pydantic import BaseModel


class RequestContext(BaseModel):
    user_id: str
    tenant_id: str
    role: str
