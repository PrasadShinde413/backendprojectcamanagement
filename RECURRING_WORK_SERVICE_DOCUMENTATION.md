# Recurring Work Service Feature Documentation

## Overview

The Recurring Work Service feature allows you to automatically assign work services to employees every month. Once a recurring work service is configured, the system will automatically create monthly work assignments without requiring manual intervention each month.

### Key Features

✅ **Automatic Monthly Work Generation** - Works are created automatically for recurring services  
✅ **Employee Persistence** - Same employees are assigned each month  
✅ **Smart Duplicate Prevention** - Duplicate works for the same month are automatically prevented  
✅ **History Tracking** - All monthly works are tracked with `created_for_month` field  
✅ **Management Command** - CLI tool to manually trigger monthly work generation  
✅ **Flexible Configuration** - Recurring assignments can be activated/deactivated as needed  

---

## Architecture

### New Models

#### 1. **RecurringWorkAssignment** Model
Stores the template for recurring work assignments.

```python
class RecurringWorkAssignment(models.Model):
    assignment          # ForeignKey to Assignment
    work_service        # ForeignKey to WorkService (marked with is_recurring=True)
    assigned_employees  # ManyToMany to User
    price               # Decimal field for work price
    advance_payment     # Decimal field for advance payment
    work_mode           # CharField ('Fixed' or 'Recurring')
    last_work_created_month  # DateField to track last created month
    is_active           # Boolean to enable/disable recurring
    created_at          # DateTime of creation
    updated_at          # DateTime of last update
```

### Updated Models

#### 1. **WorkService** Model
Already has `is_recurring` boolean field (must be True for recurring works).

#### 2. **Work** Model (Updated)
Added two new fields:

```python
# Link to RecurringWorkAssignment if auto-generated
recurring_assignment = ForeignKey(
    'RecurringWorkAssignment',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="generated_works"
)

# Track which month this recurring work is for (e.g., 2024-01-01)
created_for_month = DateField(
    null=True,
    blank=True,
    help_text="The first day of the month this recurring work is for"
)
```

---

## How It Works

### Step 1: Setup WorkService as Recurring

When creating a WorkService, mark it as recurring:

```python
POST /api/work-services/

{
    "service_name": "Monthly Compliance Audit",
    "description": "Monthly compliance audit for clients",
    "is_recurring": true  # KEY: Mark as recurring
}
```

### Step 2: Assign Recurring Work via Bulk API

Use the bulk-create work API with `is_recurring: true`:

```python
POST /api/works/bulk-create/

[
    {
        "assignment": 1,
        "work_service": 5,  # Must have is_recurring=true
        "price": "50000.00",
        "advance_payment": "10000.00",
        "work_mode": "Fixed",
        "assigned_employees": [1, 2, 3],  # Employee IDs
        "is_recurring": true  # KEY: Mark this work as recurring
    }
]
```

**What happens automatically:**
1. Work is created for the current month
2. `RecurringWorkAssignment` record is created/updated
3. All assigned employees are stored
4. `created_for_month` is set to the 1st of current month

### Step 3: Auto-Generate Monthly Works

#### Option A: Manual Trigger (via Management Command)

```bash
# Create works for current month
python manage.py create_recurring_works

# Create works for specific month
python manage.py create_recurring_works --month 2024-03-01

# Preview changes without creating (dry-run)
python manage.py create_recurring_works --dry-run
```

#### Option B: Scheduled Execution (Cron Job)

Schedule the command to run on the 1st of each month:

```bash
# Add to crontab (runs on 1st of every month at 00:00)
0 0 1 * * cd /path/to/project && python manage.py create_recurring_works
```

#### Option C: Celery Task (If Available)

```python
from celery import shared_task

@shared_task
def create_monthly_recurring_works():
    from django.core.management import call_command
    call_command('create_recurring_works')
```

---

## API Endpoints

### 1. Create/Update Recurring Work Service

**POST** `/api/work-services/create/`

```json
{
    "service_name": "Monthly Tax Compliance",
    "description": "Monthly tax compliance audit",
    "is_recurring": true  // Mark as recurring
}
```

### 2. Assign Recurring Work

**POST** `/api/works/bulk-create/`

