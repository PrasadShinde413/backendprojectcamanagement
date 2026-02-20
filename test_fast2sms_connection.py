#!/usr/bin/env python
"""Test Fast2SMS API connectivity and SMS sending"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, r'c:\AjayProject\CA\ca_firm_16Feb')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ca_firm.settings')
django.setup()

from django.conf import settings
from master.sms.providers.fast2sms import Fast2SMSProvider
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

print("=" * 70)
print("FAST2SMS CONNECTION TEST")
print("=" * 70)

# Check settings
print(f"\n1. CHECKING SETTINGS:")
print(f"   SMS_MOCK_MODE: {settings.SMS_MOCK_MODE}")
print(f"   SMS_PROVIDER: {settings.SMS_PROVIDER}")
print(f"   FAST2SMS_API_KEY: {settings.FAST2SMS_API_KEY[:20]}***")
print(f"   FAST2SMS_SENDER_ID: {settings.FAST2SMS_SENDER_ID}")

# Initialize provider
print(f"\n2. INITIALIZING PROVIDER:")
provider = Fast2SMSProvider()
print(f"   ✓ Provider initialized")
print(f"   Mock Mode: {provider.mock_mode}")
print(f"   Route: {provider.route}")

# Test phone formatting
print(f"\n3. TESTING PHONE FORMATTING:")
test_phones = ['7028405502', '07028405502', '+917028405502', '9359418275']
for phone in test_phones:
    formatted = provider._format_phone(phone)
    status = "✓ Valid" if formatted else "✗ Invalid"
    formatted_str = formatted if formatted else "None"
    print(f"   {phone:20} → {formatted_str:15} {status}")

# Test SMS sending (REAL - not mock)
print(f"\n4. TESTING REAL SMS SENDING TO: 7028405502")
print(f"   Message: 'Test SMS from CA System'")
print(f"   This will attempt to send a REAL SMS if internet connectivity is available")
print()

result = provider.send_sms('7028405502', 'Test SMS from CA System')

print(f"\n   RESULT:")
print(f"   Success: {result['success']}")
print(f"   Message ID: {result['message_id']}")
print(f"   Error: {result['error']}")

# Test with user phone
print(f"\n5. TESTING WITH YOUR USER PHONE:")
from userauth.models import User
try:
    user1 = User.objects.get(id=1)
    print(f"   User: {user1.full_name}")
    print(f"   Phone: {user1.phone_no}")
    
    result = provider.send_sms(user1.phone_no, 'Assignment deadline extended to Feb 28')
    print(f"\n   RESULT:")
    print(f"   Success: {result['success']}")
    print(f"   Message ID: {result['message_id']}")
    print(f"   Error: {result['error']}")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
