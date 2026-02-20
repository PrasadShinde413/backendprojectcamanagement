import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ca_firm.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    # Make phone_number nullable in sms_logs
    print("Making phone_number nullable in sms_logs...")
    try:
        cursor.execute("ALTER TABLE sms_logs MODIFY phone_number VARCHAR(15) NULL")
        print("✓ phone_number now allows NULL values")
    except Exception as e:
        print(f"Error: {e}")
    
    # Check columns
    cursor.execute("SHOW COLUMNS FROM sms_logs WHERE Field='phone_number'")
    result = cursor.fetchone()
    if result:
        print(f"✓ Verified: {result}")
