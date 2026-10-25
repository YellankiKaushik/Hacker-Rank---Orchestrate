"""Internal authorization provenance; never an additional submission CSV field."""
from dataclasses import dataclass,asdict
import re
from .intent import deletion_intent,AmbiguousIntent


@dataclass(frozen=True)
class IntentResolution:
    decision: bool
    method: str
    original_text: str
    quote: str
    validation: str
    confidence: str


def independently_supported(text):
    """Conservative contextual check, separate from model schema/quote validation.

    Only narrowly understood paraphrases may bridge deterministic abstention.
    Arbitrary languages/ambiguous requests still abstain. Model confidence alone
    cannot authorize deletion or establish a non-deletion request.
    """
    t=text.casefold().strip()
    # Anchored full-request templates prevent quote selection from hiding intent.
    if re.fullmatch(r'i want every link between my identity and this service severed permanently[.!]?',t):
        return True
    if re.fullmatch(r'(?:please )?(?:freeze|suspend) my account temporarily[.!]?',t):
        return False
    return None


def validated_decision(text,resolution=None):
    try:
        decision=deletion_intent(text)
    except AmbiguousIntent:
        if not isinstance(resolution,IntentResolution): raise
        if (resolution.original_text!=text or resolution.method!='AI' or
                resolution.validation!='VERIFIED' or resolution.confidence!='LIMITED' or
                not resolution.quote or resolution.quote not in text or type(resolution.decision) is not bool or
                independently_supported(text) is not resolution.decision):
            raise AmbiguousIntent('Intent resolution lacks independent contextual support')
        return resolution.decision
    if resolution is not None and (resolution.original_text!=text or resolution.decision is not decision):
        raise AmbiguousIntent('Intent provenance contradicts original request')
    return decision


def resolve(text,ai=None):
    try:
        return IntentResolution(deletion_intent(text),'DETERMINISTIC',text,text,'VERIFIED','HIGH')
    except AmbiguousIntent:
        decision=ai.classify(text) if ai else None
        value=getattr(ai,'last_result',None)
        if type(decision) is not bool or not isinstance(value,dict):
            raise AmbiguousIntent('Request requires language/intent review')
        resolution=IntentResolution(decision,'AI',text,value.get('quote',''),'VERIFIED','LIMITED')
        validated_decision(text,resolution)
        return resolution


def to_dict(resolution):
    return asdict(resolution)
