"""Strict source control values. Unknown is never an implied permission/denial."""

def boolean(value):
    if isinstance(value, bool):
        return value
    if type(value) in (int, float) and value in (0, 1):
        return bool(value)
    if isinstance(value, str):
        return {'true': True, 'false': False, '1': True, '0': False}.get(value.strip().casefold())
    return None


def control_state(category, data):
    if data.get('_state')=='UNKNOWN': return 'UNKNOWN'
    fields = {'enabled': False, 'disabled': True} if category == 'DATA_FLOW' else {
        'restore_allowed': False, 'eligible': False, 'restore_blocked': True}
    values = []
    for key, inverse in fields.items():
        if key in data:
            value = boolean(data[key])
            if value is None:
                return 'UNKNOWN'
            values.append(not value if inverse else value)
    if category == 'BACKUP_ARCHIVE' and 'decision' in data:
        value = {'allow': True, 'deny': False}.get(str(data['decision']).strip().casefold())
        if value is None:
            return 'UNKNOWN'
        values.append(value)
    explicit = data.get('result') if 'record_type' in data else data.get('_state')
    allowed = {'ACTIVE': True, 'DISABLED' if category == 'DATA_FLOW' else 'BLOCKED': False}
    if explicit in allowed:
        values.append(allowed[explicit])
    if not values or len(set(values)) != 1:
        return 'UNKNOWN'
    return 'ACTIVE' if values[0] else ('DISABLED' if category == 'DATA_FLOW' else 'BLOCKED')
