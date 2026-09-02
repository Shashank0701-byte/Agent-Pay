from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_request_id_header_is_returned() -> None:
    response = client.get("/health", headers={"X-Request-ID": "req-123"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "req-123"
