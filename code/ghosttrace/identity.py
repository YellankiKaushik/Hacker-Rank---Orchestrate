from .models import normalize, timestamp,identifier_keys


class IdentityGraph:
    def __init__(self, identities, history):
        self.identities = {r['user_id']: r for r in identities}
        self.history = history
        self._cache={}

    def aliases(self, cutoff):
        if cutoff in self._cache: return self._cache[cutoff]
        aliases = {uid: {normalize(uid)} for uid in self.identities}
        for uid, row in self.identities.items():
            # Future snapshots cannot introduce a future-only identifier.
            if timestamp(row['updated_at']) <= cutoff:
                for field in ('email','phone','email_hash'):
                    if row[field]: aliases[uid].update(identifier_keys(row[field]))
        for row in self.history:
            if timestamp(row['event_time']) <= cutoff:
                for field in ('old_value','new_value'):
                    if row[field]: aliases.setdefault(row['user_id'],{normalize(row['user_id'])}).update(identifier_keys(row[field]))
        self._cache[cutoff]=aliases
        return aliases

    def resolve(self, email, cutoff):
        aliases = self.aliases(cutoff)
        matches = [uid for uid, keys in aliases.items() if normalize(email) in keys]
        if len(matches) != 1:
            raise ValueError(f'Identity resolution requires exactly one subject; found {len(matches)}')
        return matches[0], aliases[matches[0]]
