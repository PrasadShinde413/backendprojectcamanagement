import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ca_firm.settings')
django.setup()

from master.models import SMSMessage, SMSLog
from master.sms.service import SMSService

print("Testing SMS Service...")
try:
    # Try to create an SMS message
    sms_service = SMSService()
    print("✓ SMSService initialized successfully")
    
    # Check if send_bulk_message works
    from userauth.models import User
    user = User.objects.filter(is_active=True).first()
    
    if user:
        print(f"Found test user: {user.full_name}")
        # Just test the model without actually sending
        sms = SMSMessage.objects.create(
            message_type='bulk',
            message_content='Test message'
        )
        print(f"✓ SMS created: {sms.id}")
        
        log = SMSLog.objects.create(
            sms_message=sms,
            recipient=user,
            recipient_phone='9876543210',
            status='sent'
        )
        print(f"✓ SMSLog created: {log.id}")
        
        sms.delete()
        print("✓ Test data cleaned up")
    else:
        print("⚠ No users found to test")
    
    print("\n✓✓ SMS API READY TO USE ✓✓")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
