import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ca_firm.settings')
django.setup()

from master.sms.service import SMSService
from userauth.models import User

print("\n" + "="*60)
print("TESTING FAST2SMS API WITH ACTUAL USERS")
print("="*60)

# Get users
users = User.objects.filter(id__in=[1, 2])
user_list = list(users)

if not user_list:
    print("No users found!")
else:
    print(f"\nFound {len(user_list)} users:")
    for u in user_list:
        print(f"  - {u.id}: {u.full_name} ({u.phone_no})")
    
    # Test SMS
    print("\nTesting SMS send...")
    try:
        sms_service = SMSService()
        
        # Test sending to these users
        result = sms_service.send_bulk_message(
            recipients=user_list,
            message="Test message from CA Firm",
            message_type='bulk'
        )
        
        print(f"\n✓ SMS sent!")
        print(f"  SMS ID: {result.id}")
        print(f"  Recipients: {result.recipients.count()}")
        print(f"  Sent: {result.sent_count}")
        print(f"  Failed: {result.failed_count}")
        print(f"  Status: {result.status}")
        
        # Check logs for details
        print("\nDetailed logs:")
        for log in result.logs.all():
            print(f"  - {log.recipient.full_name} ({log.recipient_phone}): {log.status}")
            if log.error_message:
                print(f"    Error: {log.error_message}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "="*60)
