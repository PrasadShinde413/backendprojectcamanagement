from django.urls import path, include
from .views import (
    
    AssignmentChatListAPIView,
    AssignmentChatSeenAPIView,
    AssignmentChatSendAPIView,
    AssignmentDocumentsAdminAPIView,
    BulkWorkByAssignmentAPIView,
    BulkWorkCreateAPIView,
    ClientCreateAPIView,
    ClientListAPIView,
    ClientDetailAPIView,
    ClientUpdateAPIView,
    ClientSoftDeleteAPIView,
    DocumentSummaryAPIView,
    EmployeeAssignmentDocumentsAPIView,
    EmployeeDailyChatHistoryAPIView,
    EmployeeDailyChatSendAPIView,
    EmployeeDiaryAPIView,
    ReturnDocumentsAPIView,
    SubmitDocumentsAPIView,
    UpdateAssignmentWorkStatusAPIView,
    UserAssignmentListAPIView,
    UserDeleteAPIView,
    WorkListByAssignmentAPIView,WorkServiceCreateAPIView,
    WorkServiceListAPIView,
    WorkServiceDetailAPIView,
    WorkServiceUpdateAPIView,
    WorkServiceSoftDeleteAPIView,AssignmentCreateAPIView,
    AssignmentDetailAPIView,
    AssignmentListAPIView,
    AssignmentSoftDeleteAPIView,
    AssignmentUpdateAPIView,
    AssignmentDetailFullAPIView,
    AssignmentListDetailAPIView,
    BulkWorkUpdateByAssignmentAPIView,
    GetAssignmentPendingDocumentsAPIView,
    SubmitAssignmentDocumentsAPIView,
    ReturnAssignmentDocumentsAPIView,
    AssignmentDocumentSubmissionHistoryAPIView,
    WorkCreateAPIView,
    WorkDetailAPIView,
    WorkSoftDeleteAPIView,
    WorkUpdateAPIView,
    ClientCountDashboardAPIView,
    AssignmentStatusCountDashboardAPIView,
    DocumentSubmissionStatusCountDashboardAPIView,
    WorkStatusCountDashboardAPIView,
    EmployeeWorkCountDashboardAPIView,
    AssignmentDocumentWorkServiceHistoryAPIView,
)

from .notification_views import (
    NotificationListAPIView,
    UnreadNotificationsAPIView,
    NotificationDetailAPIView,
    NotificationMarkAsReadAPIView,
    NotificationMarkAllAsReadAPIView,
    NotificationDeleteAPIView,
    NotificationDeleteAllAPIView,
    UnreadNotificationCountAPIView,
)