```json
[
    {
        "assignment": 1,
        "work_service": 5,
        "price": "100000.00",
        "advance_payment": "20000.00",
        "work_mode": "Fixed",
        "assigned_employees": [1, 2, 3],
        "is_recurring": true  // Enable recurring assignment
    }
]
```

### 3. View Recurring Assignments

**GET** `/api/works/by-assignment/{assignment_id}/`

Returns all works including those linked to RecurringWorkAssignment.

### 4. Modify Recurring Assignment

Update the RecurringWorkAssignment through Django admin or custom API:

```python
from master.models import RecurringWorkAssignment

# Deactivate recurring
recurring = RecurringWorkAssignment.objects.get(id=1)
recurring.is_active = False
recurring.save()

# Update employees
recurring.assigned_employees.set([5, 6, 7])
recurring.save()
```

---

## Database Fields

### RecurringWorkAssignment Table Schema

| Column | Type | Description |
|--------|------|-------------|
| id | INT (PK) | Primary key |
| assignment_id | INT (FK) | Reference to Assignment |
| work_service_id | INT (FK) | Reference to WorkService |
| price | DECIMAL | Work price |
| advance_payment | DECIMAL | Advance payment amount |
| work_mode | VARCHAR(10) | 'Fixed' or 'Recurring' |
| last_work_created_month | DATE | Last month work was created |
| is_active | BOOLEAN | Whether recurring is active |
| created_at | DATETIME | Creation timestamp |
| updated_at | DATETIME | Last update timestamp |

### Work Table Updates

| Column | Type | Description |
|--------|------|-------------|
| recurring_assignment_id | INT (FK) | Link to RecurringWorkAssignment |
| created_for_month | DATE | 1st day of month this work is for |

---

## Example Workflow

### Scenario: Monthly Compliance Audit

1. **January 1st, 2024**: Manager creates Assignment "Q1 2024 Audits"

2. **January 5th, 2024**: Creates WorkService "Monthly Compliance Audit" with `is_recurring=true`

3. **January 10th, 2024**: Assigns work to 3 employees with `is_recurring=true`
   - Work is created for January
   - RecurringWorkAssignment is created and active

4. **February 1st, 2024**: Management command runs automatically
   - Checks all RecurringWorkAssignment records
   - Creates new Work for February with same employees and price
   - Status: Pending (employees notified)

5. **March 1st, 2024**: Same process repeats

6. **April 15th, 2024**: Manager wants to stop recurring
   - Sets `is_active = False` on RecurringWorkAssignment
   - No more works will be generated starting next month

---

## Management Command Usage

### View Usage

```bash
python manage.py create_recurring_works --help
```

### Command Options

```
--month YYYY-MM-DD      Process specific month (e.g., 2024-03-01)
--dry-run               Preview changes without creating
```

### Example Outputs

#### Successful Creation
```
Processing recurring works for March 2024...
  ✅ CREATED: Project A → Monthly Audit (3 employees) - Work ID: 105
  ✅ CREATED: Project B → Monthly Tax Audit (2 employees) - Work ID: 106

======================================================================
✅ Created: 2
⏭️  Skipped: 0
======================================================================
```

#### Skip Existing Works
```
Processing recurring works for March 2024...
  ⏭️  SKIP: Project A → Monthly Audit (already exists for March 2024)

======================================================================
✅ Created: 0
⏭️  Skipped: 1
======================================================================
```

#### Dry Run
```
[DRY RUN] Processing recurring works for March 2024...
  ✅ [DRY RUN] Would create: Project A → Monthly Audit (3 employees)

======================================================================
✅ Created: 1
⏭️  Skipped: 0
======================================================================

[DRY RUN MODE] No changes were made to the database.
```

---

## Important Fields Explanation

### created_for_month
- **Type**: DateField
- **Format**: Always uses the 1st day of the month (e.g., 2024-03-01)
- **Purpose**: Uniquely identifies which month a work is for
- **Usage**: Prevents duplicate works for the same month

### recurring_assignment
- **Type**: ForeignKey to RecurringWorkAssignment
- **Null/Blank**: True (NULL for manually created works)
- **Purpose**: Links auto-generated works to their template

