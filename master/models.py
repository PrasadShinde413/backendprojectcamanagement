from django.db import models
from django.utils import timezone

class Client(models.Model):
    client_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    mobile_number = models.CharField(max_length=15, null=True, blank=True)

    gst_number = models.CharField(max_length=20, null=True, blank=True)
    pan = models.CharField(max_length=15, null=True, blank=True)

    birthdate = models.DateField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "clients"
        ordering = ['-created_at']

    def __str__(self):
        return self.client_name


from django.db import models
from django.utils import timezone

class WorkService(models.Model):
    service_name = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)
    is_recurring = models.BooleanField(default=False)

    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "work_services"

    def __str__(self):
        return self.service_name


class Document(models.Model):
    work_service = models.ForeignKey(
        WorkService,
        on_delete=models.CASCADE,
        related_name="documents"
    )
    document_name = models.CharField(max_length=150)
    is_checked = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "documents"

    def __str__(self):
        return self.document_name


# from django.db import models
# from django.utils import timezone
# from .models import Client

# class Assignment(models.Model):
#     assignment_name = models.CharField(max_length=150)
#     assignment_date = models.DateField()

#     client = models.ForeignKey(
#         Client,
#         on_delete=models.CASCADE,
#         related_name="assignments"
#     )

#     number_of_assignment = models.IntegerField(default=1)

#     is_deleted = models.BooleanField(default=False)
#     created_at = models.DateTimeField(default=timezone.now)

#     class Meta:
#         db_table = "assignments"

#     def __str__(self):
#         return self.assignment_name


from django.db import models
from django.utils import timezone
from .models import Client

class Assignment(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )

    assignment_name = models.CharField(max_length=150)
    assignment_date = models.DateField()

    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="assignments"
    )

    number_of_assignment = models.IntegerField(default=1)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'   # 👈 AUTO SET
    )

    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "assignments"

    def __str__(self):
        return self.assignment_name


# from django.db import models
# from django.utils import timezone
# from .models import Assignment
# from .models import WorkService
# from userauth.models import User

# class Work(models.Model):
#     WORK_MODE_CHOICES = (
#         ('Online', 'Online'),
#         ('Offline', 'Offline'),
#     )

#     assignment = models.ForeignKey(
#         Assignment,
#         on_delete=models.CASCADE,
#         related_name="works"
#     )

#     work_service = models.ForeignKey(
#         WorkService,
#         on_delete=models.PROTECT,
#         related_name="works"
#     )

#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     advance_payment = models.DecimalField(
#         max_digits=10, decimal_places=2, default=0
#     )

#     work_mode = models.CharField(
#         max_length=10, choices=WORK_MODE_CHOICES
#     )
#     assigned_employees = models.ManyToManyField(
#         User,
#         related_name="assigned_works"
#     )

#     is_deleted = models.BooleanField(default=False)
#     created_at = models.DateTimeField(default=timezone.now)

#     class Meta:
#         db_table = "works"

from django.db import models
from django.utils import timezone
from .models import Assignment, WorkService
from userauth.models import User

class Work(models.Model):
    WORK_MODE_CHOICES = (
        ('Fixed', 'Fixed'),
        ('Reccuring', 'Reccuring'),
    )

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),

    )

    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name="works"
    )

    work_service = models.ForeignKey(
        WorkService,
        on_delete=models.PROTECT,
        related_name="works"
    )

    price = models.DecimalField(max_digits=10, decimal_places=2)
    advance_payment = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    work_mode = models.CharField(max_length=10, choices=WORK_MODE_CHOICES)

    assigned_employees = models.ManyToManyField(
        User,
        related_name="assigned_works"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'   # 👈 AUTO SET
    )

    # 🔄 RECURRING TRACKING FIELDS
    # Link to RecurringWorkAssignment if this work is auto-generated (null if manually created)
    recurring_assignment = models.ForeignKey(
        'RecurringWorkAssignment',
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,
        related_name="generated_works"
    )
    
    # Track which month this recurring work is for (YYYY-MM-01)
    created_for_month = models.DateField(
        null=True,
        blank=True,
        help_text="The first day of the month this recurring work is for (e.g., 2024-01-01 for January 2024)"
    )

    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "works"

