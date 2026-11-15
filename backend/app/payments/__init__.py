from .base import PaymentProvider, PaymentError, PaymentOrder, PaymentVerification
from .dummy import DummyProvider
from .razorpay import RazorpayProvider
from ..config import settings


def get_provider() -> PaymentProvider:
    """Pick the provider from config. 'dummy' is for local dev and tests only."""
    if settings.payment_provider == "razorpay":
        return RazorpayProvider(settings.razorpay_key_id, settings.razorpay_key_secret,
                                settings.razorpay_webhook_secret)
    return DummyProvider()


__all__ = ["PaymentProvider", "PaymentError", "PaymentOrder", "PaymentVerification",
           "DummyProvider", "RazorpayProvider", "get_provider"]