urlpatterns = [
    path('create/', ClientCreateAPIView.as_view()),
    path('client-list/', ClientListAPIView.as_view()),
    path('client/<int:client_id>/', ClientDetailAPIView.as_view()),
    path('update/<int:client_id>/', ClientUpdateAPIView.as_view()),
    path('status/<int:client_id>/', ClientSoftDeleteAPIView.as_view()),

    path('work-service/create/', WorkServiceCreateAPIView.as_view()),
    path('work-service/', WorkServiceListAPIView.as_view()),
    path('work-service/<int:id>/', WorkServiceDetailAPIView.as_view()),
    path('work-service/update/<int:id>/', WorkServiceUpdateAPIView.as_view()),
    path('work-service/delete/<int:id>/', WorkServiceSoftDeleteAPIView.as_view()),

    path('assignment/create/', AssignmentCreateAPIView.as_view()),
    path('assignment-list/', AssignmentListDetailAPIView.as_view()),
    path('assignment/<int:assignment_id>/', AssignmentListAPIView.as_view()),
    path('assignment/<int:id>/', AssignmentDetailAPIView.as_view()),
    path('assignment/details/<int:id>/', AssignmentDetailFullAPIView.as_view()),
    path('assignment/update/<int:id>/', AssignmentUpdateAPIView.as_view()),
    path('assignment/delete/<int:id>/', AssignmentSoftDeleteAPIView.as_view()), 
    path('works/bulk-create/', BulkWorkCreateAPIView.as_view()),
    path(
    "bulk-work/<int:assignment_id>/",
    BulkWorkByAssignmentAPIView.as_view(),
    name="bulk-work-by-assignment"
),
    path(
    "bulk-work/<int:assignment_id>/",
    BulkWorkUpdateByAssignmentAPIView.as_view(),
    name="bulk-work-update-by-assignment"
    ),
    path('work/create/', WorkCreateAPIView.as_view()),
    path('work/assignment/<int:assignment_id>/', WorkListByAssignmentAPIView.as_view()),
    path('work/<int:id>/', WorkDetailAPIView.as_view()),
    path('work/update/<int:id>/', WorkUpdateAPIView.as_view()),
    path('work/delete/<int:id>/', WorkSoftDeleteAPIView.as_view()),

    path('assignment/<int:assignment_id>/documents/', GetAssignmentPendingDocumentsAPIView.as_view()),
    path('assignment/<int:assignment_id>/documents/submit/', SubmitAssignmentDocumentsAPIView.as_view()),
    path('assignment/<int:assignment_id>/documents/return/', ReturnAssignmentDocumentsAPIView.as_view()),
    path('assignment/<int:assignment_id>/documents/history/', AssignmentDocumentSubmissionHistoryAPIView.as_view()),
    path('assignment/user/<int:user_id>/', UserAssignmentListAPIView.as_view(), name='user-assignment-list'),
    path('assignment/<int:assignment_id>/documents/history/<int:work_service_id>/', AssignmentDocumentWorkServiceHistoryAPIView.as_view(), name='assignment-workservice-doc-history'),

    # Dashboard APIs
    path('dashboard/clients-count/', ClientCountDashboardAPIView.as_view()),
    path('dashboard/assignments-count/', AssignmentStatusCountDashboardAPIView.as_view()),
    path('dashboard/documents-count/', DocumentSubmissionStatusCountDashboardAPIView.as_view()),
    path('dashboard/works-count/', WorkStatusCountDashboardAPIView.as_view()),
    path('dashboard/employee-works-count/', EmployeeWorkCountDashboardAPIView.as_view()),


    path('send_comment/', AssignmentChatSendAPIView.as_view()),
    path( "assignment-chat/<int:assignment_id>/<int:work_service_id>/", AssignmentChatListAPIView.as_view()),
    path('seen/<int:message_id>/', AssignmentChatSeenAPIView.as_view()),

    path('employee-diary/<int:employee_id>/', EmployeeDiaryAPIView.as_view()),
    path('document-summary/', DocumentSummaryAPIView.as_view()),
    path('update-status/', UpdateAssignmentWorkStatusAPIView.as_view(), name='update-assignment-work-status'),

    path('employee/<int:assignment_id>/<int:employee_id>/', EmployeeAssignmentDocumentsAPIView.as_view()),
    path('users/delete/<int:user_id>/', UserDeleteAPIView.as_view(), name='delete-user'),###delet api
    path('submit/<int:assignment_id>/', SubmitDocumentsAPIView.as_view()),
    path('return/<int:assignment_id>/', ReturnDocumentsAPIView.as_view()),
    path('sumitted_documents/<int:assignment_id>/', AssignmentDocumentsAdminAPIView.as_view()),
    path('assignment-documents/<int:assignment_id>/', AssignmentDocumentsAdminAPIView.as_view(), name='assignment-documents-admin'),

    # Notification URLs
    path('notifications/', NotificationListAPIView.as_view(), name='notification-list'),
    path('notifications/unread/', UnreadNotificationsAPIView.as_view(), name='unread-notifications'),
    path('notifications/<int:notification_id>/', NotificationDetailAPIView.as_view(), name='notification-detail'),
    path('notifications/<int:notification_id>/read/', NotificationMarkAsReadAPIView.as_view(), name='mark-notification-read'),
    path('notifications/read-all/', NotificationMarkAllAsReadAPIView.as_view(), name='mark-all-notifications-read'),
    path('notifications/<int:notification_id>/delete/', NotificationDeleteAPIView.as_view(), name='delete-notification'),
    path('notifications/delete-all/', NotificationDeleteAllAPIView.as_view(), name='delete-all-notifications'),
    path('notifications/unread-count/', UnreadNotificationCountAPIView.as_view(), name='unread-count'),

    # SMS URLs
    path('sms/', include('master.sms_urls')),

    path('employee-diary/chat/send/', EmployeeDailyChatSendAPIView.as_view(), name='send-daily-remark'),
    path('employee-diary/chat/history/<int:employee_id>/', EmployeeDailyChatHistoryAPIView.as_view(), name='daily-remark-history'),

]
