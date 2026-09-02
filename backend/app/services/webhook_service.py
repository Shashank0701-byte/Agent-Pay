from __future__ import annotations

import hashlib
import hmac
from typing import Any


class WebhookVerificationError(Exception):
    pass


class WebhookService:
    def __init__(self, webhook_secret: str):
        self.webhook_secret = webhook_secret

    def verify_signature(self, raw_body: bytes, signature: str | None) -> bool:
        if not signature:
            return False
        expected = hmac.new(
            self.webhook_secret.encode("utf-8"),
            raw_body,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(signature, expected)

    def parse_event(self, payload: dict[str, Any]) -> dict[str, Any]:
        event = payload.get("event", "")
        return {
            "event": event,
            "payment_id": payload.get("payment_id") or payload.get("id"),
            "status": payload.get("status"),
        }
