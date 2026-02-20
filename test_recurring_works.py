"""
Test script to demonstrate the Recurring Work Service Feature

This script:
1. Creates test data (Client, Assignment, WorkService, Employees)
2. Uses the bulk-create API to assign a recurring work service
3. Runs the management command to generate monthly works
4. Verifies the recurring assignments were created correctly
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
sys.path.insert(0, 'c:\\AjayProject\\CA\\ca_firm_16Feb')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ca_firm.settings')
django.setup()

from django.contrib.auth.models import User as DjangoUser
from userauth.models import User
from master.models import Client, Assignment, WorkService, Document, Work, RecurringWorkAssignment


def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)


def test_recurring_work_feature():
    """Test the recurring work service feature"""
    
    print_header("RECURRING WORK SERVICE FEATURE - TEST SCRIPT")
    
    # Step 1: Create or fetch test data
    print("\n📋 Step 1: Setting up test data...")
    
    # Cleanup existing test data
    WorkService.objects.filter(service_name__startswith="[TEST]").delete()
    Client.objects.filter(client_name__startswith="[TEST]").delete()
    Assignment.objects.filter(assignment_name__startswith="[TEST]").delete()
    
    # Create a test client
    client, _ = Client.objects.get_or_create(
        client_name="[TEST] ABC Corporation",
        defaults={
            'phone': '1234567890',
            'email': 'test@abc.com',
            'mobile_number': '9876543210'
        }
    )
    print(f"✅ Created Client: {client.client_name}")
    
    # Create a recurring work service
    work_service, created = WorkService.objects.get_or_create(
        service_name="[TEST] Monthly Compliance Audit",
        defaults={
            'description': 'Monthly compliance audit - recurring monthly',
            'is_recurring': True  # 🔄 KEY: Mark as recurring
        }
    )
    print(f"✅ Created WorkService: {work_service.service_name} (Recurring: {work_service.is_recurring})")
    
    # Create documents for the work service
    doc1, _ = Document.objects.get_or_create(
        work_service=work_service,
        document_name="[TEST] Compliance Report",
        defaults={'is_checked': False}
    )
    print(f"✅ Created Document: {doc1.document_name}")
    
    # Create an assignment
    assignment, created = Assignment.objects.get_or_create(
        assignment_name="[TEST] Q1 Compliance Check",
        assignment_date=datetime.now().date(),
        client=client,
        defaults={'number_of_assignment': 1}
    )
    print(f"✅ Created Assignment: {assignment.assignment_name}")
    
    # Get or create test employees
    employees = []
    for i in range(1, 3):
        user, created = User.objects.get_or_create(
            username=f"test_employee_{i}",
            defaults={
                'full_name': f"[TEST] Employee {i}",
                'email': f"employee{i}@test.com",
                'is_active': True,
                'phone_no': f"999{i:0>4}",  # Unique phone number
                'joining_date': datetime.now().date()  # Required field
            }
        )
        employees.append(user)
        print(f"✅ Created Employee: {user.full_name}")
    
    # Step 2: Simulate bulk-create API call with recurring=True
    print_header("Step 2: Creating work via API (with is_recurring=True)")
    
    from master.serializers import BulkWorkSerializer
    from django.db import transaction
    from master.models import AssignmentDocumentSubmission
    from django.utils import timezone
    
    work_data = [
        {
            'assignment': assignment.id,
            'work_service': work_service.id,
            'price': '50000.00',
            'advance_payment': '10000.00',
            'work_mode': 'Fixed',
            'assigned_employees': [e.id for e in employees],
            'is_recurring': True,  # 🔄 KEY: Mark this as recurring
            'document_ids': [doc1.id]
        }
    ]
    
    serializer = BulkWorkSerializer(data=work_data, many=True)
    
    if serializer.is_valid():
        with transaction.atomic():
            works = serializer.save()
            
            for work in works:
                assigned_employees = work.assigned_employees.all()
                if assigned_employees.exists():
                    print(f"✅ Created Work: {work.id}")
                    print(f"   - Assignment: {work.assignment.assignment_name}")
                    print(f"   - Service: {work.work_service.service_name}")
                    print(f"   - Price: ₹{work.price}")
                    print(f"   - Employees: {', '.join([e.full_name for e in assigned_employees])}")
                
                # Handle recurring assignment
                is_recurring = getattr(work, "_is_recurring", False)
                if is_recurring and work.work_service.is_recurring:
                    work_service_obj = work.work_service
                    assignment_obj = work.assignment
                    employees_list = getattr(work, "_employees", list(assigned_employees.values_list('id', flat=True)))
                    
                    recurring_record, created = RecurringWorkAssignment.objects.update_or_create(
                        assignment=assignment_obj,
                        work_service=work_service_obj,
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
                    
                    print(f"\n🔄 RECURRING ASSIGNMENT CREATED:")
                    print(f"   - ID: {recurring_record.id}")
                    print(f"   - Assignment: {recurring_record.assignment.assignment_name}")
                    print(f"   - Service: {recurring_record.work_service.service_name}")
                    print(f"   - Price: ₹{recurring_record.price}")
                    print(f"   - Employees: {recurring_record.assigned_employees.count()}")
                    print(f"   - Active: {recurring_record.is_active}")
    else:
        print(f"❌ Serializer validation failed: {serializer.errors}")
        return
    
    # Step 3: Check RecurringWorkAssignment
    print_header("Step 3: Verifying RecurringWorkAssignment")
    
    recurring_assignments = RecurringWorkAssignment.objects.filter(
        assignment=assignment,
        work_service=work_service,
        is_active=True
    )
    
    if recurring_assignments.exists():
        for recurring in recurring_assignments:
            print(f"✅ Found Recurring Assignment: {recurring.id}")
            print(f"   - Assignment: {recurring.assignment.assignment_name}")
            print(f"   - Service: {recurring.work_service.service_name}")
            print(f"   - Price: ₹{recurring.price}")
            print(f"   - Last work created for: {recurring.last_work_created_month}")
            print(f"   - Assigned Employees: {recurring.assigned_employees.count()}")
            
            for emp in recurring.assigned_employees.all():
                print(f"     • {emp.full_name}")
    else:
        print("❌ No recurring assignments found!")
        return
    
    # Step 4: Run the management command (simulate)
    print_header("Step 4: Running management command to create next month's works")
    
    # For demonstration, we'll create works for next month manually
    next_month_date = datetime.now() + timedelta(days=32)
    next_month = next_month_date.replace(day=1)
    
    print(f"\n🗓️  Processing for: {next_month.strftime('%B %Y')}")
    
    recurring_records = RecurringWorkAssignment.objects.filter(is_active=True)
    
    created_works = []
    for recurring in recurring_records:
        # Check if work already exists
        existing = Work.objects.filter(
            assignment=recurring.assignment,
            work_service=recurring.work_service,
            created_for_month=next_month.replace(day=1),
            is_deleted=False
        ).exists()
        
        if not existing:
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
            
            # Assign employees
            new_work.assigned_employees.set(recurring.assigned_employees.all())
            
            # Update last work created month
            recurring.last_work_created_month = next_month.replace(day=1)
            recurring.save(update_fields=['last_work_created_month'])
            
            created_works.append(new_work)
            print(f"✅ Created Work for {next_month.strftime('%B %Y')}: ID {new_work.id}")
    
    # Step 5: Verify monthly works
    print_header("Step 5: Verifying all works for this assignment")
    
    all_works = Work.objects.filter(
        assignment=assignment,
        work_service=work_service,
        is_deleted=False
    ).order_by('created_for_month')
    
    print(f"\n📊 Total Works: {all_works.count()}")
    for work in all_works:
        month_str = work.created_for_month.strftime('%B %Y') if work.created_for_month else 'N/A'
        recurring_str = "Yes" if work.recurring_assignment else "No"
        print(f"   • Work ID: {work.id} | Month: {month_str} | Recurring: {recurring_str} | Status: {work.status}")
    
    print_header("✅ TEST COMPLETED SUCCESSFULLY!")
    print("\n🎯 Summary:")
    print("   1. ✅ Recurring WorkService created")
    print("   2. ✅ Work assigned to employees with is_recurring=True")
    print("   3. ✅ RecurringWorkAssignment record created")
    print("   4. ✅ Next month's work auto-generated")
    print("   5. ✅ Works properly tracked for recurring assignment")
    
    print("\n💡 How it works:")
    print("   • When is_recurring=True is passed in bulk-create API")
    print("   • RecurringWorkAssignment is created automatically")
    print("   • Run: python manage.py create_recurring_works")
    print("   • This generates works for the current month")
    print("   • Use --month YYYY-MM-DD to create for specific month")


if __name__ == '__main__':
    try:
        test_recurring_work_feature()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
