from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from functools import cached_property
import re


def timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('Timestamps must specify a timezone')
    return parsed.astimezone(timezone.utc)


def normalize(value: Any) -> str:
    return str(value).strip().casefold()


def identifier_keys(value) -> set[str]:
    key=normalize(value)
    result={key} if key else set()
    if re.fullmatch(r'(?:\+|00)[\d ()-]+',key):
        digits=re.sub(r'\D','',key)
        if key.startswith('00'): digits=digits[2:]
        if 8<=len(digits)<=15:
            result.add('phone:+'+digits)
    return result


def strings(value):
    if isinstance(value, dict):
        for v in value.values():
            yield from strings(v)
    elif isinstance(value, list):
        for v in value:
            yield from strings(v)
    elif isinstance(value, str):
        yield value


def tokens(value) -> set[str]:
    """Exact atoms, never substring user_1/user_10 or name-based joins."""
    found = set()
    for text in strings(value):
        found.update(identifier_keys(text))
        found.update(normalize(v) for v in re.findall(
            r'[\w.+-]+@[\w.-]+\.[a-zA-Z]+|\buser_\d+\b|\b[a-fA-F0-9]{64}\b', text))
        for phone in re.findall(r'(?<!\w)\+\d[\d ()-]{6,24}\d(?!\d)',text):
            found.update(identifier_keys(phone))
    return found - {'', 'null', 'none', '[redacted]', 'no direct identifier'}


@dataclass(frozen=True)
class Fact:
    source: str
    captured: datetime
    observed: datetime
    system: str
    resource: str
    category: str
    state: str
    data: dict = field(compare=False)
    scope: str = ''
    locator: str = ''

    def admissible(self, cutoff):
        return self.captured <= cutoff and self.observed <= cutoff

    @property
    def copy_role(self):
        """Typed physical scope, without interpreting incidental text as topology."""
        roles={'customer_profiles_failover_replica':'REPLICA','customer_data_regional_replica':'REPLICA',
               'customer_data_reporting_replica':'REPLICA','customer_data_failover_replica':'REPLICA',
               'customer_data_read_replica':'REPLICA','customer_data_replica_ap_south':'REPLICA',
               'customer_data_replica_eu_west':'REPLICA','customer_data_primary':'PRIMARY',
               'replica':'REPLICA','customer_profiles_primary':'PRIMARY','search_documents_primary':'PRIMARY','primary':'PRIMARY'}
        declared=self.data.get('copy_role')
        return declared if declared in ('PRIMARY','REPLICA') else roles.get(self.scope,'UNKNOWN')

    @cached_property
    def binding_tokens(self):
        # Facts are treated as immutable; source changes require a new hash-checked parse.
        return frozenset(tokens(self.data.get('_bindings',self.data)))


@dataclass
class Audit:
    case: dict
    subject: str
    facts: list[Fact]
    status: str
    steps: list[dict]
    issues: list[str] = field(default_factory=list)
    bindings: dict = field(default_factory=dict)
    coverage_proofs: list = field(default_factory=list)
    intent_resolution: object = None
