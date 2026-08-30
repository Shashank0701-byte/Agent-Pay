from app.providers.mock_provider import MockPaymentProvider


def test_mock_provider_create_and_capture() -> None:
    provider = MockPaymentProvider()
    order = provider.create_order(1500, "INR", "Supabase", {"task_id": "t-123"})

    assert order["status"] == "created"
    assert order["amount"] == 1500

    result = provider.capture(order["order_id"])
    assert result["status"] == "captured"

    assert provider.verify_webhook({"event": "paid"}, "sig_123") is True
