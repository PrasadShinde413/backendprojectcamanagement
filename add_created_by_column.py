import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ca_firm.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    # Check if created_by_id column exists in sms_messages
    cursor.execute("SHOW COLUMNS FROM sms_messages WHERE Field='created_by_id'")
    if cursor.fetchone():
        print("✓ created_by_id column already exists in sms_messages")
    else:
        print("Adding created_by_id column to sms_messages...")
        try:
            cursor.execute("""
                ALTER TABLE sms_messages 
                ADD COLUMN created_by_id BIGINT NULL
            """)
            # Add foreign key separately
            cursor.execute("""
                ALTER TABLE sms_messages 
                ADD CONSTRAINT fk_sms_messages_created_by 
                FOREIGN KEY (created_by_id) 
                REFERENCES auth_user(id) ON DELETE SET NULL
            """)
            print("✓ created_by_id column and foreign key added successfully")
        except Exception as e:
            print(f"Note: {e}")
    
    # Verify it's there and test query
    try:
        cursor.execute("SHOW COLUMNS FROM sms_messages WHERE Field='created_by_id'")
        result = cursor.fetchone()
        if result:
            print(f"✓ Verified: created_by_id column exists")
        else:
            print("✗ Column still not found")
    except Exception as e:
        print(f"Error verifying: {e}")
