import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ca_firm.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    # Check if recipient_phone column exists
    cursor.execute("SHOW COLUMNS FROM sms_logs WHERE Field='recipient_phone'")
    if cursor.fetchone():
        print("✓ recipient_phone column already exists")
    else:
        print("Adding recipient_phone column to sms_logs...")
        try:
            cursor.execute("ALTER TABLE sms_logs ADD COLUMN recipient_phone VARCHAR(15)")
            print("✓ recipient_phone column added successfully")
        except Exception as e:
            print(f"Error: {e}")
    
    # Verify
    cursor.execute("SHOW COLUMNS FROM sms_logs WHERE Field='recipient_phone'")
    result = cursor.fetchone()
    if result:
        print(f"✓ Verified: {result}")
