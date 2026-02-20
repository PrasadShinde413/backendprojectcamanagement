from rest_framework import serializers
from master.models import SMSMessage, SMSLog
from userauth.models import User


class SMSLogSerializer(serializers.ModelSerializer):
    recipient_name = serializers.CharField(source='recipient.full_name', read_only=True)
    
    class Meta:
        model = SMSLog
        fields = ['id', 'recipient_name', 'recipient_phone', 'status', 
                  'error_message', 'sent_at', 'created_at']


class SendBulkSMSSerializer(serializers.Serializer):
    message = serializers.CharField(max_length=160, min_length=1)
    recipient_type = serializers.ChoiceField(choices=['employees', 'clients', 'all'])
    recipients = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=True
    )
    
    def validate_recipients(self, value):
        if value:
            # Ensure all are valid user IDs
            for user_id in value:
                if not User.objects.filter(id=user_id, is_active=True).exists():
                    raise serializers.ValidationError(f"User {user_id} not found or inactive")
        return value


class SMSMessageListSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True, allow_null=True)
    recipient_count = serializers.SerializerMethodField()
    
    class Meta:
        model = SMSMessage
        fields = ['id', 'message_type', 'message_content', 'status', 
                  'sent_count', 'failed_count', 'recipient_count', 
                  'created_at', 'sent_at', 'created_by_name']
    
    def get_recipient_count(self, obj):
        return obj.recipients.count()


class SMSMessageDetailSerializer(serializers.ModelSerializer):
    logs = SMSLogSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.full_name', read_only=True, allow_null=True)
    recipient_list = serializers.SerializerMethodField()
    
    class Meta:
        model = SMSMessage
        fields = ['id', 'message_type', 'message_content', 'status', 
                  'sent_count', 'failed_count', 'created_at', 'sent_at', 
                  'created_by_name', 'recipient_list', 'logs']
    
    def get_recipient_list(self, obj):
        return list(obj.recipients.values_list('id', 'full_name', 'phone_no'))
