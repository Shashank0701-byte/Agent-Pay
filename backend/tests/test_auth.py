from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_invalid_api_key_is_rejected() -> None:
    create = client.post("/api/v1/agents", json={"name": "Secure Agent"})
    agent_id = create.json()["id"]

    response = client.post(
        f"/api/v1/agents/{agent_id}/payments/requests",
        headers={"Authorization": "Bearer invalid-key"},
        json={
            "amount": 200,
            "currency": "INR",
            "merchant": "Supabase",
            "reason": "db",
            "category": "software",
        },
    )

    assert response.status_code == 401
