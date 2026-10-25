"""Data-driven policy actions and explicit condition checks."""
from .adapters import identifying
from .models import timestamp
from .controls import boolean


def attachment_ownership(data):
    """A subject selector proves association; sole ownership needs its own witness."""
    if 'shared_subjects' in data:
        owners=data['shared_subjects']
        if not isinstance(owners,list) or not owners or any(not isinstance(v,str) or not v.strip() for v in owners):
            return 'UNKNOWN'
        return 'SHARED' if len(set(owners))>1 else 'SOLE'
    details=data.get('_link_details','').casefold()
    if 'belongs only to' in details and 'no other subject is linked' in details:
        return 'SOLE'
    if 'sole_owner' in data:
        value=boolean(data['sole_owner'])
        if value is True: return 'SOLE'
    return 'UNKNOWN'


class Policy:
    def __init__(self, rules):
        self.rules = {r['data_category']:r for r in rules}
        supported = {'Always','Conversation contains shared customer, agent, or order context that must be retained',
            'Attachment belongs only to the deletion subject','Record is still attributable to a user',
            'Log contains a user email address','Record is within the supplied retention period',
            'A supplied legal hold is active','Restore access can be blocked',
            'Account is deleted and only a stable internal user_id is needed to preserve references to retained records'}
        if any(r['condition'] not in supported for r in rules):
            raise ValueError('Unrecognized policy condition; requires explicit implementation')

    def action(self, fact, cutoff):
        if fact.category=='DATA_FLOW': return 'DISABLE'
        if fact.category not in self.rules:
            raise ValueError(f'Unrecognized category: {fact.category}')
        rule = self.rules[fact.category]
        action = rule['required_action']
        data = fact.data
        if fact.category=='SECURITY_AUDIT_LOG':
            if 'retention_active' in data:
                active=boolean(data['retention_active'])
                if active is None: return 'UNKNOWN'
                if not active: return 'DELETE'
            until = data.get('retention_until') or data.get('retained_until')
            if until:
                try:
                    if timestamp(until) < cutoff: return 'DELETE'
                except (ValueError,TypeError): return 'UNKNOWN'
        elif fact.category=='LEGAL_HOLD_RECORD':
            if 'legal_hold_active' in data and boolean(data['legal_hold_active']) is None:
                return 'UNKNOWN'
            until = data.get('retained_until')
            if until:
                try:
                    if timestamp(until) < cutoff: return 'DELETE'
                except (ValueError,TypeError): return 'UNKNOWN'
            if 'legal_hold_active' in data and boolean(data['legal_hold_active']) is False:
                return 'DELETE'
        elif fact.category=='SUPPORT_ATTACHMENT':
            ownership=attachment_ownership(data)
            return {'SOLE':'DELETE','SHARED':'REDACT','UNKNOWN':'UNKNOWN'}[ownership]
        return action

    def violation(self, fact, cutoff):
        action = self.action(fact,cutoff)
        state = fact.state
        if state == 'UNKNOWN' or action == 'UNKNOWN':
            return None
        if fact.category=='BACKUP_ARCHIVE':
            return state=='ACTIVE'
        return {'DELETE':state!='ABSENT', 'REDACT':state not in ('REDACTED','ABSENT'),
                'ANONYMIZE':state not in ('ANONYMIZED','ABSENT'), 'RETAIN':state=='ABSENT',
                'DISABLE':state=='ACTIVE'}[action]

    def operations(self, fact, cutoff):
        if fact.category in ('ACCOUNT_TOMBSTONE','SUPPORT_MESSAGE') and fact.state=='ABSENT':
            raise ValueError('Required retained context/reference is absent; no permitted restoration operation is defined')
        action = self.action(fact,cutoff)
        if fact.category=='BACKUP_ARCHIVE': return ('REPORT_RESTORE_RISK','BLOCK_RESTORE','VERIFY_RESTORE_BLOCKED')
        return {
            'DELETE':('REPORT_REMAINING_RECORD','DELETE_RECORD','VERIFY_RECORD_ABSENT'),
            'REDACT':('REPORT_EXPOSED_PII','REDACT_RECORD','VERIFY_RECORD_REDACTED'),
            'ANONYMIZE':('REPORT_EXPOSED_PII','ANONYMIZE_RECORD','VERIFY_RECORD_ANONYMIZED'),
            'RETAIN':(None,None,'VERIFY_RECORD_PRESENT'),
            'DISABLE':('REPORT_ACTIVE_DATA_FLOW','DISABLE_DATA_FLOW','VERIFY_DATA_FLOW_DISABLED'),
        }[action]
