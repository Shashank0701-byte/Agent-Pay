from fastapi import FastAPI, HTTPException

from app.config import get_settings
from app.schemas import AgentCreate, AgentResponse, PaymentDecision, PaymentRequestCreate, PolicyUpdate
from app.services.policy_engine import evaluate_payment

settings = get_settings()

app = FastAPI(title=settings.app_name, version="0.1.0")

agents: dict[str, dict] = {}
policies: dict[str, dict] = {}


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.environment,
    }


@app.post("/api/v1/agents", response_model=AgentResponse, status_code=201)
def create_agent(payload: AgentCreate) -> dict:
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
def upsert_policy(agent_id: str, payload: PolicyUpdate) -> dict:
    if agent_id not in agents:
        raise HTTPException(status_code=404, detail="agent not found")

    policies[agent_id] = payload.model_dump()
    return policies[agent_id]


@app.post("/api/v1/agents/{agent_id}/payments/requests", response_model=PaymentDecision)
def request_payment(agent_id: str, payload: PaymentRequestCreate) -> dict:
    if agent_id not in agents:
        raise HTTPException(status_code=404, detail="agent not found")

    policy = policies.get(agent_id, {})
    decision = evaluate_payment(policy, payload.amount, payload.category)
    payment_id = f"pay_{len(agents) + 1}"

    if decision["decision"] == "denied":
        return {
            "id": payment_id,
            "status": decision["status"],
            "decision": decision["decision"],
            "amount": payload.amount,
            "currency": payload.currency,
        }

    if decision["decision"] == "auto_approved":
        return {
            "id": payment_id,
            "status": "approved",
            "decision": "auto_approved",
            "amount": payload.amount,
            "currency": payload.currency,
        }

    return {
        "id": payment_id,
        "status": "approval_required",
        "decision": "human_approval",
        "amount": payload.amount,
        "currency": payload.currency,
        "approval_id": f"apr_{len(agents) + 1}",
    }
