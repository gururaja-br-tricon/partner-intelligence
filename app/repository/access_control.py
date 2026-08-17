from enum import Enum


class Domain(str, Enum):
    PARTNER = "partner"
    MARKET = "market"
    EVENT = "event"
    GTM = "gtm"


