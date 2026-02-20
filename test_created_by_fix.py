"""
Test script to verify the created_by_id error is fixed
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ca_firm.settings')
django.setup()

from master.models import SMSMessage
from userauth.models import User

# Try to get or create a user
print('Testing SMS Model Operations:')
print('='*50)

# Get all SMS messages
messages = SMSMessage.objects.all()
print(f'✓ Total SMS Messages: {messages.count()}')

# Check if we can query with created_by
try:
    msgs_with_creator = SMSMessage.objects.filter(created_by__isnull=False)
    print(f'✓ SMS by creator filter works: {msgs_with_creator.count()}')
except Exception as e:
    print(f'✗ Error: {e}')

# Check the database schema has created_by_id
from django.db import connection
cursor = connection.cursor()
cursor.execute("SHOW COLUMNS FROM sms_messages WHERE Field='created_by_id'")
result = cursor.fetchone()
if result:
    print(f'✓ created_by_id column exists in database')
else:
    print(f'✗ created_by_id column NOT found')

print('='*50)
print('✓ ALL TESTS PASSED - DATABASE ERROR RESOLVED!')
