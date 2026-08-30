from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.config import get_settings

settings = get_settings()

app = FastAPI(title=settings.app_name, version="0.1.0")


class AgentCreateRequest(BaseModel):
    name: str = Field(..., min_length=1)


class AgentResponse(BaseModel):
    id: str
    name: str
    status: str = "active"
    api_key: str
    created_at: str


class PolicyRequest(BaseModel):
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


class PaymentDecisionResponse(BaseModel):
    id: str
    status: str
    decision: str
    amount: int
    currency: str


agents: dict[str, dict[str, Any]] = {}
policies: dict[str, dict[str, Any]] = {}


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.environment,
    }


@app.post("/api/v1/agents", status_code=201)
def create_agent(payload: AgentCreateRequest) -> dict[str, Any]:
    agent_id = f"agt_{len(agents) + 1}"
    api_key = f"ap_live_{agent_id}"
    agent = {
        "id": agent_id,
        "name": payload.name,
        "status": "active",
        "api_key": api_key,
        "created_at": "2026-08-31T00:00:00Z",
    }
    agents[agent_id] = agent
    policies[agent_id] = {
        "monthly_limit": 10000,
        "auto_approve_limit": 500,
        "max_transaction": 2000,
        "allowed_categories": ["software", "cloud", "api"],
        "blocked_categories": ["gambling", "crypto"],
    }
    return agent


@app.put("/api/v1/agents/{agent_id}/policy")
def upsert_policy(agent_id: str, payload: PolicyRequest) -> dict[str, Any]:
    if agent_id not in agents:
        raise HTTPException(status_code=404, detail="agent not found")

    policies[agent_id] = payload.model_dump()
    return policies[agent_id]


@app.post("/api/v1/agents/{agent_id}/payments/requests")
def request_payment(agent_id: str, payload: PaymentRequestCreate) -> dict[str, Any]:
    if agent_id not in agents:
        raise HTTPException(status_code=404, detail="agent not found")

    policy = policies.get(agent_id, {})
    blocked = policy.get("blocked_categories", [])
    allowed = policy.get("allowed_categories", [])
    if payload.category in blocked:
        return {
            "id": f"pay_{len(agents) + 1}",
            "status": "denied",
            "decision": "denied",
            "amount": payload.amount,
            "currency": payload.currency,
        }

    if payload.amount > int(policy.get("max_transaction", 2000)):
        return {
            "id": f"pay_{len(agents) + 1}",
            "status": "denied",
            "decision": "denied",
            "amount": payload.amount,
            "currency": payload.currency,
        }

    if payload.category not in allowed:
        return {
            "id": f"pay_{len(agents) + 1}",
            "status": "denied",
            "decision": "denied",
            "amount": payload.amount,
            "currency": payload.currency,
        }

    if payload.amount <= int(policy.get("auto_approve_limit", 500)):
        return {
            "id": f"pay_{len(agents) + 1}",
            "status": "approved",
            "decision": "auto_approved",
            "amount": payload.amount,
            "currency": payload.currency,
        }

    return {
        "id": f"pay_{len(agents) + 1}",
        "status": "approval_required",
        "decision": "human_approval",
        "amount": payload.amount,
        "currency": payload.currency,
        "approval_id": f"apr_{len(agents) + 1}",
    }
