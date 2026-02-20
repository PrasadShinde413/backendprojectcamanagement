import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ca_firm.settings')
django.setup()

import json
from rest_framework.test import APIRequestFactory
from master.sms_views import SendBulkSMSAPIView
from userauth.models import User

print("\n" + "="*60)
print("TESTING SEND-BULK SMS API ENDPOINT")
print("="*60)

# Create factory
factory = APIRequestFactory()

# Create POST request
request_data = {
    "message": "Assignment deadline extended to Feb 28",
    "recipient_type": "employees",
    "recipients": [1, 2]
}

print(f"\nRequest: {json.dumps(request_data, indent=2)}")

# Create request
request = factory.post('/api/sms/send-bulk/', request_data, format='json')

# Call API
view = SendBulkSMSAPIView.as_view()
response = view(request)

print(f"\nResponse Status: {response.status_code}")
print(f"Response Data: {json.dumps(response.data, indent=2)}")

print("\n" + "="*60)
if response.status_code == 201 and response.data.get('sent_count', 0) > 0:
    print("✓✓ API WORKING - SMS SENT SUCCESSFULLY! ✓✓")
else:
    print(f"✗ Issue with API response")
print("="*60 + "\n")
