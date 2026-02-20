import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ca_firm.settings')
django.setup()

from userauth.models import User

print("\n" + "="*60)
print("CHECKING STORED PHONE NUMBERS")
print("="*60)

users = User.objects.filter(id__in=[1, 2])

for user in users:
    print(f"\nUser ID {user.id}: {user.full_name}")
    print(f"  Phone: {user.phone_no}")
    
    # Check format
    phone = str(user.phone_no).replace('+', '').replace(' ', '').replace('-', '')
    
    if len(phone) == 12 and phone.startswith('91'):
        phone = phone[2:]
    
    print(f"  Format check: {phone}")
    
    if len(phone) == 10 and phone[0] in ['6', '7', '8', '9']:
        print(f"  ✓ Format OK for SMS")
    else:
        print(f"  ✗ Invalid format - needs to be 10 digits starting with 6-9")

print("\n" + "="*60)
print("CORRECT FORMAT EXAMPLES:")
print("="*60)
print("✓ 9876543210 - Correct (10 digits)")
print("✓ +919876543210 - Will be converted to 9876543210")
print("✓ 91-9876543210 - Will be converted to 9876543210")
print("✗ 123456789 - Invalid (9 digits)")
print("✗ 1234567890 - Invalid (starts with 1)")
print("="*60 + "\n")
