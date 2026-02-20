from abc import ABC, abstractmethod


class SMSProvider(ABC):
    """Base SMS provider interface"""
    
    @abstractmethod
    def send_sms(self, phone_number, message):
        """Send SMS to single number
        
        Returns: {
            'success': bool,
            'message_id': str or None,
            'error': str or None
        }
        """
        pass
    
    @abstractmethod
    def send_bulk_sms(self, phone_numbers, message):
        """Send SMS to multiple numbers
        
        Returns: {
            'sent': int,
            'failed': int,
            'details': [{'phone': str, 'success': bool, 'error': str}]
        }
        """
        pass
