"""
Notification utility functions for CA Firm application
"""
from datetime import datetime
from django.utils import timezone
from .models import Notification, Work, Assignment
from userauth.models import User


def create_assignment_notification(work, assigned_employees):
    """
    Create notification when a work is assigned to employees
    """
    assignment = work.assignment
    for employee in assigned_employees:
        Notification.objects.create(
            user=employee,
            notification_type='assignment',
            title=f'New Assignment: {assignment.assignment_name}',
            message=f'You have been assigned to work on {work.work_service.service_name} for client {assignment.client.client_name}',
            assignment=assignment,
            work=work,
            employee=employee
        )


def create_work_update_notification(work, updated_by):
    """
    Create notification to admin when employee updates work status/progress
    """
    # Get all admin users
    admins = User.objects.filter(role='Admin', is_active=True)
    
    for admin in admins:
        Notification.objects.create(
            user=admin,
            notification_type='work_update',
            title=f'Work Status Update: {work.work_service.service_name}',
            message=f'{updated_by.full_name} has updated the status to {work.status} for {work.assignment.assignment_name}',
            assignment=work.assignment,
            work=work,
            employee=updated_by
        )


def create_birthday_notifications(birthday_user):
    """
    Create birthday notification for all active users
    """
    all_users = User.objects.filter(is_active=True)
    
    for user in all_users:
        if user.id != birthday_user.id:  # Don't notify the birthday person
            Notification.objects.create(
                user=user,
                notification_type='birthday',
                title=f"🎂 {birthday_user.full_name}'s Birthday!",
                message=f"Today is {birthday_user.full_name}'s birthday! Please send your wishes.",
                employee=birthday_user
            )


def check_and_send_birthday_notifications():
    """
    Check if any user has birthday today and send notifications
    Called from a periodic task/celery beat
    """
    today = datetime.now().date()
    birthday_users = User.objects.filter(
        birthdate__month=today.month,
        birthdate__day=today.day,
        is_active=True
    )
    
    for user in birthday_users:
        create_birthday_notifications(user)


def mark_notification_as_read(notification):
    """
    Mark a notification as read
    """
    notification.is_read = True
    notification.read_at = timezone.now()
    notification.save()


def get_unread_notifications_count(user):
    """
    Get count of unread notifications for a user
    """
    return Notification.objects.filter(user=user, is_read=False).count()


def get_user_notifications(user, limit=None, unread_only=False):
    """
    Get notifications for a user
    """
    notifications = Notification.objects.filter(user=user)
    
    if unread_only:
        notifications = notifications.filter(is_read=False)
    
    notifications = notifications.order_by('-created_at')
    
    if limit:
        notifications = notifications[:limit]
    
    return notifications
