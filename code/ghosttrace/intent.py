import re
import unicodedata


class AmbiguousIntent(ValueError):
    pass


def deletion_intent(text):
    """High-confidence multilingual intent. Unsupported language fails explicitly."""
    t = unicodedata.normalize('NFKC', text).casefold().replace('’', "'")
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
    positive = r'\b(?:delet\w*|eras\w*|elimin\w*|borr\w*|supprim\w*|suppression|exclus[aã]o|excluir|apagar|losch\w*|lösch\w*)\b|削除|删除|刪除|삭제|حذف|मिटा'
    if re.search(positive, t) or re.search(r'(?:remove|close|closed|closure).*(?:account|profile|personal|data)|account.*(?:closed|removed)', t):
        return True
    if re.search(r'remove (?:that|the) search result|remove records|profile is gone|records cannot identify me',t):
        return True
    if re.search(r'(?:purge|destroy|dispose of).*(?:account|profile|personal (?:data|information))|withdraw.*consent.*retain.*personal.*dispose',t):
        return True
    if any(re.search(p, t) for p in negatives[4:]) or re.search(r'marketing lists only|information request|login|surname|mobile number|email address.*continue', t):
        return False
    raise AmbiguousIntent('Request requires language/intent review')
