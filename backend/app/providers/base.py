from abc import ABC, abstractmethod


class PaymentProvider(ABC):
    @abstractmethod
    def create_order(self, amount: int, currency: str, merchant: str, metadata: dict | None = None):
        raise NotImplementedError

    @abstractmethod
    def capture(self, order_id: str):
        raise NotImplementedError

    @abstractmethod
    def verify_webhook(self, payload: dict, signature: str) -> bool:
        raise NotImplementedError