### last_work_created_month
- **Type**: DateField
- **null/Blank**: True
- **Purpose**: Tracks when last monthly generation occurred
- **Usage**: Helps identify stale recurring assignments

---

## Testing

### Run Simple Test
```bash
python test_recurring_simple.py
```

### Expected Output
```
[OK] Work created: ID=19, Employees=2
[RECURRING] Created RecurringWorkAssignment:
   - ID: 1
   - Assignment: [TEST] Q1 Audit
   - Service: [TEST] Monthly Audit
   - Employees: 2

[OK] Created work for March 2026: ID=20
[INFO] Total works: 2
   - Work ID=19 | Month=February 2026 | Recurring=Yes
   - Work ID=20 | Month=March 2026 | Recurring=Yes
```

---

## Troubleshooting

### Issue: Works not being created
**Solution**: Ensure `WorkService.is_recurring = True`

### Issue: Duplicate works created
**Solution**: The system prevents duplicates via `created_for_month` check

### Issue: Employees not assigned to recurring work
**Solution**: Verify `assigned_employees` list in API request and check `RecurringWorkAssignment.assigned_employees`

### Issue: Management command shows errors
**Solution**: Check logs and ensure assignment/work_service combo doesn't have permission issues

---

## API Request/Response Examples

### Create Recurring Work

**Request:**
```json
POST /api/works/bulk-create/
[{
    "assignment": 1,
    "work_service": 5,
    "price": "50000.00",
    "advance_payment": "10000.00",
    "work_mode": "Fixed",
    "assigned_employees": [1, 2, 3],
    "is_recurring": true
}]
```

**Response:**
```json
{
    "message": "Works created successfully",
    "total_created": 1,
    "total_price": 50000.00,
    "total_advance_payment": 10000.00,
    "balance_amount": 40000.00
}
```

---

## Migration Information

### Migration File Created
```
0015_work_created_for_month_recurringworkassignment_and_more.py
```

### Changes Made
1. Added `created_for_month` field to Work model
2. Added `recurring_assignment` field to Work model
3. Created new `RecurringWorkAssignment` model
4. Created `recurring_work_assignments` database table
5. Created many-to-many table for `assigned_employees`

### Migration Status
- ✅ Migrations created successfully
- ✅ Database updated
- ✅ No conflicts or errors

---

## Files Modified/Created

### Modified Files
1. `master/models.py` - Added RecurringWorkAssignment model, updated Work model
2. `master/serializers.py` - Updated BulkWorkSerializer to handle `is_recurring`
3. `master/views.py` - Updated BulkWorkCreateAPIView to create recurring assignments

### New Files
1. `master/management/commands/create_recurring_works.py` - Management command
2. `test_recurring_simple.py` - Test script (root directory)

---

## Best Practices

1. **Always mark WorkService**: Ensure `is_recurring=True` when creating recurring work services

2. **Use Management Command**: Schedule the command to run monthly for automation

3. **Monitor last_work_created_month**: Track when works were last generated

4. **Deactivate When Done**: Set `is_active=False` to stop recurring without deleting

5. **Validate Employees**: Ensure all assigned employee IDs are valid and active

6. **Test in Dry-Run**: Always use `--dry-run` first to preview changes

---

## FAQ

**Q: Can I change employees in a recurring assignment?**  
A: Yes, update the `assigned_employees` many-to-many field on RecurringWorkAssignment. Future months will reflect new employees.

**Q: What if I need to skip a month?**  
A: Manually delete the Work for that month before running the command.

**Q: Can I have multiple recurring services for the same assignment?**  
A: Yes, create separate RecurringWorkAssignment records for each service.

**Q: How do I stop recurring works?**  
A: Set `is_active = False` on the RecurringWorkAssignment record.

**Q: Can I change the price for future recurring works?**  
A: Yes, update the `price` field on RecurringWorkAssignment. Future works will use new price.

---

## Summary

The Recurring Work Service feature provides:
- ✅ Automatic monthly work generation
- ✅ Employee persistence across months
- ✅ Duplicate prevention
- ✅ Comprehensive tracking
- ✅ Flexible management command
- ✅ Easy activation/deactivation

This ensures consistent work assignments without manual intervention!
