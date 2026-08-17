"""
Single source of truth for domain/role names. Every place that currently
uses bare strings ("partner", "market", "event", "gtm") should import
Domain from here instead — a typo in a string literal fails silently as
"access denied"; a typo referencing Domain.PARTNR fails loudly at import
time, which is what you want for anything access-control-related.

Values are still plain strings under the hood (Domain.PARTNER.value ==
"partner") so JWT payloads, Snowflake ROLES column, and the DB stay
unchanged — this doesn't require a data migration, just consistent
usage going forward.
"""

from enum import Enum


class Domain(str, Enum):
    PARTNER = "partner"
    MARKET = "market"
    EVENT = "event"  # includes MATCHMAKING_DATA per earlier decision
    GTM = "gtm"

    def __str__(self) -> str:
        return self.value


VALID_DOMAINS = frozenset(d.value for d in Domain)
