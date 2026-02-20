from django.conf import settings
from django.utils import timezone
from .providers.fast2sms import Fast2SMSProvider


class SMSService:
    """Main SMS service for sending bulk and birthday SMS"""
    
    def __init__(self):
        provider_name = getattr(settings, 'SMS_PROVIDER', 'fast2sms')
        
        if provider_name == 'fast2sms':
            self.provider = Fast2SMSProvider()
        else:
            raise ValueError(f"Unknown SMS provider: {provider_name}")
    
    def send_bulk_message(self, recipients, message, message_type='bulk', created_by=None):
        """
        Send bulk SMS to recipients
        
        Args:
            recipients: List of User objects
            message: SMS message text
            message_type: 'bulk' or 'birthday'
            created_by: User who created this message
        
        Returns: SMSMessage object
        """
        from master.models import SMSMessage, SMSLog
        
        # Create SMSMessage record
        sms_msg = SMSMessage.objects.create(
            message_type=message_type,
            message_content=message,
            created_by=created_by
        )
        sms_msg.recipients.set(recipients)
        
        # Get phone numbers (filter out None/empty)
        phone_numbers = [r.phone_no for r in recipients if r.phone_no]
        
        if not phone_numbers:
            sms_msg.status = 'failed'
            sms_msg.save()
            return sms_msg
        
        # Send via provider
        result = self.provider.send_bulk_sms(phone_numbers, message)
        
        # Create logs for each recipient
        for idx, recipient in enumerate(recipients):
            if idx < len(result['details']):
                detail = result['details'][idx]
                
                SMSLog.objects.create(
                    sms_message=sms_msg,
                    recipient=recipient,
                    recipient_phone=recipient.phone_no,
                    status='sent' if detail['success'] else 'failed',
                    error_message=detail['error'] if not detail['success'] else None
                )
        
        # Update SMSMessage
        sms_msg.sent_count = result['sent']
        sms_msg.failed_count = result['failed']
        sms_msg.status = 'sent' if result['sent'] > 0 else 'failed'
        sms_msg.save()
        
        return sms_msg
    
    def get_today_birthdays(self):
        """Get all users with birthdays today"""
        from datetime import datetime
        from userauth.models import User
        
        today = datetime.now().date()
        
        birthday_users = User.objects.filter(
            is_active=True,
            birthdate__month=today.month,
            birthdate__day=today.day
        )
        
        return birthday_users
    
    def send_birthday_sms_today(self):
        """Send birthday SMS to all employees/clients with birthdays today"""
        birthday_users = self.get_today_birthdays()
        
        if not birthday_users.exists():
            return {
                'success': False,
                'message': 'No birthdays today',
                'recipients_count': 0,
                'sent_count': 0
            }
        
        message = getattr(settings, 'BIRTHDAY_SMS_TEMPLATE', 
                         "Happy Birthday! Wishing you a wonderful day ahead.")
        
        sms_msg = self.send_bulk_message(
            recipients=list(birthday_users),
            message=message,
            message_type='birthday',
            created_by=None
        )
        
        return {
            'success': True,
            'message': f'Birthday SMS sent successfully',
            'sms_id': sms_msg.id,
            'recipients_count': sms_msg.recipients.count(),
            'sent_count': sms_msg.sent_count,
            'failed_count': sms_msg.failed_count
        }
