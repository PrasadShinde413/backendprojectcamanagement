import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ca_firm.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    # Check SMSLog structure
    cursor.execute("SHOW COLUMNS FROM sms_logs")
    columns = cursor.fetchall()
    print("SMSLog columns:")
    for col in columns:
        print(f"  - {col}")
