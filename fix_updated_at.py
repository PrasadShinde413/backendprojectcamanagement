import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ca_firm.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    # Update updated_at to have default value
    print("Adding default for updated_at in sms_logs...")
    try:
        cursor.execute("ALTER TABLE sms_logs MODIFY updated_at DATETIME(6) DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)")
        print("✓ updated_at now has default value")
    except Exception as e:
        print(f"Error: {e}")
    
    # Check columns
    cursor.execute("SHOW COLUMNS FROM sms_logs WHERE Field='updated_at'")
    result = cursor.fetchone()
    if result:
        print(f"✓ Verified: {result}")
