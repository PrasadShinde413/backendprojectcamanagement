from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import datetime

from master.models import SMSMessage, User
from master.sms.service import SMSService
from master.sms_serializers import (
    SendBulkSMSSerializer, 
    SMSMessageListSerializer, 
    SMSMessageDetailSerializer
)


class SendBulkSMSAPIView(APIView):
    """Send bulk SMS to employees/clients"""
    
    def post(self, request):
        serializer = SendBulkSMSSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        message = serializer.validated_data['message']
        recipient_type = serializer.validated_data['recipient_type']
        recipients_ids = serializer.validated_data.get('recipients', [])
        
        # Get recipients based on type
        if recipients_ids:
            # Specific recipients selected
            recipients = User.objects.filter(id__in=recipients_ids, is_active=True)
        else:
            # Get all active users
            recipients = User.objects.filter(is_active=True)
        
        if not recipients.exists():
            return Response(
                {'error': 'No recipients found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Send SMS
        try:
            sms_service = SMSService()
            sms_msg = sms_service.send_bulk_message(
                recipients=list(recipients),
                message=message,
                message_type='bulk',
                created_by=request.user if hasattr(request, 'user') and request.user.is_authenticated else None
            )
            
            return Response({
                'message': 'SMS sent successfully',
                'sms_id': sms_msg.id,
                'total_recipients': sms_msg.recipients.count(),
                'sent_count': sms_msg.sent_count,
                'failed_count': sms_msg.failed_count,
                'status': sms_msg.status
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SendBirthdaySMSAPIView(APIView):
    """Check for birthdays today and send SMS automatically"""
    
    def post(self, request):
        try:
            sms_service = SMSService()
            result = sms_service.send_birthday_sms_today()
            
            if result['success']:
                return Response(result, status=status.HTTP_201_CREATED)
            else:
                return Response(result, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SMSHistoryAPIView(APIView):
    """Get SMS history with pagination"""
    
    def get(self, request):
        limit = int(request.query_params.get('limit', 50))
        offset = int(request.query_params.get('offset', 0))
        
        messages = SMSMessage.objects.all()[offset:offset+limit]
        total = SMSMessage.objects.count()
        
        serializer = SMSMessageListSerializer(messages, many=True)
        
        return Response({
            'message': 'SMS history retrieved successfully',
            'total': total,
            'limit': limit,
            'offset': offset,
            'data': serializer.data
        }, status=status.HTTP_200_OK)


class SMSDetailAPIView(APIView):
    """Get SMS details with all logs"""
    
    def get(self, request, sms_id):
        try:
            sms_msg = SMSMessage.objects.get(id=sms_id)
        except SMSMessage.DoesNotExist:
            return Response(
                {'error': 'SMS not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = SMSMessageDetailSerializer(sms_msg)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SMSStatsAPIView(APIView):
    """Get SMS statistics"""
    
    def get(self, request):
        total_messages = SMSMessage.objects.count()
        bulk_messages = SMSMessage.objects.filter(message_type='bulk').count()
        birthday_messages = SMSMessage.objects.filter(message_type='birthday').count()
        
        total_sent = sum(msg.sent_count for msg in SMSMessage.objects.all())
        total_failed = sum(msg.failed_count for msg in SMSMessage.objects.all())
        
        # Today's SMS
        today = datetime.now().date()
        today_messages = SMSMessage.objects.filter(created_at__date=today).count()
        
        return Response({
            'total_messages': total_messages,
            'bulk_messages': bulk_messages,
            'birthday_messages': birthday_messages,
            'total_sent': total_sent,
            'total_failed': total_failed,
            'today_messages': today_messages,
            'success_rate': f"{(total_sent / (total_sent + total_failed) * 100) if (total_sent + total_failed) > 0 else 0:.2f}%"
        }, status=status.HTTP_200_OK)
