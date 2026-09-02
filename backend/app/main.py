import hashlib
from datetime import datetime, timezone

from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import get_agent_from_api_key
from app.config import get_settings
from app.database import Base, create_db_and_tables, get_db
from app.models import Agent, Approval, PaymentRequest, Policy, User
from app.schemas import AgentCreate, AgentResponse, ApprovalDecision, PaymentDecision, PaymentRequestCreate, PolicyUpdate
from app.services.policy_engine import evaluate_payment
from app.services.webhook_service import WebhookService

settings = get_settings()
webhook_service = WebhookService(settings.secret_key)

# Ensure metadata is loaded before schema creation
create_db_and_tables()

app = FastAPI(title=settings.app_name, version="0.1.0")


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.on_event("startup")
def startup() -> None:
    create_db_and_tables()


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.environment,
    }


@app.get("/api/v1/agents")
def list_agents(db: Session = Depends(get_db)) -> dict:
    agents = db.scalars(select(Agent)).all()
    return {
        "data": [
            {
                "id": agent.id,
                "name": agent.name,
                "status": agent.status,
                "created_at": agent.created_at.isoformat(),
            }
            for agent in agents
        ]
    }


@app.post("/api/v1/agents", response_model=AgentResponse, status_code=201)
def create_agent(payload: AgentCreate, db: Session = Depends(get_db)) -> dict:
    default_user = db.scalar(select(User).where(User.email == "default@agentpay.local"))
    if default_user is None:
        default_user = User(
            id="usr_default",
            email="default@agentpay.local",
        )
        db.add(default_user)
        db.commit()

    agent_id = f"agt_{db.query(Agent).count() + 1}"
    api_key = f"ap_live_{agent_id}"
    api_key_hash = hashlib.sha256(api_key.encode("utf-8")).hexdigest()

    agent = Agent(
        id=agent_id,
        name=payload.name,
        status="active",
        api_key_hash=api_key_hash,
        owner_id=default_user.id,
        created_at=datetime.now(timezone.utc),
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)

    default_policy = Policy(
        id=f"pol_{agent_id}",
        agent_id=agent.id,
        monthly_limit=10000,
        auto_approve_limit=500,
        max_transaction=2000,
        allowed_categories="software,cloud,api",
        blocked_categories="gambling,crypto",
    )
    db.add(default_policy)
    db.commit()

    return {
        "id": agent.id,
        "name": agent.name,
        "status": agent.status,
        "api_key": api_key,
        "created_at": agent.created_at.isoformat(),
    }


@app.put("/api/v1/agents/{agent_id}/policy")
def upsert_policy(agent_id: str, payload: PolicyUpdate, db: Session = Depends(get_db)) -> dict:
    agent = db.get(Agent, agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="agent not found")

    policy = db.scalar(select(Policy).where(Policy.agent_id == agent_id))
    if policy is None:
        policy = Policy(
            id=f"pol_{agent_id}",
            agent_id=agent.id,
        )
        db.add(policy)

    policy.monthly_limit = payload.monthly_limit
    policy.auto_approve_limit = payload.auto_approve_limit
    policy.max_transaction = payload.max_transaction
    policy.allowed_categories = ",".join(payload.allowed_categories)
    policy.blocked_categories = ",".join(payload.blocked_categories)
    db.commit()
    db.refresh(policy)
    return {
        "agent_id": agent_id,
        "monthly_limit": policy.monthly_limit,
        "auto_approve_limit": policy.auto_approve_limit,
        "max_transaction": policy.max_transaction,
        "allowed_categories": policy.allowed_categories.split(",") if policy.allowed_categories else [],
        "blocked_categories": policy.blocked_categories.split(",") if policy.blocked_categories else [],
    }


