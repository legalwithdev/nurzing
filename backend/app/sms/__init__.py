from .base import SmsProvider, SmsResult
from .console import ConsoleProvider
from .msg91 import Msg91Provider
from ..config import settings


def get_sms() -> SmsProvider:
    if settings.sms_provider == "msg91" and settings.msg91_authkey:
        return Msg91Provider(settings.msg91_authkey, settings.msg91_sender, settings.msg91_template_id)
    return ConsoleProvider()


__all__ = ["SmsProvider", "SmsResult", "ConsoleProvider", "Msg91Provider", "get_sms"]
