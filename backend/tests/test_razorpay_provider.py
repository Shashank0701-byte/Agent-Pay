from app.providers.razorpay_provider import RazorpayProvider


def test_razorpay_provider_order_and_webhook_verification() -> None:
    provider = RazorpayProvider("rzp_test_key", "test_secret")

    order = provider.create_order(1500, "INR", "Supabase", {"task_id": "task_123"})
    assert order["amount"] == 1500
    assert order["currency"] == "INR"
    assert order["status"] == "created"

    result = provider.capture(order["id"])
    assert result["status"] == "captured"

    payload = {"raw_body": "hello"}
    signature = ""
    assert provider.verify_webhook(payload, signature) is False
