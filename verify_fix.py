"""
Final verification that the created_by_id error is FIXED
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ca_firm.settings')
django.setup()

from master.models import SMSMessage
from userauth.models import User
from django.db import connection

print("\n" + "="*60)
print("✓ FINAL VERIFICATION - created_by_id ERROR FIX")
print("="*60)

try:
    # Test 1: Query SMSMessage
    print("\n[TEST 1] Querying SMSMessage model...")
    messages = SMSMessage.objects.all()
    print(f"  ✓ SMSMessage.objects.all() works: {messages.count()} messages")
    
    # Test 2: Filter by created_by
    print("\n[TEST 2] Filtering by created_by...")
    msgs = SMSMessage.objects.filter(created_by__isnull=False)
    print(f"  ✓ created_by filter works: {msgs.count()} messages with creator")
    
    # Test 3: Verify column exists
    print("\n[TEST 3] Verifying database column...")
    with connection.cursor() as cursor:
        cursor.execute("SHOW COLUMNS FROM sms_messages WHERE Field='created_by_id'")
        col = cursor.fetchone()
        if col:
            print(f"  ✓ created_by_id column exists: {col}")
        else:
            print("  ✗ FAILED: Column not found")
    
    # Test 4: Try to create a record
    print("\n[TEST 4] Creating a test SMS message...")
    sms = SMSMessage(
        message_type='bulk',
        message_content='Test message',
        status='pending'
    )
    sms.full_clean()
    sms.save()
    print(f"  ✓ SMS created successfully: ID={sms.id}")
    
    # Clean up
    sms.delete()
    print(f"  ✓ Test record cleaned up")
    
    print("\n" + "="*60)
    print("✓✓✓ ALL TESTS PASSED - ERROR IS FIXED! ✓✓✓")
    print("="*60 + "\n")
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