##############################################################################################
# class AssignmentDocumentSubmission(models.Model):
#     SUBMISSION_STATUS_CHOICES = (
#         ('Pending', 'Pending'),
#         ('Submitted', 'Submitted'),
#         ('Returned', 'Returned'),
#     )

#     assignment = models.ForeignKey(
#         Assignment,
#         on_delete=models.CASCADE,
#         related_name="document_submissions"
#     )

#     document = models.ForeignKey(
#         Document,
#         on_delete=models.CASCADE,
#         related_name="submissions"
#     )

#     status = models.CharField(
#         max_length=20,
#         choices=SUBMISSION_STATUS_CHOICES,
#         default='Pending'
#     )

#     submitted_date = models.DateTimeField(null=True, blank=True)
#     return_date = models.DateTimeField(null=True, blank=True)
#     return_reason = models.TextField(null=True, blank=True)

#     created_at = models.DateTimeField(default=timezone.now)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         db_table = "assignment_document_submissions"
#         unique_together = ('assignment', 'document')

#     def __str__(self):
#         return f"{self.assignment.assignment_name} - {self.document.document_name} - {self.status}"

from userauth.models import User

# class AssignmentDocumentSubmission(models.Model):
#     SUBMISSION_STATUS_CHOICES = (
#         ('Pending', 'Pending'),
#         ('Submitted', 'Submitted'),
#         ('Returned', 'Returned'),
#     )

#     assignment = models.ForeignKey(
#         Assignment,
#         on_delete=models.CASCADE,
#         related_name="document_submissions"
#     )

#     document = models.ForeignKey(
#         Document,
#         on_delete=models.CASCADE,
#         related_name="submissions"
#     )

#     employee = models.ForeignKey(   # ✅ NEW FIELD
#         User,
#         on_delete=models.CASCADE,
#         related_name="document_submissions"
#     )

#     status = models.CharField(
#         max_length=20,
#         choices=SUBMISSION_STATUS_CHOICES,
#         default='Pending'
#     )

#     submitted_date = models.DateTimeField(null=True, blank=True)
#     return_date = models.DateTimeField(null=True, blank=True)
#     return_reason = models.TextField(null=True, blank=True)

#     created_at = models.DateTimeField(default=timezone.now)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         db_table = "assignment_document_submissions"
#         unique_together = ('assignment', 'document', 'employee')  # ✅ UPDATED

#     def __str__(self):
#         return f"{self.assignment.assignment_name} - {self.document.document_name} - {self.employee.full_name} - {self.status}"


from django.db import models
from django.utils import timezone
from userauth.models import User


class AssignmentDocumentSubmission(models.Model):
    SUBMISSION_STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Submitted', 'Submitted'),
        ('Returned', 'Returned'),
    )

    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name="document_submissions"
    )

    work_service = models.ForeignKey(   # ✅ NEW FIELD
        WorkService,
        on_delete=models.CASCADE,
        related_name="document_submissions"
    )

    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="submissions"
    )

    employee = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="document_submissions",
        null=True, blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=SUBMISSION_STATUS_CHOICES,
        default='Pending'
    )

    submitted_date = models.DateTimeField(null=True, blank=True)
    return_date = models.DateTimeField(null=True, blank=True)
    return_reason = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "assignment_document_submissions"
        unique_together = ('assignment', 'work_service', 'document', 'employee')  # ✅ UPDATED

    def __str__(self):
        return f"{self.assignment.assignment_name} - {self.work_service.service_name} - {self.document.document_name} - {self.employee.full_name} - {self.status}"

###############################################################################################


# from django.db import models
# from django.utils import timezone
# from .models import Assignment
# from userauth.models import User

# class AssignmentChatMessage(models.Model):

#     assignment = models.ForeignKey(
#         Assignment,
#         on_delete=models.CASCADE,
#         related_name="chat_messages"
#     )

#     sender = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name="sent_assignment_messages"
#     )

#     message = models.TextField(blank=True)

#     parent = models.ForeignKey(
#         "self",
#         null=True,
#         blank=True,
#         on_delete=models.CASCADE,
#         related_name="replies"
#     )

#     seen_by = models.ManyToManyField(
#         User,
#         blank=True,
#         related_name="seen_assignment_messages"
#     )

