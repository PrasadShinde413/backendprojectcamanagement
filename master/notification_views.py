from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone

from .models import Notification
from .notification_serializers import NotificationSerializer
from .notification_utils import mark_notification_as_read, get_unread_notifications_count
from userauth.models import User


class NotificationListAPIView(APIView):
    """Get all notifications for the logged-in user"""
    def get(self, request):
        try:
            # Get the current user from request
            user_id = request.query_params.get('user_id') or request.user.id
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        notifications = Notification.objects.filter(user=user).order_by('-created_at')
        serializer = NotificationSerializer(notifications, many=True)
        
        return Response({
            "count": notifications.count(),
            "unread_count": notifications.filter(is_read=False).count(),
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class UnreadNotificationsAPIView(APIView):
    """Get only unread notifications for the logged-in user"""
    def get(self, request):
        try:
            user_id = request.query_params.get('user_id') or request.user.id
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        notifications = Notification.objects.filter(
            user=user,
            is_read=False
        ).order_by('-created_at')
        serializer = NotificationSerializer(notifications, many=True)
        
        return Response({
            "count": notifications.count(),
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class NotificationDetailAPIView(APIView):
    """Get a single notification"""
    def get(self, request, notification_id):
        try:
            notification = Notification.objects.get(id=notification_id)
        except Notification.DoesNotExist:
            return Response(
                {"error": "Notification not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = NotificationSerializer(notification)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NotificationMarkAsReadAPIView(APIView):
    """Mark a notification as read"""
    def put(self, request, notification_id):
        try:
            notification = Notification.objects.get(id=notification_id)
        except Notification.DoesNotExist:
            return Response(
                {"error": "Notification not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        mark_notification_as_read(notification)
        serializer = NotificationSerializer(notification)
        
        return Response({
            "message": "Notification marked as read",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class NotificationMarkAllAsReadAPIView(APIView):
    """Mark all unread notifications as read for a user"""
    def put(self, request):
        try:
            user_id = request.data.get('user_id') or request.user.id
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        unread_notifications = Notification.objects.filter(
            user=user,
            is_read=False
        )
        
        count = unread_notifications.count()
        
        # Update all unread notifications
        unread_notifications.update(
            is_read=True,
            read_at=timezone.now()
        )
        
        return Response({
            "message": f"Marked {count} notifications as read",
            "count_updated": count
        }, status=status.HTTP_200_OK)


class NotificationDeleteAPIView(APIView):
    """Delete a notification"""
    def delete(self, request, notification_id):
        try:
            notification = Notification.objects.get(id=notification_id)
        except Notification.DoesNotExist:
            return Response(
                {"error": "Notification not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        notification.delete()
        
        return Response({
            "message": "Notification deleted successfully"
        }, status=status.HTTP_200_OK)


class NotificationDeleteAllAPIView(APIView):
    """Delete all notifications for a user"""
    def delete(self, request):
        try:
            user_id = request.data.get('user_id') or request.user.id
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        notifications = Notification.objects.filter(user=user)
        count = notifications.count()
        notifications.delete()
        
        return Response({
            "message": f"Deleted {count} notifications",
            "count_deleted": count
        }, status=status.HTTP_200_OK)


class UnreadNotificationCountAPIView(APIView):
    """Get unread notification count for a user"""
    def get(self, request):
        try:
            user_id = request.query_params.get('user_id') or request.user.id
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        unread_count = get_unread_notifications_count(user)
        
        return Response({
            "user_id": user.id,
            "user_name": user.full_name,
            "unread_count": unread_count
        }, status=status.HTTP_200_OK)
