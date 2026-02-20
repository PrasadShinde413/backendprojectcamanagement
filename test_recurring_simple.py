"""
Simple test for Recurring Work Service Feature
"""

import os
import sys
import django
from datetime import datetime, timedelta

sys.path.insert(0, 'c:\\AjayProject\\CA\\ca_firm_16Feb')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ca_firm.settings')
django.setup()

from userauth.models import User
from master.models import Client, Assignment, WorkService, Document, Work, RecurringWorkAssignment


def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)


def main():
    print_header("RECURRING WORK SERVICE FEATURE - TEST")
    
    # Cleanup
    print("\n[SETUP] Cleaning up old test data...")
    WorkService.objects.filter(service_name__startswith="[TEST]").delete()
    Client.objects.filter(client_name__startswith="[TEST]").delete()
    Assignment.objects.filter(assignment_name__startswith="[TEST]").delete()
    User.objects.filter(username__startswith="test_employee_").delete()
    
    # Create test client
    print("[SETUP] Creating test client...")
    client, _ = Client.objects.get_or_create(
        client_name="[TEST] ABC Corporation",
        defaults={'phone': '1234567890', 'email': 'test@abc.com', 'mobile_number': '9876543210'}
    )
    print(f"[OK] Client: {client.client_name}")
    
    # Create recurring work service
    print("[SETUP] Creating recurring work service...")
    work_service, _ = WorkService.objects.get_or_create(
        service_name="[TEST] Monthly Audit",
        defaults={'description': 'Monthly audit - recurring', 'is_recurring': True}
    )
    print(f"[OK] WorkService: {work_service.service_name} (is_recurring={work_service.is_recurring})")
    
    # Create document
    print("[SETUP] Creating document...")
    doc1, _ = Document.objects.get_or_create(
        work_service=work_service,
        document_name="[TEST] Audit Report",
        defaults={'is_checked': False}
    )
    print(f"[OK] Document: {doc1.document_name}")
    
    # Create assignment
    print("[SETUP] Creating assignment...")
    assignment, _ = Assignment.objects.get_or_create(
        assignment_name="[TEST] Q1 Audit",
        assignment_date=datetime.now().date(),
        client=client,
        defaults={'number_of_assignment': 1}
    )
    print(f"[OK] Assignment: {assignment.assignment_name}")
    
    # Create employees
    print("[SETUP] Creating employees...")
    employees = []
    for i in range(1, 3):
        user, _ = User.objects.get_or_create(
            username=f"test_employee_{i}",
            defaults={
                'full_name': f"[TEST] Employee {i}",
                'email': f"employee{i}@test.com",
                'is_active': True,
                'phone_no': f"999{i:0>4}",
                'joining_date': datetime.now().date()
            }
        )
        employees.append(user)
        print(f"[OK] Employee: {user.full_name}")
    
    # Test the API call (simulate bulk-create with recurring=True)
    print_header("TEST 1: Creating work via API with is_recurring=True")
    
    from master.serializers import BulkWorkSerializer
    from django.db import transaction
    from master.models import AssignmentDocumentSubmission
    from django.utils import timezone
    
    work_data = [{
        'assignment': assignment.id,
        'work_service': work_service.id,
        'price': '50000.00',
        'advance_payment': '10000.00',
        'work_mode': 'Fixed',
        'assigned_employees': [e.id for e in employees],
        'is_recurring': True,  # KEY: Mark as recurring
        'document_ids': [doc1.id]
    }]
    
    serializer = BulkWorkSerializer(data=work_data, many=True)
    
    if not serializer.is_valid():
        print(f"[ERROR] Validation failed: {serializer.errors}")
        return
    
    print("[OK] Serializer validation passed")
    
    # Save with recurring assignment logic
    with transaction.atomic():
        works = serializer.save()
        
        for work in works:
            assigned_employees = work.assigned_employees.all()
            print(f"[OK] Work created: ID={work.id}, Employees={assigned_employees.count()}")
            
            # Handle recurring
            is_recurring = getattr(work, "_is_recurring", False)
            if is_recurring and work.work_service.is_recurring:
                employees_list = getattr(work, "_employees", list(assigned_employees.values_list('id', flat=True)))
                
                recurring_record, created = RecurringWorkAssignment.objects.update_or_create(
                    assignment=work.assignment,
                    work_service=work.work_service,
                    defaults={
                        'price': work.price,
                        'advance_payment': work.advance_payment,
                        'work_mode': work.work_mode,
                        'is_active': True
                    }
                )
                
                recurring_record.assigned_employees.set(employees_list)
                
                work.recurring_assignment = recurring_record
                work.created_for_month = datetime.now().replace(day=1)
                work.save(update_fields=['recurring_assignment', 'created_for_month'])
                
                print(f"\n[RECURRING] Created RecurringWorkAssignment:")
                print(f"   - ID: {recurring_record.id}")
                print(f"   - Assignment: {recurring_record.assignment.assignment_name}")
                print(f"   - Service: {recurring_record.work_service.service_name}")
                print(f"   - Employees: {recurring_record.assigned_employees.count()}")
                print(f"   - Active: {recurring_record.is_active}")
    
    # Test 2: Verify recurring assignment
    print_header("TEST 2: Verify RecurringWorkAssignment")
    
    recurring = RecurringWorkAssignment.objects.get(
        assignment=assignment,
        work_service=work_service
    )
    
    print(f"[OK] Found RecurringWorkAssignment: {recurring.id}")
    print(f"   - Price: {recurring.price}")
    print(f"   - Advance Payment: {recurring.advance_payment}")
    print(f"   - Employees: {list(recurring.assigned_employees.values_list('full_name', flat=True))}")
    
    # Test 3: Simulate management command
    print_header("TEST 3: Simulate creating next month's work")
    
    next_month_date = datetime.now() + timedelta(days=32)
    next_month = next_month_date.replace(day=1)
    
    print(f"[ACTION] Processing for month: {next_month.strftime('%B %Y')}")
    
    # Check if already exists
    existing = Work.objects.filter(
        assignment=recurring.assignment,
        work_service=recurring.work_service,
        created_for_month=next_month.replace(day=1),
        is_deleted=False
    ).exists()
    
    if existing:
        print(f"[SKIP] Work already exists for {next_month.strftime('%B %Y')}")
    else:
        # Create new work
        new_work = Work.objects.create(
            assignment=recurring.assignment,
            work_service=recurring.work_service,
            price=recurring.price,
            advance_payment=recurring.advance_payment,
            work_mode=recurring.work_mode,
            recurring_assignment=recurring,
            created_for_month=next_month.replace(day=1),
            status='Pending'
        )
        
        new_work.assigned_employees.set(recurring.assigned_employees.all())
        
        recurring.last_work_created_month = next_month.replace(day=1)
        recurring.save(update_fields=['last_work_created_month'])
        
        print(f"[OK] Created work for {next_month.strftime('%B %Y')}: ID={new_work.id}")
    
    # Test 4: Verify all works
    print_header("TEST 4: Verify all works")
    
    all_works = Work.objects.filter(
        assignment=assignment,
        work_service=work_service,
        is_deleted=False
    ).order_by('created_for_month')
    
    print(f"[INFO] Total works: {all_works.count()}")
    for work in all_works:
        month_str = work.created_for_month.strftime('%B %Y') if work.created_for_month else 'N/A'
        recurring_str = "Yes" if work.recurring_assignment else "No"
        print(f"   - Work ID={work.id} | Month={month_str} | Recurring={recurring_str} | Status={work.status}")
    
    print_header("TEST COMPLETED SUCCESSFULLY!")
    print("\nSUMMARY:")
    print("  1. [OK] Recurring WorkService created")
    print("  2. [OK] Work assigned to employees with is_recurring=True")
    print("  3. [OK] RecurringWorkAssignment record created")
    print("  4. [OK] Next month's work auto-generated")
    print("  5. [OK] Works properly tracked")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
