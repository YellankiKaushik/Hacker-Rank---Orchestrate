"""Data-driven policy actions and explicit condition checks."""
from .adapters import identifying
from .models import timestamp


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
            until = data.get('retention_until') or data.get('retained_until')
            if until and timestamp(until) < cutoff:
                return 'DELETE'
        elif fact.category=='LEGAL_HOLD_RECORD':
            until = data.get('retained_until')
            if until and timestamp(until) < cutoff:
                return 'DELETE'
            if data.get('legal_hold_active') is False:
                return 'DELETE'
        elif fact.category=='SUPPORT_ATTACHMENT' and data.get('shared_subjects'):
            return 'REDACT'
        return action

    def violation(self, fact, cutoff):
        action = self.action(fact,cutoff)
        state = fact.state
        if state == 'UNKNOWN':
            return None
        if fact.category=='BACKUP_ARCHIVE':
            return state=='ACTIVE'
        return {'DELETE':state!='ABSENT', 'REDACT':state not in ('REDACTED','ABSENT'),
                'ANONYMIZE':state not in ('ANONYMIZED','ABSENT'), 'RETAIN':state=='ABSENT',
                'DISABLE':state=='ACTIVE'}[action]

    def operations(self, fact, cutoff):
        action = self.action(fact,cutoff)
        if fact.category=='BACKUP_ARCHIVE': return ('REPORT_RESTORE_RISK','BLOCK_RESTORE','VERIFY_RESTORE_BLOCKED')
        return {
            'DELETE':('REPORT_REMAINING_RECORD','DELETE_RECORD','VERIFY_RECORD_ABSENT'),
            'REDACT':('REPORT_EXPOSED_PII','REDACT_RECORD','VERIFY_RECORD_REDACTED'),
            'ANONYMIZE':('REPORT_EXPOSED_PII','ANONYMIZE_RECORD','VERIFY_RECORD_ANONYMIZED'),
            'RETAIN':(None,None,'VERIFY_RECORD_PRESENT'),
            'DISABLE':('REPORT_ACTIVE_DATA_FLOW','DISABLE_DATA_FLOW','VERIFY_DATA_FLOW_DISABLED'),
        }[action]
