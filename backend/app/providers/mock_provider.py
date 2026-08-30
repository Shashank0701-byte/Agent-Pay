from app.providers.base import PaymentProvider


class MockPaymentProvider(PaymentProvider):
    def __init__(self):
        self.orders = {}

    def create_order(self, amount: int, currency: str, merchant: str, metadata: dict | None = None):
        order_id = f"mock_order_{len(self.orders) + 1}"
        self.orders[order_id] = {
            "order_id": order_id,
            "amount": amount,
            "currency": currency,
            "merchant": merchant,
            "metadata": metadata or {},
            "status": "created",
        }
        return self.orders[order_id]

    def capture(self, order_id: str):
        if order_id not in self.orders:
            raise ValueError("order not found")

        self.orders[order_id]["status"] = "captured"
        return {"order_id": order_id, "status": "captured"}

    def verify_webhook(self, payload: dict, signature: str) -> bool:
        return bool(payload) and bool(signature)