#     created_at = models.DateTimeField(default=timezone.now)

#     class Meta:
#         db_table = "assignment_chat_messages"
#         ordering = ["created_at"]

#     def __str__(self):
#         return f"{self.assignment_id} - {self.sender.full_name}"

from django.db import models
from django.utils import timezone
from .models import Assignment, WorkService   # import WorkService
from userauth.models import User


class AssignmentChatMessage(models.Model):

    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name="chat_messages"
    )

    work_service = models.ForeignKey(   # ✅ NEW FIELD
        WorkService,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="chat_messages"
    )

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_assignment_messages"
    )

    message = models.TextField(blank=True)

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="replies"
    )

    seen_by = models.ManyToManyField(
        User,
        blank=True,
        related_name="seen_assignment_messages"
    )

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = "assignment_chat_messages"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.assignment_id} - {self.sender.full_name}"


class ChatAttachment(models.Model):
    message = models.ForeignKey(
        AssignmentChatMessage,
        on_delete=models.CASCADE,
        related_name="attachments"
    )
    file = models.FileField(upload_to="chat_files/")
    file_name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('assignment', 'Assignment'),
        ('work_update', 'Work Update'),
        ('birthday', 'Birthday'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        default='assignment'
    )
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Related objects
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications"
    )
    
    work = models.ForeignKey(
        Work,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications"
    )
    
    employee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications_about_employee"
    )
    
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "notifications"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.full_name}"


class EmployeeDailyRemark(models.Model):
    employee = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="daily_remarks"
    )
    message = models.TextField()
    date = models.DateField(default=timezone.now)  # The target work date
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "employee_daily_remarks"
        ordering = ['created_at']

    def __str__(self):
        return f"{self.employee.full_name} - {self.date}"


####################################################################################################
# RECURRING WORK ASSIGNMENT MODEL
####################################################################################################

class RecurringWorkAssignment(models.Model):
    """
    Tracks which employees are assigned to recurring work services for a specific assignment.
    When is_recurring=True, this model records the assignment so monthly works can be auto-generated.
    """
    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name="recurring_work_assignments"
    )

    work_service = models.ForeignKey(
        WorkService,
        on_delete=models.CASCADE,
        related_name="recurring_assignments"
    )

    # Store the employees for this recurring assignment
    assigned_employees = models.ManyToManyField(
        User,
        related_name="recurring_work_assignments"
    )

    # Work details to be copied each month
    price = models.DecimalField(max_digits=10, decimal_places=2)
    advance_payment = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    work_mode = models.CharField(
        max_length=10,
        choices=Work.WORK_MODE_CHOICES
    )

    # Track the last month when works were created, use None if never created
    last_work_created_month = models.DateField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "recurring_work_assignments"
        unique_together = ('assignment', 'work_service')
        ordering = ['-created_at']

    def __str__(self):
        return f"Recurring: {self.assignment.assignment_name} - {self.work_service.service_name}"


# ============================= SMS MODELS =============================

class SMSMessage(models.Model):
    """Store bulk/birthday SMS messages"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]
    
    TYPE_CHOICES = [
        ('bulk', 'Bulk Message'),
        ('birthday', 'Birthday Message'),
    ]
    
    message_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    message_content = models.TextField()
    recipients = models.ManyToManyField('userauth.User', related_name='received_sms')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    sent_count = models.IntegerField(default=0)
    failed_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    created_by = models.ForeignKey('userauth.User', on_delete=models.SET_NULL, null=True, 
                                   related_name='sent_sms_messages', blank=True)

    class Meta:
        db_table = "sms_messages"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.message_type.upper()} - {self.created_at.date()}"


class SMSLog(models.Model):
    """Track individual SMS delivery"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('delivered', 'Delivered'),
    ]
    
    sms_message = models.ForeignKey(SMSMessage, on_delete=models.CASCADE, 
                                    related_name='logs')
    recipient = models.ForeignKey('userauth.User', on_delete=models.CASCADE)
    recipient_phone = models.CharField(max_length=15)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    external_id = models.CharField(max_length=255, null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sms_logs"
        ordering = ['-created_at']

    def __str__(self):
        return f"To {self.recipient.full_name} - {self.status}"