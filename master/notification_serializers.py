from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    assignment_name = serializers.CharField(source='assignment.assignment_name', read_only=True, allow_null=True)
    work_service_name = serializers.CharField(source='work.work_service.service_name', read_only=True, allow_null=True)
    employee_name = serializers.CharField(source='employee.full_name', read_only=True, allow_null=True)

    class Meta:
        model = Notification
        fields = [
            'id',
            'user',
            'user_name',
            'notification_type',
            'title',
            'message',
            'assignment',
            'assignment_name',
            'work',
            'work_service_name',
            'employee',
            'employee_name',
            'is_read',
            'read_at',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
