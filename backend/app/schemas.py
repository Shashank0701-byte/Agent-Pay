from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    email: str


class AgentCreate(BaseModel):
    name: str = Field(..., min_length=1)


class AgentResponse(BaseModel):
    id: str
    name: str
    status: str
    api_key: str
    created_at: str


class PolicyUpdate(BaseModel):
    monthly_limit: int = 10000
    auto_approve_limit: int = 500
    max_transaction: int = 2000
    allowed_categories: list[str] = ["software", "cloud", "api"]
    blocked_categories: list[str] = ["gambling", "crypto"]


class PaymentRequestCreate(BaseModel):
    amount: int
    currency: str = "INR"
    merchant: str
    reason: str
    category: str


class PaymentDecision(BaseModel):
    id: str
    status: str
    decision: str
    amount: int
    currency: str
    approval_id: str | None = None


class ApprovalDecision(BaseModel):
    id: str
    status: str
    payment_id: str
    approved_by: str | None = None
