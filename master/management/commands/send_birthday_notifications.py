from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime
from userauth.models import User
from master.notification_utils import create_birthday_notifications


class Command(BaseCommand):
    help = 'Check for employee birthdays and send notifications to all users'

    def handle(self, *args, **options):
        today = datetime.now().date()
        
        # Get users with birthday today
        birthday_users = User.objects.filter(
            birthdate__month=today.month,
            birthdate__day=today.day,
            is_active=True
        )
        
        if birthday_users.exists():
            count = 0
            for user in birthday_users:
                create_birthday_notifications(user)
                count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Birthday notifications sent for {user.full_name}'
                    )
                )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n{count} birthday notification(s) sent successfully!'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING('No birthdays today')
            )
