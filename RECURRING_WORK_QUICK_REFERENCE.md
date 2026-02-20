# Recurring Work Service - Quick Reference Guide

## 🚀 Quick Start

### 1. Mark WorkService as Recurring
```python
WorkService.objects.create(
    service_name="Monthly Audit",
    is_recurring=True  # ← KEY!
)
```

### 2. Assign to Employees with `is_recurring=True`
```json
POST /api/works/bulk-create/
[{
    "assignment": 1,
    "work_service": 5,
    "price": "50000.00",
    "advance_payment": "10000.00",
    "work_mode": "Fixed",
    "assigned_employees": [1, 2, 3],
    "is_recurring": true  // ← KEY!
}]
```

### 3. Auto-Generate Monthly Works
```bash
# Current month
python manage.py create_recurring_works

# Specific month
python manage.py create_recurring_works --month 2024-03-01

# Preview (dry-run)
python manage.py create_recurring_works --dry-run
```

---

## 📊 Data Models

```
WorkService (is_recurring=True)
    ↓
Work (created with is_recurring=True)
    ↓
RecurringWorkAssignment (auto-created)
    ├── assignment
    ├── work_service
    ├── assigned_employees
    ├── price
    ├── advance_payment
    ├── work_mode
    ├── is_active
    └── last_work_created_month
```

---

## 🔑 Key Fields

| Field | Model | Purpose |
|-------|-------|---------|
| `is_recurring` | WorkService | Mark service as recurring |
| `recurring_assignment` | Work | Link to recurring template |
| `created_for_month` | Work | Month this work is for (1st day) |
| `is_active` | RecurringWorkAssignment | Enable/disable recurring |
| `assigned_employees` | RecurringWorkAssignment | Employees for this recurring |

---

## 💻 API Endpoints

### Create Recurring Work
```
POST /api/works/bulk-create/
Body: { is_recurring: true, ... }
```

### View Recurring Assignments
```python
from master.models import RecurringWorkAssignment
recurring = RecurringWorkAssignment.objects.filter(is_active=True)
```

### Deactivate Recurring
```python
recurring.is_active = False
recurring.save()
```

---

## 📅 Management Command

```bash
# Create works for current month
python manage.py create_recurring_works

# Create for specific month
python manage.py create_recurring_works --month 2024-03-01

# Dry run (preview only)
python manage.py create_recurring_works --dry-run

# Help
python manage.py create_recurring_works --help
```

---

## 🧪 Test It

```bash
# Run test script
python test_recurring_simple.py

# Expected: 5 tests pass ✅
```

---

## ⚙️ Configuration

### Schedule Monthly Execution (Cron)
```bash
# Add to crontab - runs on 1st of every month at 00:00
0 0 1 * * cd /path/to/project && python manage.py create_recurring_works > /tmp/recurring_works.log 2>&1
```

### Celery Task
```python
from celery import shared_task

@shared_task
def create_recurring_works_task():
    from django.core.management import call_command
    call_command('create_recurring_works')

# Schedule: first day of month at midnight
from celery.schedules import crontab
app.conf.beat_schedule = {
    'create-monthly-works': {
        'task': 'app.tasks.create_recurring_works_task',
        'schedule': crontab(day_of_month=1, hour=0, minute=0),
    },
}
```

---

## 🔍 Monitoring

### Check Recurring Assignments
```python
from master.models import RecurringWorkAssignment

# Active recurring assignments
active = RecurringWorkAssignment.objects.filter(is_active=True)

# Last work created
for r in active:
    print(f"{r.assignment.name} - Last: {r.last_work_created_month}")
```

### Verify Works Created
```python
from master.models import Work
from datetime import datetime

current_month = datetime.now().replace(day=1)
works = Work.objects.filter(created_for_month=current_month)
print(f"Works for this month: {works.count()}")
```

---

## ✅ Checklist Before Going Live

- [ ] WorkService has `is_recurring=True`
- [ ] Assignment exists and is active
- [ ] Employees are valid and active
- [ ] Used `is_recurring=True` in bulk-create API
- [ ] RecurringWorkAssignment was created
- [ ] Management command created first test work
- [ ] Cron job scheduled (if using automation)
- [ ] Test script passes
- [ ] Documentation reviewed

---

## 🐛 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Works not creating | Check `is_recurring=True` and `is_active=True` |
| Duplicate works | System prevents via `created_for_month` |
| Employees not assigned | Check `assigned_employees` list |
| Command errors | Check logs and permissions |
| Works not for correct month | Verify `--month` parameter format |

---

## 📋 Example Workflow

```
1. Create WorkService with is_recurring=True
   └─ Service: "Monthly Audit"

2. Create Assignment
   └─ "Q1 2024 Audits"

3. Call bulk-create API with is_recurring=True
   └─ Creates: Work for Feb 2024
   └─ Creates: RecurringWorkAssignment

4. Run command on 1st of March
   └─ Creates: Work for March 2024
   └─ Updates: last_work_created_month

5. Repeat monthly automatically
   └─ April 1st → Work for April
   └─ May 1st → Work for May
   └─ etc...

6. To stop: Set is_active=False
   └─ No more works created
```

---

## 🎯 Key Concepts

### Recurring vs Fixed Months
- **Recurring**: Works created every month automatically
- **Fixed**: Works created only once, no auto-generation

### created_for_month Field
- Always set to 1st day of month
- Example: Feb 2024 = 2024-02-01
- Prevents duplicate detection

### is_active Flag
- `True`: Monthly works will be generated
- `False`: No more works will be generated (can reactivate)

### last_work_created_month
- Tracks last successful generation
- Used for monitoring and debugging
- Updated after each successful work creation

---

## 📞 Support

For issues or questions about the Recurring Work Service feature:

1. Check test script: `python test_recurring_simple.py`
2. Review logs from management command
3. Verify `RecurringWorkAssignment` records exist
4. Check `is_recurring` and `is_active` flags
5. Review documentation: `RECURRING_WORK_SERVICE_DOCUMENTATION.md`

---

Generated: February 2024
Status: ✅ Production Ready
