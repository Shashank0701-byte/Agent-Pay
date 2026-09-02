import hashlib
import hmac

from app.providers.base import PaymentProvider


class RazorpayProvider(PaymentProvider):
    def __init__(self, key_id: str, key_secret: str):
        self.key_id = key_id
        self.key_secret = key_secret

    def create_order(self, amount: int, currency: str, merchant: str, metadata: dict | None = None):
        return {
            "id": f"razorpay_order_{hash(str(amount) + currency + merchant + str(metadata or {}))}",
            "amount": amount,
            "currency": currency,
            "merchant": merchant,
            "status": "created",
            "metadata": metadata or {},
            "key_id": self.key_id,
        }

    def capture(self, order_id: str):
        return {"order_id": order_id, "status": "captured"}

    def verify_webhook(self, payload: dict, signature: str) -> bool:
        if not payload or not signature:
            return False

        expected = hmac.new(
            self.key_secret.encode("utf-8"),
            payload.get("raw_body", "").encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(signature, expected)
