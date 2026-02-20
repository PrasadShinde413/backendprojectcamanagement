from django.urls import path
from .sms_views import (
    SendBulkSMSAPIView,
    SendBirthdaySMSAPIView,
    SMSHistoryAPIView,
    SMSDetailAPIView,
    SMSStatsAPIView
)

urlpatterns = [
    path('send-bulk/', SendBulkSMSAPIView.as_view(), name='send-bulk-sms'),
    path('send-birthdays/', SendBirthdaySMSAPIView.as_view(), name='send-birthday-sms'),
    path('history/', SMSHistoryAPIView.as_view(), name='sms-history'),
    path('detail/<int:sms_id>/', SMSDetailAPIView.as_view(), name='sms-detail'),
    path('stats/', SMSStatsAPIView.as_view(), name='sms-stats'),
]
