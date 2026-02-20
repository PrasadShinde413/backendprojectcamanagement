#!/usr/bin/env python
"""Test SMS API with mock mode enabled"""

import requests
import json

# Test URL
url = "http://127.0.0.1:8000/api/sms/send-bulk/"

# Request data
data = {
    "message": "Assignment deadline extended to Feb 28",
    "recipient_type": "employees",
    "recipients": [1]
}

# Send request
headers = {
    'Content-Type': 'application/json'
}

print(f"Testing SMS API at {url}")
print(f"Request data: {json.dumps(data, indent=2)}")
print("-" * 50)

try:
    response = requests.post(url, json=data, headers=headers, timeout=30)
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
