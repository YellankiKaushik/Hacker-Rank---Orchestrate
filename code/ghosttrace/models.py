from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
import re


def timestamp(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('Timestamps must specify a timezone')
    return parsed.astimezone(timezone.utc)


def normalize(value: Any) -> str:
    return str(value).strip().casefold()


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
        found.add(normalize(text))
        found.update(normalize(v) for v in re.findall(
            r'[\w.+-]+@[\w.-]+\.[a-zA-Z]+|\buser_\d+\b|\b[a-fA-F0-9]{64}\b', text))
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


@dataclass
class Audit:
    case: dict
    subject: str
    facts: list[Fact]
    status: str
    steps: list[dict]
    issues: list[str] = field(default_factory=list)
