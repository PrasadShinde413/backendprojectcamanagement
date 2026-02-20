"""
Management Command: create_recurring_works

This command automatically creates monthly work entries for all active RecurringWorkAssignment records.
It checks if work already exists for the current month and skips if it does.

Usage:
    python manage.py create_recurring_works       # Creates works for current month
    python manage.py create_recurring_works --month 2024-02-01   # Specific month
    python manage.py create_recurring_works --dry-run            # Preview without creating

Run monthly via cron job or scheduler to automate recurring work generation.
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import datetime, timedelta
import calendar

from master.models import RecurringWorkAssignment, Work


class Command(BaseCommand):
    help = 'Create monthly work entries for all active recurring work assignments'

    def add_arguments(self, parser):
        parser.add_argument(
            '--month',
            type=str,
            help='Process specific month (format: YYYY-MM-01, e.g., 2024-02-01)',
            default=None
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview changes without creating works'
        )

    def handle(self, *args, **options):
        # Determine the target month
        if options['month']:
            try:
                target_date = datetime.strptime(options['month'], '%Y-%m-%d')
                target_month = target_date.replace(day=1)
            except ValueError:
                raise CommandError(f"Invalid date format: {options['month']}. Use YYYY-MM-DD")
        else:
            # Use current month (1st day)
            target_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        dry_run = options['dry_run']

        self.stdout.write(f"{'[DRY RUN] ' if dry_run else ''}Processing recurring works for {target_month.strftime('%B %Y')}...")

        # Fetch all active recurring assignments
        recurring_assignments = RecurringWorkAssignment.objects.filter(
            is_active=True
        ).select_related('assignment', 'work_service').prefetch_related('assigned_employees')

        if not recurring_assignments.exists():
            self.stdout.write(self.style.WARNING("No active recurring work assignments found."))
            return

        created_count = 0
        skipped_count = 0
        errors = []

        for recurring in recurring_assignments:
            try:
                assignment = recurring.assignment
                work_service = recurring.work_service
                employees = list(recurring.assigned_employees.all())

                # Check if work already exists for this month
                existing_work = Work.objects.filter(
                    assignment=assignment,
                    work_service=work_service,
                    created_for_month=target_month,
                    is_deleted=False
                ).exists()

                if existing_work:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  ⏭️  SKIP: {assignment.assignment_name} → {work_service.service_name} "
                            f"(already exists for {target_month.strftime('%B %Y')})"
                        )
                    )
                    skipped_count += 1
                    continue

                if not dry_run:
                    # Create new work entry
                    work = Work.objects.create(
                        assignment=assignment,
                        work_service=work_service,
                        price=recurring.price,
                        advance_payment=recurring.advance_payment,
                        work_mode=recurring.work_mode,
                        recurring_assignment=recurring,
                        created_for_month=target_month,
                        status='Pending'  # New works start as Pending
                    )

                    # Assign employees
                    work.assigned_employees.set(employees)

                    # Update the last_work_created_month
                    recurring.last_work_created_month = target_month
                    recurring.save(update_fields=['last_work_created_month'])

                    # Log creation
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  ✅ CREATED: {assignment.assignment_name} → {work_service.service_name} "
                            f"({len(employees)} employees) - Work ID: {work.id}"
                        )
                    )
                    created_count += 1
                else:
                    # Dry run: just show what would be created
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  ✅ [DRY RUN] Would create: {assignment.assignment_name} → {work_service.service_name} "
                            f"({len(employees)} employees)"
                        )
                    )
                    created_count += 1

            except Exception as e:
                error_msg = f"ERROR processing {recurring.assignment.assignment_name}: {str(e)}"
                self.stdout.write(self.style.ERROR(f"  ❌ {error_msg}"))
                errors.append(error_msg)

        # Summary
        self.stdout.write("\n" + "="*70)
        self.stdout.write(self.style.SUCCESS(f"✅ Created: {created_count}"))
        self.stdout.write(self.style.WARNING(f"⏭️  Skipped: {skipped_count}"))
        if errors:
            self.stdout.write(self.style.ERROR(f"❌ Errors: {len(errors)}"))
            for error in errors:
                self.stdout.write(self.style.ERROR(f"   - {error}"))
        self.stdout.write("="*70)

        if dry_run:
            self.stdout.write(self.style.WARNING("\n[DRY RUN MODE] No changes were made to the database."))
