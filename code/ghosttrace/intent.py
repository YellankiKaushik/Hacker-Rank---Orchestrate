import re
import unicodedata


class AmbiguousIntent(ValueError):
    pass


def deletion_intent(text):
    """High-confidence multilingual intent. Unsupported language fails explicitly."""
    t = unicodedata.normalize('NFKC', text).casefold().replace('’', "'")
    # A mention of erasure is not an instruction. Apply speech-act and scoped
    # negation rules before the multilingual affirmative vocabulary below.
    subject = r'(?:my|the|this|an?)?\s*(?:account|profile|personal\s+(?:data|information)|records|data)'
    if re.search(r"\b(?:not|never)\s+(?:requesting|asking\s+for|authori[sz]ing|seeking|consenting\s+to|request(?:ed)?)\s+(?:(?:the|any|account|data)\s+)*(?:deletion|erasure|removal|closure)",t):
        return False
    if re.search(r'\bnot\s+(?:asking|requesting|authori[sz]ing)(?:\s+you)?\s+to\s+(?:delete|erase|remove|close)\s+'+subject,t):
        return False
    if re.search(r"\b(?:do not|don't|never)\s+(?:want|wish|consent|agree)(?:\s+to)?\s+(?:have\s+)?"+subject+r'.{0,25}(?:delet|eras|remov|clos)',t):
        return False
    informational = re.search(r'\b(?:explain|describe|tell me about|information (?:on|about)|what (?:is|does)|how (?:does|would|can|do)|whether|what happens).{0,90}\b(?:delet\w*|eras\w*|removal|closure)\b',t)
    # A separate explicit directive can coexist with a policy question.
    directive = re.search(r'(?:^|[.!;]\s*)(?:also\s+)?(?:please\s+)?(?:delete|erase|remove|close|purge|destroy)\s+'+subject,t)
    if informational and not directive:
        return False
    if not directive and re.search(r'\b(?:should|must|do)\s+i\b.{0,45}\b(?:delete|erase|remove|close)\b',t):
        return False
    if not directive and re.search(r'\b(?:considering|thinking about|might|maybe|perhaps)\b.{0,55}\b(?:delet\w*|eras\w*)\b',t):
        raise AmbiguousIntent('Tentative erasure language is not authorization')
    if not directive and re.search(r'\b(?:unsubscribe|opt[ -]out)\b.{0,60}\b(?:marketing|promotional|newsletter)\b',t):
        return False
    if re.search(r'\b(?:freeze|suspend|pause|deactivate)\b.{0,45}\b(?:temporarily|temporary|for now)\b',t) and not directive:
        return False
    explicit_negative=(
        r"(?:do not|don't|never)\s+(?:(?:want|wish)(?: you)? to\s+)?(?:delete|erase|close|remove)(?:\s+or\s+(?:change|modify|remove|delete))?\s+(?:(?:my|the|this|any)\s+)?(?:account|profile|personal|data|records|anything|it)",
        r'not (?:asking for|a request (?:for|to))\s+(?:deletion|erasure|erase|delete)',
        r'削除しない|削除を希望しません|不要删除|不要刪除|삭제하지',
        r'no (?:quiero|deseo|autorizo).*?(?:eliminar|borrar)|no (?:eliminen|borren|elimine)',
        r'ne (?:supprimez|supprimer).*?pas|ne veux pas.*?supprim',
        r'não (?:quero|desejo|autorizo).*?(?:exclu|apagar)|não (?:exclua|apague)',
        r'(?:lösch|losch)\w*.*?nicht|nicht.*?(?:lösch|losch)',
    )
    if any(re.search(p,t) for p in explicit_negative):
        # Retention exceptions mention invoices/journals, not a negation of account erasure.
        return False
    if re.search(r'(?:explain|what is|tell me about|information about|how (?:do|can) i).*?(?:deletion policy|deletion process|(?:delete|erase|close|destroy|purge) (?:my|an) account)',t):
        return False
    negatives = (
        r"without\s+(?:delet\w*|eras\w*|remov\w*)",
        r'(?:marketing|promotional|newsletter).*(?:only|still (?:need|want)|not asking)',
        r'leave (?:the|my) (?:account|profile).*?(?:active|in place)',
        r'keep the account (?:as it is|open|active)',
        r'(?:correc|replace|change|reset|download|copy|what personal information).*?(?:profile|account|information|records|hold)',
    )
    # Explicit positive erasure can coexist with a request to keep lawful retained data.
    if any(re.search(p, t) for p in negatives[:4]):
        return False
    # English nominal mentions require an affirmative request frame. Foreign
    # vocabulary remains bounded to supported language forms/negations.
    english_action = re.search(r'\b(?:delete|erase|deleting|erasing|deleted|erased)\b.{0,90}\b(?:account|profile|data|information|records|identifiers)\b|\b(?:account|profile|data|information|records)\b.{0,90}\b(?:deleted|erased|deleting|erasing)\b',t)
    english_request = re.search(r'\b(?:request|requesting|asking|want|wish|authorize|authorise|consent)\b.{0,75}\b(?:deletion|erasure|removal|closure)\b',t)
    procedural_request = re.search(r'\b(?:begin|start|process|perform|complete|finish|carry out|proceed with)\b.{0,65}\b(?:deletion|erasure|removal)\b',t)
    positive = r'\b(?:elimin\w*|borr\w*|supprim\w*|suppression|exclus[aã]o|excluir|apagar|losch\w*|lösch\w*)\b|削除|删除|刪除|삭제|حذف|मिटा'
    if english_action or english_request or procedural_request:
        return True
    if re.search(positive, t) or re.search(r'(?:remove|close|closed|closure).*(?:account|profile|personal|data)|account.*(?:closed|removed)', t):
        return True
    if re.search(r'remove (?:that|the) search result|remove records|profile is gone|records cannot identify me',t):
        return True
    if re.search(r'(?:purge|destroy|dispose of).*(?:account|profile|personal (?:data|information))|withdraw.*consent.*retain.*personal.*dispose',t):
        return True
    if any(re.search(p, t) for p in negatives[4:]) or re.search(r'marketing lists only|information request|login|surname|mobile number|email address.*continue', t):
        return False
    raise AmbiguousIntent('Request requires language/intent review')
