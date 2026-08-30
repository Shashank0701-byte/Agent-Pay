from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_create_agent() -> None:
    response = client.post("/api/v1/agents", json={"name": "DevOps Agent"})

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "DevOps Agent"
    assert data["status"] == "active"
    assert "api_key" in data
    assert data["api_key"].startswith("ap_")


def test_policy_decision_auto_approve() -> None:
    agent_response = client.post("/api/v1/agents", json={"name": "Budget Agent"})
    agent_id = agent_response.json()["id"]

    policy_response = client.put(
        f"/api/v1/agents/{agent_id}/policy",
        json={
            "monthly_limit": 10000,
            "auto_approve_limit": 500,
            "max_transaction": 2000,
            "allowed_categories": ["software", "cloud", "api"],
            "blocked_categories": ["gambling", "crypto"],
        },
    )
    assert policy_response.status_code == 200

    decision = client.post(
        f"/api/v1/agents/{agent_id}/payments/requests",
        json={
            "amount": 300,
            "currency": "INR",
            "merchant": "Supabase",
            "reason": "Production database",
            "category": "software",
        },
    )

    assert decision.status_code == 200
    assert decision.json()["decision"] == "auto_approved"