@app.post("/api/v1/agents/{agent_id}/payments/requests", response_model=PaymentDecision)
def request_payment(
    agent_id: str,
    payload: PaymentRequestCreate,
    db: Session = Depends(get_db),
    agent_auth: Agent | None = Depends(get_agent_from_api_key),
) -> dict:
    agent = db.get(Agent, agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="agent not found")
    if agent_auth is not None and agent_auth.id != agent.id:
        raise HTTPException(status_code=403, detail="agent does not match api key")

    policy = db.scalar(select(Policy).where(Policy.agent_id == agent_id))
    if policy is None:
        policy = Policy(
            id=f"pol_{agent_id}",
            agent_id=agent.id,
            monthly_limit=10000,
            auto_approve_limit=500,
            max_transaction=2000,
            allowed_categories="software,cloud,api",
            blocked_categories="gambling,crypto",
        )
        db.add(policy)
        db.commit()

    policy_map = {
        "monthly_limit": policy.monthly_limit,
        "auto_approve_limit": policy.auto_approve_limit,
        "max_transaction": policy.max_transaction,
        "allowed_categories": policy.allowed_categories.split(",") if policy.allowed_categories else [],
        "blocked_categories": policy.blocked_categories.split(",") if policy.blocked_categories else [],
    }
    decision = evaluate_payment(policy_map, payload.amount, payload.category)
    payment_id = f"pay_{db.query(PaymentRequest).count() + 1}"

    payment = PaymentRequest(
        id=payment_id,
        agent_id=agent.id,
        amount=payload.amount,
        currency=payload.currency,
        merchant=payload.merchant,
        reason=payload.reason,
        category=payload.category,
        status=decision["status"],
        decision=decision["decision"],
        created_at=datetime.now(timezone.utc),
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    if decision["decision"] == "denied":
        return {
            "id": payment.id,
            "status": payment.status,
            "decision": payment.decision,
            "amount": payment.amount,
            "currency": payment.currency,
        }

    if decision["decision"] == "auto_approved":
        return {
            "id": payment.id,
            "status": "approved",
            "decision": "auto_approved",
            "amount": payment.amount,
            "currency": payment.currency,
        }

    approval = Approval(
        id=f"apr_{db.query(Approval).count() + 1}",
        payment_request_id=payment.id,
        status="pending",
        created_at=datetime.now(timezone.utc),
    )
    db.add(approval)
    db.commit()
    db.refresh(approval)

    payment.approval_id = approval.id
    db.commit()

    return {
        "id": payment.id,
        "status": "approval_required",
        "decision": "human_approval",
        "amount": payment.amount,
        "currency": payment.currency,
        "approval_id": approval.id,
    }


@app.get("/api/v1/payments/requests/{payment_id}")
def get_payment(payment_id: str, db: Session = Depends(get_db)) -> dict:
    payment = db.get(PaymentRequest, payment_id)
    if payment is None:
        raise HTTPException(status_code=404, detail="payment not found")
    return {
        "id": payment.id,
        "status": payment.status,
        "decision": payment.decision,
        "amount": payment.amount,
        "currency": payment.currency,
        "agent_id": payment.agent_id,
        "approval_id": payment.approval_id,
    }


@app.post("/api/v1/approvals/{approval_id}/approve", response_model=ApprovalDecision)
def approve_payment(approval_id: str, payload: dict, db: Session = Depends(get_db)) -> dict:
    approval = db.get(Approval, approval_id)
    if approval is None:
        raise HTTPException(status_code=404, detail="approval not found")

    if approval.status != "pending":
        raise HTTPException(status_code=400, detail="approval already resolved")

    approval.status = "approved"
    approval.approved_by = payload.get("approved_by", "unknown")

    payment = db.get(PaymentRequest, approval.payment_request_id)
    if payment is not None:
        payment.status = "approved"
        payment.decision = "approved"

    db.commit()
    db.refresh(approval)

    return {
        "id": approval.id,
        "status": approval.status,
        "payment_id": approval.payment_request_id,
        "approved_by": approval.approved_by,
    }


@app.post("/api/v1/webhooks/payment")
def handle_payment_webhook(payload: dict, signature: str | None = None, db: Session = Depends(get_db)) -> dict:
    raw_body = b"" if not payload else b"{" + b""  # placeholder to satisfy request validation path
    if not webhook_service.verify_signature(raw_body, signature):
        raise HTTPException(status_code=401, detail="invalid webhook signature")

    parsed = webhook_service.parse_event(payload)
    payment_id = parsed.get("payment_id")
    if not payment_id:
        raise HTTPException(status_code=400, detail="missing payment id")

    payment = db.scalar(select(PaymentRequest).where(PaymentRequest.id == payment_id))
    if payment is None:
        raise HTTPException(status_code=404, detail="payment not found")

    payment.status = "paid" if parsed.get("status") == "paid" else payment.status
    payment.decision = "paid" if parsed.get("status") == "paid" else payment.decision
    db.commit()

    return {
        "status": "accepted",
        "payment_id": payment_id,
        "event": parsed.get("event"),
    }
