from app.services.webhook_service import WebhookService


def test_webhook_service_verifies_signature() -> None:
    service = WebhookService("secret")
    raw = b"hello"
    signature = ""

    assert service.verify_signature(raw, signature) is False

    import hashlib
    import hmac

    valid_signature = hmac.new(
        b"secret",
        raw,
        hashlib.sha256,
    ).hexdigest()

    assert service.verify_signature(raw, valid_signature) is True


def test_webhook_service_parses_event() -> None:
    service = WebhookService("secret")

    payload = {
        "event": "payment.captured",
        "payment_id": "pay_123",
        "status": "paid",
    }

    parsed = service.parse_event(payload)
    assert parsed["event"] == "payment.captured"
    assert parsed["payment_id"] == "pay_123"
    assert parsed["status"] == "paid"
