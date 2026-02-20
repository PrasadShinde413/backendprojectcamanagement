import requests
from django.conf import settings
from .base import SMSProvider
import logging

logger = logging.getLogger(__name__)


class Fast2SMSProvider(SMSProvider):
    """Fast2SMS Implementation - Free SMS Provider for India"""
    
    BASE_URL = "https://www.fast2sms.com/api/send"
    
    def __init__(self):
        self.api_key = settings.FAST2SMS_API_KEY
        self.sender_id = getattr(settings, 'FAST2SMS_SENDER_ID', 'CAFRM')
        self.route = getattr(settings, 'FAST2SMS_ROUTE', '2')
        # Mock mode for testing (disable in production)
        self.mock_mode = getattr(settings, 'SMS_MOCK_MODE', False)
    
    def _format_phone(self, phone_number):
        """Format phone number to 10 digits (remove +, spaces, etc)"""
        phone = str(phone_number).replace('+', '').replace(' ', '').replace('-', '')
        
        # If starts with 91 (India code), remove it
        if len(phone) == 12 and phone.startswith('91'):
            phone = phone[2:]
        
        # Ensure it's 10 digits and starts with valid digit (6-9 for India)
        if len(phone) == 10 and phone[0] in ['6', '7', '8', '9']:
            return phone
        
        return None
    
    def send_sms(self, phone_number, message):
        """Send single SMS via Fast2SMS"""
        try:
            phone = self._format_phone(phone_number)
            
            if not phone:
                return {
                    'success': False,
                    'message_id': None,
                    'error': f'Invalid phone format: {phone_number}'
                }
            
            # Mock mode for testing
            if self.mock_mode:
                logger.info(f"[MOCK SMS] To: {phone}, Message: {message}")
                return {
                    'success': True,
                    'message_id': f'MOCK-{phone}-{hash(message) % 10000}',
                    'error': None
                }
            
            headers = {
                'authorization': self.api_key,
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            payload = {
                'message': message[:160],  # SMS limit is 160 chars
                'language': 'english',
                'route': self.route,
                'numbers': phone,
                'sender_id': self.sender_id
            }
            
            logger.info(f"[FAST2SMS] Sending to: {phone}, Route: {self.route}, SenderID: {self.sender_id}")
            
            response = requests.post(self.BASE_URL, data=payload, headers=headers, timeout=10)
            result = response.json()
            
            logger.info(f"[FAST2SMS] Response: {result}")
            
            if result.get('return'):
                logger.info(f"[FAST2SMS SUCCESS] Message ID: {result.get('request_id')}")
                return {
                    'success': True,
                    'message_id': result.get('request_id'),
                    'error': None
                }
            else:
                error_msg = result.get('message', 'Unknown error')
                logger.error(f"[FAST2SMS FAILED] Error: {error_msg}, Response: {result}")
                return {
                    'success': False,
                    'message_id': None,
                    'error': error_msg
                }
        
        except requests.exceptions.Timeout:
            logger.error(f"[FAST2SMS ERROR] Request timeout for phone: {phone_number}")
            return {
                'success': False,
                'message_id': None,
                'error': 'Request timeout'
            }
        except requests.exceptions.ConnectionError as e:
            logger.error(f"[FAST2SMS ERROR] Connection error for phone: {phone_number}, Error: {str(e)}")
            return {
                'success': False,
                'message_id': None,
                'error': f'Connection error - {str(e)}'
            }
        except Exception as e:
            logger.error(f"[FAST2SMS ERROR] Unexpected error for phone: {phone_number}, Error: {str(e)}")
            return {
                'success': False,
                'message_id': None,
                'error': str(e)
            }
    
    def send_bulk_sms(self, phone_numbers, message):
        """Send bulk SMS to multiple numbers"""
        details = []
        sent = 0
        failed = 0
        
        for phone in phone_numbers:
            result = self.send_sms(phone, message)
            details.append({
                'phone': phone,
                'success': result['success'],
                'error': result['error']
            })
            
            if result['success']:
                sent += 1
            else:
                failed += 1
        
        return {
            'sent': sent,
            'failed': failed,
            'details': details
        }
