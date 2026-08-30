from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_agent_list_and_policy_update() -> None:
    create = client.post("/api/v1/agents", json={"name": "Ops Agent"})
    agent_id = create.json()["id"]

    policy = client.put(
        f"/api/v1/agents/{agent_id}/policy",
        json={
            "monthly_limit": 15000,
            "auto_approve_limit": 600,
            "max_transaction": 2500,
            "allowed_categories": ["software", "cloud"],
            "blocked_categories": ["gambling"],
        },
    )

    assert create.status_code == 201
    assert policy.status_code == 200
    assert policy.json()["monthly_limit"] == 15000

    listing = client.get("/api/v1/agents")
    assert listing.status_code == 200
    payload = listing.json()
    assert any(item["id"] == agent_id for item in payload["data"])


def test_human_approval_flow() -> None:
    create = client.post("/api/v1/agents", json={"name": "Review Agent"})
    agent_id = create.json()["id"]

    client.put(
        f"/api/v1/agents/{agent_id}/policy",
        json={
            "monthly_limit": 10000,
            "auto_approve_limit": 500,
            "max_transaction": 2000,
            "allowed_categories": ["software", "cloud", "api"],
            "blocked_categories": ["gambling", "crypto"],
        },
    )

    payment = client.post(
        f"/api/v1/agents/{agent_id}/payments/requests",
        json={
            "amount": 750,
            "currency": "INR",
            "merchant": "Supabase",
            "reason": "Production database",
            "category": "software",
        },
    )

    assert payment.status_code == 200
    body = payment.json()
    assert body["decision"] == "human_approval"
    assert "approval_id" in body

    approval_id = body["approval_id"]
    approve = client.post(f"/api/v1/approvals/{approval_id}/approve", json={"approved_by": "user_123"})
    assert approve.status_code == 200
    assert approve.json()["status"] == "approved"

    status = client.get(f"/api/v1/payments/requests/{body['id']}")
    assert status.status_code == 200
    assert status.json()["status"] == "approved"
