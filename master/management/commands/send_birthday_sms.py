from django.core.management.base import BaseCommand
from django.utils import timezone
from master.sms.service import SMSService


class Command(BaseCommand):
    help = 'Send birthday SMS to employees/clients with birthdays today'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('🎂 Birthday SMS Service Started...'))
        
        sms_service = SMSService()
        result = sms_service.send_birthday_sms_today()
        
        if result['success']:
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Birthday SMS sent successfully!\n"
                    f"   Sent: {result['sent_count']} SMS\n"
                    f"   Failed: {result['failed_count']} SMS\n"
                    f"   SMS ID: {result['sms_id']}"
                )
            )
        else:
            self.stdout.write(self.style.WARNING(f"⏭️  {result['message']}"))
