from .models import normalize, timestamp


class IdentityGraph:
    def __init__(self, identities, history):
        self.identities = {r['user_id']: r for r in identities}
        self.history = history

    def aliases(self, cutoff):
        aliases = {uid: {normalize(uid)} for uid in self.identities}
        for uid, row in self.identities.items():
            # Future snapshots cannot introduce a future-only identifier.
            if timestamp(row['updated_at']) <= cutoff:
                aliases[uid].update(normalize(row[k]) for k in ('email','phone','email_hash') if row[k])
        for row in self.history:
            if timestamp(row['event_time']) <= cutoff:
                aliases.setdefault(row['user_id'], {normalize(row['user_id'])}).update(
                    normalize(row[k]) for k in ('old_value','new_value') if row[k])
        return aliases

    def resolve(self, email, cutoff):
        aliases = self.aliases(cutoff)
        matches = [uid for uid, keys in aliases.items() if normalize(email) in keys]
        if len(matches) != 1:
            raise ValueError(f'Identity resolution requires exactly one subject; found {len(matches)}')
        return matches[0], aliases[matches[0]]
