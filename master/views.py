from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from userauth.models import User
from .models import Assignment, AssignmentChatMessage, ChatAttachment, Client, Document, EmployeeDailyRemark, Work,WorkService
from .serializers import AssignmentSerializer, ClientSerializer, EmployeeDailyRemarkSerializer, WorkSerializer, WorkServiceSerializer, BulkWorkCreateSerializer, WorkServiceCreateSerializer, AssignmentDetailSerializer

class ClientCreateAPIView(APIView):
    def post(self, request):
        serializer = ClientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Client created successfully"},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ClientListAPIView(APIView):
    def get(self, request):
        clients = Client.objects.filter(is_active=True)
        serializer = ClientSerializer(clients, many=True)
        return Response({
            "count": clients.count(),
            "data": serializer.data
        }, status=status.HTTP_200_OK)

class ClientDetailAPIView(APIView):
    def get(self, request, client_id):
        try:
            client = Client.objects.get(id=client_id, is_active=True)
        except Client.DoesNotExist:
            return Response(
                {"error": "Client not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ClientSerializer(client)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ClientUpdateAPIView(APIView):
    def put(self, request, client_id):
        try:
            client = Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            return Response(
                {"error": "Client not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ClientSerializer(
            client, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Client updated successfully"},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ClientSoftDeleteAPIView(APIView):
    def put(self, request, client_id):
        try:
            client = Client.objects.get(id=client_id)
        except Client.DoesNotExist:
            return Response(
                {"error": "Client not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        client.is_active = not client.is_active
        client.save()

        return Response({
            "message": "Client status updated",
            "is_active": client.is_active
        }, status=status.HTTP_200_OK)


#############################################################################################


# class AssignmentCreateAPIView(APIView):
#     def post(self, request):
#         serializer = AssignmentSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({"message": "Assignment created"}, status=201)
#         return Response(serializer.errors, status=400)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import AssignmentSerializer


class AssignmentCreateAPIView(APIView):
    def post(self, request):
        serializer = AssignmentSerializer(data=request.data)
        if serializer.is_valid():
            assignment = serializer.save()

            return Response(
                {
                    "message": "Assignment created successfully",
                    "assignment_id": assignment.id,
                    "assignment": AssignmentSerializer(assignment).data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AssignmentListAPIView(APIView):
    def get(self, request):
        data = Assignment.objects.filter(is_deleted=False)
        serializer = AssignmentSerializer(data, many=True)
        return Response(serializer.data)


class AssignmentDetailAPIView(APIView):
    def get(self, request, id):
        assignment = Assignment.objects.filter(id=id, is_deleted=False).first()
        if not assignment:
            return Response({"error": "Not found"}, status=404)
        serializer = AssignmentSerializer(assignment)
        return Response(serializer.data)


# class AssignmentUpdateAPIView(APIView):
#     def put(self, request, id):
#         assignment = Assignment.objects.filter(id=id).first()
#         if not assignment:
#             return Response({"error": "Not found"}, status=404)

#         serializer = AssignmentSerializer(
#             assignment, data=request.data, partial=True
#         )
#         if serializer.is_valid():
#             serializer.save()
#             return Response({"message": "Updated"})
#         return Response(serializer.errors, status=400)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Assignment
from .serializers import AssignmentSerializer


class AssignmentUpdateAPIView(APIView):
    def put(self, request, id):

        assignment = Assignment.objects.filter(id=id).first()
        if not assignment:
            return Response(
                {"error": "Assignment not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = AssignmentSerializer(
            assignment,
            data=request.data,
            partial=True   # allows updating only passed fields
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Assignment updated successfully",
                    "assignment_id": assignment.id
                },
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AssignmentSoftDeleteAPIView(APIView):
    def put(self, request, id):
        assignment = Assignment.objects.filter(id=id).first()
        if not assignment:
            return Response({"error": "Not found"}, status=404)

        assignment.is_deleted = True
        assignment.save()
        return Response({"message": "Assignment deleted"})


class AssignmentDetailFullAPIView(APIView):
    def get(self, request, id):
        try:
            assignment = Assignment.objects.prefetch_related(
                'works__work_service__documents',
                'works__assigned_employees',
                'client'
            ).get(id=id, is_deleted=False)
        except Assignment.DoesNotExist:
            return Response(
                {"error": "Assignment not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = AssignmentDetailSerializer(assignment)
        return Response({
            "message": "Assignment details retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class AssignmentListDetailAPIView(APIView):
    def get(self, request):
        assignment_id = request.query_params.get('assignment_id')
        
        if assignment_id:
            # Get specific assignment by ID
            try:
                assignments = Assignment.objects.filter(id=assignment_id, is_deleted=False).prefetch_related(
                    'works__work_service__documents',
                    'works__assigned_employees',
                    'client'
                )
                
                if not assignments.exists():
                    return Response(
                        {"error": "Assignment not found"},
                        status=status.HTTP_404_NOT_FOUND
                    )
                
                serializer = AssignmentDetailSerializer(assignments, many=True)
                return Response({
                    "message": "Assignment details retrieved successfully",
                    "count": assignments.count(),
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            except ValueError:
                return Response(
                    {"error": "Invalid assignment_id"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            # Get all assignments
            assignments = Assignment.objects.filter(is_deleted=False).prefetch_related(
                'works__work_service__documents',
                'works__assigned_employees',
                'client'
            )
            
            serializer = AssignmentDetailSerializer(assignments, many=True)
            return Response({
                "message": "All assignment details retrieved successfully",
                "count": assignments.count(),
                "data": serializer.data
            }, status=status.HTTP_200_OK)


class WorkServiceCreateAPIView(APIView):
    def post(self, request):
        serializer = WorkServiceCreateSerializer(data=request.data)
        if serializer.is_valid():
            work_service = serializer.save()
            # Return full work service with documents
            response_serializer = WorkServiceSerializer(work_service)
            return Response({
                "message": "Work service created successfully",
                "data": response_serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WorkServiceListAPIView(APIView):
    def get(self, request):
        services = WorkService.objects.filter(is_deleted=False).prefetch_related('documents')
        serializer = WorkServiceSerializer(services, many=True)
        return Response({
            "count": services.count(),
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class WorkServiceDetailAPIView(APIView):
    def get(self, request, id):
        try:
            service = WorkService.objects.prefetch_related('documents').get(id=id, is_deleted=False)
        except WorkService.DoesNotExist:
            return Response(
                {"error": "Work service not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = WorkServiceSerializer(service)
        return Response(serializer.data, status=status.HTTP_200_OK)


# class WorkServiceUpdateAPIView(APIView):
#     def put(self, request, id):
#         try:
#             service = WorkService.objects.prefetch_related('documents').get(id=id, is_deleted=False)
#         except WorkService.DoesNotExist:
#             return Response(
#                 {"error": "Work service not found"},
#                 status=status.HTTP_404_NOT_FOUND
#             )

#         serializer = WorkServiceSerializer(
#             service, data=request.data, partial=True
#         )

#         if serializer.is_valid():
#             serializer.save()
#             return Response({
#                 "message": "Work service updated successfully",
#                 "data": serializer.data
#             }, status=status.HTTP_200_OK)

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class WorkServiceUpdateAPIView(APIView):
    def put(self, request, id):
        try:
            service = WorkService.objects.prefetch_related('documents').get(
                id=id, is_deleted=False
            )
        except WorkService.DoesNotExist:
            return Response(
                {"error": "Work service not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = WorkServiceSerializer(
            service, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Work service updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class WorkServiceSoftDeleteAPIView(APIView):
    def put(self, request, id):
        try:
            service = WorkService.objects.get(id=id)
        except WorkService.DoesNotExist:
            return Response(
                {"error": "Work service not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        service.is_deleted = True
        service.save()

        return Response(
            {"message": "Work service deleted successfully"},
            status=status.HTTP_200_OK
        )

##############################################################################################

class WorkCreateAPIView(APIView):
    def post(self, request):
        serializer = WorkSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Work created successfully"},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

######################################################################################################

# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from django.db import transaction

# from .serializers import BulkWorkSerializer


# class BulkWorkCreateAPIView(APIView):
#     def post(self, request):

#         if not isinstance(request.data, list):
#             return Response(
#                 {"error": "Expected a list of work objects"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         serializer = BulkWorkSerializer(data=request.data, many=True)

#         if serializer.is_valid():
#             with transaction.atomic():
#                 works = serializer.save()

#             return Response(
#                 {
#                     "message": "Works created successfully",
#                     "total_created": len(works)
#                 },
#                 status=status.HTTP_201_CREATED
#             )

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from django.db import transaction

# from .serializers import BulkWorkSerializer


# class BulkWorkCreateAPIView(APIView):
#     def post(self, request):

#         if not isinstance(request.data, list):
#             return Response(
#                 {"error": "Expected a list of work objects"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         serializer = BulkWorkSerializer(data=request.data, many=True)

#         if serializer.is_valid():
#             with transaction.atomic():
#                 works = serializer.save()
                
#                 # 🔔 Create notifications for assigned employees
#                 from .notification_utils import create_assignment_notification
#                 for work in works:
#                     assigned_employees = work.assigned_employees.all()
#                     if assigned_employees.exists():
#                         create_assignment_notification(work, assigned_employees)

#             # 🔹 Calculate totals
#             total_price = sum(work.price or 0 for work in works)
#             total_advance_payment = sum(work.advance_payment or 0 for work in works)
#             balance_amount = total_price - total_advance_payment

#             return Response(
#                 {
#                     "message": "Works created successfully",
#                     "total_created": len(works),
#                     "total_price": total_price,
#                     "total_advance_payment": total_advance_payment,
#                     "balance_amount": balance_amount
#                 },
#                 status=status.HTTP_201_CREATED
#             )

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.utils import timezone

from .serializers import BulkWorkSerializer
from .models import AssignmentDocumentSubmission


class BulkWorkCreateAPIView(APIView):
    def post(self, request):

        if not isinstance(request.data, list):
            return Response(
                {"error": "Expected a list of work objects"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = BulkWorkSerializer(data=request.data, many=True)

        if serializer.is_valid():
            with transaction.atomic():
                works = serializer.save()

                # 🔔 Notifications
                from .notification_utils import create_assignment_notification
                for work in works:
                    assigned_employees = work.assigned_employees.all()
                    if assigned_employees.exists():
                        create_assignment_notification(work, assigned_employees)

                    # 🔹 STORE SUBMITTED DOCUMENTS (NEW LOGIC)
                    document_ids = getattr(work, "_document_ids", [])

                    submissions = [
                        AssignmentDocumentSubmission(
                            assignment_id=work.assignment_id,
                            work_service_id=work.work_service_id,
                            document_id=doc_id,
                            employee_id=None,
                            status="Returned",
                            return_date=timezone.now(),
                            return_reason=""
                        )
                        for doc_id in document_ids
                    ]

                    AssignmentDocumentSubmission.objects.bulk_create(submissions)

                    # 🔄 NEW: HANDLE RECURRING ASSIGNMENTS
                    is_recurring = getattr(work, "_is_recurring", False)
                    if is_recurring and work.work_service.is_recurring:
                        # Get the work_service and check if it's marked as recurring
                        work_service = work.work_service
                        assignment = work.assignment
                        employees = getattr(work, "_employees", list(assigned_employees.values_list('id', flat=True)))
                        
                        # Create or update RecurringWorkAssignment
                        from .models import RecurringWorkAssignment
                        recurring_record, created = RecurringWorkAssignment.objects.update_or_create(
                            assignment=assignment,
                            work_service=work_service,
                            defaults={
                                'price': work.price,
                                'advance_payment': work.advance_payment,
                                'work_mode': work.work_mode,
                                'is_active': True
                            }
                        )
                        
                        # Update the many-to-many employees
                        recurring_record.assigned_employees.set(employees)
                        
                        # Set the current work as the first recurring work
                        work.recurring_assignment = recurring_record
                        from datetime import datetime
                        work.created_for_month = datetime.now().replace(day=1)
                        work.save(update_fields=['recurring_assignment', 'created_for_month'])

            # 🔹 Totals
            total_price = sum(work.price or 0 for work in works)
            total_advance_payment = sum(work.advance_payment or 0 for work in works)
            balance_amount = total_price - total_advance_payment

            return Response(
                {
                    "message": "Works created successfully",
                    "total_created": len(works),
                    "total_price": total_price,
                    "total_advance_payment": total_advance_payment,
                    "balance_amount": balance_amount
                },
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#########################################################################################################
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Work
from .serializers import BulkWorkReadSerializer


class BulkWorkByAssignmentAPIView(APIView):
    def get(self, request, assignment_id):

        works = Work.objects.filter(
            assignment_id=assignment_id,
            is_deleted=False
        )

        if not works.exists():
            return Response(
                {"error": "No work found for this assignment"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = BulkWorkReadSerializer(works, many=True)

        # 🔹 Totals
        total_price = sum(w.price or 0 for w in works)
        total_advance_payment = sum(w.advance_payment or 0 for w in works)
        balance_amount = total_price - total_advance_payment

        return Response(
            {
                "assignment_id": assignment_id,
                "total_works": works.count(),
                "total_price": total_price,
                "total_advance_payment": total_advance_payment,
                "balance_amount": balance_amount,
                "works": serializer.data
            },
            status=status.HTTP_200_OK
        )
##############################################################################################


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction

from .models import Work
from .serializers import BulkWorkSerializer


class BulkWorkUpdateByAssignmentAPIView(APIView):
    def put(self, request, assignment_id):

        if not isinstance(request.data, list):
            return Response(
                {"error": "Expected a list of work objects"},
                status=status.HTTP_400_BAD_REQUEST
            )

        updated_works = []

        with transaction.atomic():
            for item in request.data:
                work_service_id = item.get("work_service")

                if not work_service_id:
                    return Response(
                        {"error": "work_service is required"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                work = Work.objects.filter(
                    assignment_id=assignment_id,
                    work_service_id=work_service_id,
                    is_deleted=False
                ).first()

                if not work:
                    return Response(
                        {
                            "error": f"Work not found for assignment {assignment_id} "
                                     f"and work_service {work_service_id}"
                        },
                        status=status.HTTP_404_NOT_FOUND
                    )

                serializer = BulkWorkSerializer(
                    work,
                    data=item,
                    partial=True
                )

                serializer.is_valid(raise_exception=True)
                old_status = work.status
                updated_work = serializer.save()
                updated_works.append(updated_work)
                
                # 🔔 Create notification if status changed
                if old_status != updated_work.status:
                    from .notification_utils import create_work_update_notification
                    # Get the user who made the update from request
                    updated_by = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
                    if updated_by:
                        create_work_update_notification(updated_work, updated_by)

        # 🔹 Totals
        total_price = sum(w.price or 0 for w in updated_works)
        total_advance_payment = sum(w.advance_payment or 0 for w in updated_works)
        balance_amount = total_price - total_advance_payment

        return Response(
            {
                "message": "Works updated successfully",
                "assignment_id": assignment_id,
                "total_updated": len(updated_works),
                "total_price": total_price,
                "total_advance_payment": total_advance_payment,
                "balance_amount": balance_amount
            },
            status=status.HTTP_200_OK
        )


class WorkListByAssignmentAPIView(APIView):
    def get(self, request, assignment_id):
        works = Work.objects.filter(
            assignment_id=assignment_id,
            is_deleted=False
        )

        serializer = WorkSerializer(works, many=True)
        return Response({
            "count": works.count(),
            "data": serializer.data
        }, status=status.HTTP_200_OK)

class WorkDetailAPIView(APIView):
    def get(self, request, id):
        try:
            work = Work.objects.get(id=id, is_deleted=False)
        except Work.DoesNotExist:
            return Response(
                {"error": "Work not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = WorkSerializer(work)
        return Response(serializer.data, status=status.HTTP_200_OK)


class WorkUpdateAPIView(APIView):
    def put(self, request, id):
        try:
            work = Work.objects.get(id=id)
        except Work.DoesNotExist:
            return Response(
                {"error": "Work not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = WorkSerializer(
            work, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Work updated successfully"},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WorkSoftDeleteAPIView(APIView):
    def put(self, request, id):
        try:
            work = Work.objects.get(id=id)
        except Work.DoesNotExist:
            return Response(
                {"error": "Work not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        work.is_deleted = True
        work.save()

        return Response(
            {"message": "Work deleted successfully"},
            status=status.HTTP_200_OK
        )


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Work
from .serializers import BulkWorkCreateSerializer

class WorkBulkCreateAPIView(APIView):
    def post(self, request):
        """
        Create multiple works under one assignment
        """
        serializer = BulkWorkCreateSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        works = []
        for work_data in serializer.validated_data:
            employees = work_data.pop('assigned_employees')

            work = Work.objects.create(**work_data)  # status auto Pending
            work.assigned_employees.set(employees)
            works.append(work)

        return Response(
            {
                "message": "Works created successfully",
                "total_created": len(works)
            },
            status=status.HTTP_201_CREATED
        )

##############################################################################################
# ASSIGNMENT DOCUMENT SUBMISSION APIs
##############################################################################################

from .models import AssignmentDocumentSubmission
from .serializers import AssignmentDocumentSubmissionSerializer, DocumentSubmitSerializer, DocumentReturnSerializer
from django.utils import timezone


class UserAssignmentListAPIView(APIView):
    def get(self, request, user_id):
        # 1. Validate if the user exists
        user_exists = User.objects.filter(id=user_id, is_active=True).exists()
        if not user_exists:
            return Response(
                {"error": "User not found or inactive"},
                status=status.HTTP_404_NOT_FOUND
            )

        # 2. Filter assignments where any related "Work" has this user in "assigned_employees"
        # We use prefetch_related for performance since the serializer nested data
        assignments = Assignment.objects.filter(
            works__assigned_employees__id=user_id,
            is_deleted=False
        ).prefetch_related(
            'works__work_service__documents',
            'works__assigned_employees',
            'client'
        ).distinct()

        # 3. Serialize and return
        serializer = AssignmentDetailSerializer(assignments, many=True)
        return Response({
            "message": "User assignments retrieved successfully",
            "user_id": user_id,
            "count": assignments.count(),
            "data": serializer.data
        }, status=status.HTTP_200_OK)

class GetAssignmentPendingDocumentsAPIView(APIView):
    """Get all pending documents for an assignment"""
    def get(self, request, assignment_id):
        try:
            assignment = Assignment.objects.get(id=assignment_id, is_deleted=False)
        except Assignment.DoesNotExist:
            return Response(
                {"error": "Assignment not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get all documents from work services in this assignment
        documents = []
        for work in assignment.works.all():
            documents.extend(work.work_service.documents.all())

        # Create submission records if they don't exist
        for document in documents:
            AssignmentDocumentSubmission.objects.get_or_create(
                assignment=assignment,
                document=document,
                defaults={'status': 'Pending'}
            )

        # Get all submission records - only Pending and Submitted status
        submissions = AssignmentDocumentSubmission.objects.filter(
            assignment=assignment,
            status__in=['Pending', 'Submitted']
        ).select_related('document')

        # Separate pending and taken documents
        pending_submissions = submissions.filter(status='Pending')
        taken_submissions = submissions.filter(status='Submitted')
        
        pending_serializer = AssignmentDocumentSubmissionSerializer(pending_submissions, many=True)
        taken_serializer = AssignmentDocumentSubmissionSerializer(taken_submissions, many=True)
        
        # Calculate counts
        pending_count = pending_submissions.count()
        submitted_count = taken_submissions.count()

        return Response({
            "message": "Assignment documents retrieved successfully",
            "assignment_name": assignment.assignment_name,
            "total_documents": submissions.count(),
            "pending_count": pending_count,
            "submitted_count": submitted_count,
            "pending_documents": pending_serializer.data,
            "taken_documents": taken_serializer.data
        }, status=status.HTTP_200_OK)


class SubmitAssignmentDocumentsAPIView(APIView):
    """Submit documents for an assignment"""
    def post(self, request, assignment_id):
        try:
            assignment = Assignment.objects.get(id=assignment_id, is_deleted=False)
        except Assignment.DoesNotExist:
            return Response(
                {"error": "Assignment not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = DocumentSubmitSerializer(
            data=request.data,
            context={'assignment_id': assignment_id}
        )
        
        if serializer.is_valid():
            serializer.save()
            
            # Update assignment status to "In Progress" when documents are submitted
            if assignment.status == 'Pending':
                assignment.status = 'In Progress'
                assignment.save()
            
            # Get updated counts - only Pending and Submitted
            submissions = AssignmentDocumentSubmission.objects.filter(
                assignment=assignment,
                status__in=['Pending', 'Submitted']
            )
            pending_count = submissions.filter(status='Pending').count()
            submitted_count = submissions.filter(status='Submitted').count()
            
            # Get separated data
            pending_submissions = submissions.filter(status='Pending')
            taken_submissions = submissions.filter(status='Submitted')
            
            pending_serializer = AssignmentDocumentSubmissionSerializer(pending_submissions, many=True)
            taken_serializer = AssignmentDocumentSubmissionSerializer(taken_submissions, many=True)
            
            return Response({
                "message": "Documents submitted successfully",
                "assignment_name": assignment.assignment_name,
                "assignment_status": assignment.status,
                "total_documents": submissions.count(),
                "pending_count": pending_count,
                "submitted_count": submitted_count,
                "submitted_documents_count": len(request.data.get('document_ids', [])),
                "pending_documents": pending_serializer.data,
                "taken_documents": taken_serializer.data
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReturnAssignmentDocumentsAPIView(APIView):
    """Return documents for an assignment (mark as inappropriate)"""
    def post(self, request, assignment_id):
        try:
            assignment = Assignment.objects.get(id=assignment_id, is_deleted=False)
        except Assignment.DoesNotExist:
            return Response(
                {"error": "Assignment not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = DocumentReturnSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        document_ids = serializer.validated_data.get('document_ids', [])
        return_reason = serializer.validated_data.get('return_reason', '') or None

        # Update submission records - set back to Pending
        submissions = AssignmentDocumentSubmission.objects.filter(
            assignment=assignment,
            document_id__in=document_ids
        )

        updated_count = 0
        for submission in submissions:
            submission.status = 'Pending'  # Go back to pending
            submission.return_date = timezone.now()
            submission.return_reason = return_reason
            submission.save()
            updated_count += 1

        if updated_count == 0:
            return Response(
                {"error": "No documents found to return"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get updated counts - only Pending and Submitted
        all_submissions = AssignmentDocumentSubmission.objects.filter(
            assignment=assignment,
            status__in=['Pending', 'Submitted']
        )
        pending_count = all_submissions.filter(status='Pending').count()
        submitted_count = all_submissions.filter(status='Submitted').count()

        # Get separated data
        pending_submissions = all_submissions.filter(status='Pending')
        taken_submissions = all_submissions.filter(status='Submitted')
        
        pending_serializer = AssignmentDocumentSubmissionSerializer(pending_submissions, many=True)
        taken_serializer = AssignmentDocumentSubmissionSerializer(taken_submissions, many=True)

        return Response({
            "message": "Documents returned successfully",
            "assignment_name": assignment.assignment_name,
            "total_documents": all_submissions.count(),
            "pending_count": pending_count,
            "submitted_count": submitted_count,
            "returned_documents_count": updated_count,
            "pending_documents": pending_serializer.data,
            "taken_documents": taken_serializer.data
        }, status=status.HTTP_200_OK)


class AssignmentDocumentSubmissionHistoryAPIView(APIView):
    """Get submission history for an assignment"""
    def get(self, request, assignment_id):
        try:
            assignment = Assignment.objects.get(id=assignment_id, is_deleted=False)
        except Assignment.DoesNotExist:
            return Response(
                {"error": "Assignment not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        submissions = AssignmentDocumentSubmission.objects.filter(
            assignment=assignment
        ).select_related('document').order_by('-updated_at')

        serializer = AssignmentDocumentSubmissionSerializer(submissions, many=True)
        
        # Calculate counts
        pending_count = submissions.filter(status='Pending').count()
        submitted_count = submissions.filter(status='Submitted').count()
        returned_count = submissions.filter(status='Returned').count()

        return Response({
            "message": "Document submission history retrieved successfully",
            "assignment_name": assignment.assignment_name,
            "total_documents": submissions.count(),
            "pending_count": pending_count,
            "submitted_count": submitted_count,
            "returned_count": returned_count,
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class AssignmentDocumentWorkServiceHistoryAPIView(APIView):
    """
    Get document submission history for a specific assignment 
    AND a specific work service, including client details and counts.
    """
    def get(self, request, assignment_id, work_service_id):
        # 1. Validate Assignment (and fetch related client for the name)
        try:
            assignment = Assignment.objects.select_related('client').get(
                id=assignment_id, 
                is_deleted=False
            )
        except Assignment.DoesNotExist:
            return Response(
                {"error": "Assignment not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # 2. Validate Work Service
        try:
            work_service = WorkService.objects.get(id=work_service_id, is_deleted=False)
        except WorkService.DoesNotExist:
            return Response(
                {"error": "Work service not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # 3. Filter submissions by both IDs
        submissions = AssignmentDocumentSubmission.objects.filter(
            assignment_id=assignment_id,
            work_service_id=work_service_id
        ).select_related('document', 'employee').order_by('-updated_at')

        # 4. Serialize data
        serializer = AssignmentDocumentSubmissionSerializer(submissions, many=True)
        
        # 5. Calculate specific counts as requested
        pending_count = submissions.filter(status='Pending').count()
        submitted_count = submissions.filter(status='Submitted').count()
        returned_count = submissions.filter(status='Returned').count()

        return Response({
            "message": "Document submission history retrieved successfully",
            "client_name": assignment.client.client_name,  # Added Client Name
            "assignment_name": assignment.assignment_name,
            "work_service_name": work_service.service_name,
            "total_documents": submissions.count(),
            "pending_count": pending_count,
            "submitted_count": submitted_count,
            "returned_count": returned_count,
            "data": serializer.data
        }, status=status.HTTP_200_OK)
################################################################################################################

class EmployeeAssignmentDocumentsAPIView(APIView):
    def get(self, request, assignment_id, employee_id):

        docs = AssignmentDocumentSubmission.objects.filter(
            assignment_id=assignment_id,
            employee_id=employee_id
        ).select_related("document")

        pending = docs.filter(status="Pending")
        submitted = docs.filter(status="Submitted")
        returned = docs.filter(status="Returned")

        def serialize(qs):
            return [
                {
                    "id": d.id,
                    "document_id": d.document.id,
                    "document_name": d.document.document_name,
                    "status": d.status
                }
                for d in qs
            ]

        return Response({
            "employee_id": employee_id,
            "assignment_id": assignment_id,
            "pending_documents": serialize(pending),
            "submitted_documents": serialize(submitted),
            "returned_documents": serialize(returned),
        })




####################################################################################################delet employe api by prasad.r.shinde

class UserDeleteAPIView(APIView):
    """
    DELETE API to remove an employee
    URL: /api/users/delete/<int:user_id>/
    """
    def delete(self, request, user_id):
        try:
            # Fetch the user from the userauth model
            user = User.objects.get(id=user_id)
            
            # --- OPTION 1: Hard Delete (Permanent) ---
            user.delete()
            return Response({"message": "Employee deleted permanently"}, status=status.HTTP_200_OK)

            # --- OPTION 2: Soft Delete (Safer for CA systems) ---
            # user.is_active = False
            # user.save()
            # return Response({"message": "Employee account deactivated"}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response(
                {"error": "Employee not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
# class SubmitDocumentsAPIView(APIView):
#     def post(self, request, assignment_id):

#         employee_id = request.data.get("employee_id")
#         document_ids = request.data.get("document_ids", [])

#         # ✅ Validate assignment
#         assignment = Assignment.objects.filter(id=assignment_id).first()
#         if not assignment:
#             return Response({"error": "Assignment not found"}, status=404)

#         # ✅ Validate employee
#         employee = User.objects.filter(id=employee_id).first()
#         if not employee:
#             return Response({"error": "Employee not found"}, status=404)

#         submitted_count = 0

#         for doc_id in document_ids:

#             # ✅ Validate document
#             document = Document.objects.filter(id=doc_id).first()
#             if not document:
#                 continue

#             # ✅ CREATE OR UPDATE record
#             obj, created = AssignmentDocumentSubmission.objects.get_or_create(
#                 assignment=assignment,
#                 document=document,
#                 employee=employee,
#                 defaults={"status": "Pending"}
#             )

#             obj.status = "Submitted"
#             obj.submitted_date = timezone.now()
#             obj.save()

#             submitted_count += 1

#         return Response({
#             "message": "Documents submitted successfully",
#             "submitted_count": submitted_count
#         }, status=200)

###############################################################################################################
# class SubmitDocumentsAPIView(APIView):
#     def post(self, request, assignment_id):

#         employee_id = request.data.get("employee_id")
#         work_service_id = request.data.get("work_service_id")   # ✅ NEW
#         document_ids = request.data.get("document_ids", [])

#         if not work_service_id:
#             return Response({"error": "work_service_id is required"}, status=400)

#         # ✅ Validate assignment
#         assignment = Assignment.objects.filter(id=assignment_id).first()
#         if not assignment:
#             return Response({"error": "Assignment not found"}, status=404)

#         # ✅ Validate employee
#         employee = User.objects.filter(id=employee_id).first()
#         if not employee:
#             return Response({"error": "Employee not found"}, status=404)

#         # ✅ Validate work service
#         work_service = WorkService.objects.filter(id=work_service_id).first()
#         if not work_service:
#             return Response({"error": "Work service not found"}, status=404)

#         submitted_count = 0

#         for doc_id in document_ids:

#             document = Document.objects.filter(id=doc_id).first()
#             if not document:
#                 continue

#             obj, created = AssignmentDocumentSubmission.objects.get_or_create(
#                 assignment=assignment,
#                 work_service=work_service,     # ✅ ADDED
#                 document=document,
#                 employee=employee,
#                 defaults={"status": "Pending"}
#             )

#             obj.status = "Submitted"
#             obj.submitted_date = timezone.now()
#             obj.save()

#             submitted_count += 1

#         return Response({
#             "message": "Documents submitted successfully",
#             "submitted_count": submitted_count
#         }, status=200)


class SubmitDocumentsAPIView(APIView):
    def put(self, request, assignment_id):

        employee_id = request.data.get("employee_id")
        work_service_id = request.data.get("work_service_id")
        document_ids = request.data.get("document_ids", [])

        if not all([employee_id, work_service_id, document_ids]):
            return Response(
                {"error": "employee_id, work_service_id and document_ids are required"},
                status=400
            )

        employee = User.objects.filter(id=employee_id).first()
        if not employee:
            return Response({"error": "Employee not found"}, status=404)

        updated_count = 0
        not_found = []

        for doc_id in document_ids:
            qs = AssignmentDocumentSubmission.objects.filter(
                assignment_id=assignment_id,
                work_service_id=work_service_id,
                document_id=doc_id
            )

            if not qs.exists():
                not_found.append(doc_id)
                continue

            qs.update(
                employee_id=employee_id,
                status="Submitted",
                submitted_date=timezone.now()
            )

            updated_count += 1

        return Response(
            {
                "message": "Documents submitted successfully",
                "updated_count": updated_count,
                "not_found_documents": not_found
            },
            status=200
        )


# class ReturnDocumentsAPIView(APIView):
#     def post(self, request, assignment_id):

#         employee_id = request.data.get("employee_id")
#         document_ids = request.data.get("document_ids", [])
#         reason = request.data.get("reason", "")

#         submissions = AssignmentDocumentSubmission.objects.filter(
#             assignment_id=assignment_id,
#             employee_id=employee_id,
#             document_id__in=document_ids
#         )

#         count = 0
#         for s in submissions:
#             s.status = "Returned"
#             s.return_date = timezone.now()
#             s.return_reason = reason
#             s.save()
#             count += 1

#         return Response({
#             "message": "Documents returned successfully",
#             "returned_count": count
#         })

from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class ReturnDocumentsAPIView(APIView):
    def put(self, request, assignment_id):

        employee_id = request.data.get("employee_id")
        work_service_id = request.data.get("work_service_id")
        document_ids = request.data.get("document_ids", [])
        reason = request.data.get("reason", "")

        submissions = AssignmentDocumentSubmission.objects.filter(
            assignment_id=assignment_id,
            work_service_id=work_service_id,
            employee_id=employee_id,
            document_id__in=document_ids
        )

        if not submissions.exists():
            return Response(
                {"message": "No matching documents found to update"},
                status=status.HTTP_404_NOT_FOUND
            )

        count = submissions.update(
            status="Returned",
            return_date=timezone.now(),
            return_reason=reason
        )

        return Response({
            "message": "Documents returned successfully",
            "returned_count": count
        }, status=status.HTTP_200_OK)


# class AssignmentDocumentsAdminAPIView(APIView):
#     def get(self, request, assignment_id):

#         submissions = AssignmentDocumentSubmission.objects.filter(
#             assignment_id=assignment_id
#         ).select_related("document", "employee")

#         data = {}

#         for s in submissions:
#             emp = s.employee.full_name
#             if emp not in data:
#                 data[emp] = []

#             data[emp].append({
#                 "document_name": s.document.document_name,
#                 "status": s.status
#             })

#         return Response({
#             "assignment_id": assignment_id,
#             "employees": data
#         })


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status



class AssignmentDocumentsAdminAPIView(APIView):
    def get(self, request, assignment_id):

        work_service_id = request.query_params.get("work_service_id")

        # ✅ Base filter
        filters = {
            "assignment_id": assignment_id
        }

        # ✅ Add work_service filter if provided
        if work_service_id:
            filters["work_service_id"] = work_service_id

        submissions = AssignmentDocumentSubmission.objects.filter(
            **filters
        ).select_related("document", "employee", "work_service")

        data = {}

        for s in submissions:
            emp = s.employee.full_name

            if emp not in data:
                data[emp] = []

            data[emp].append({
                "document_id": s.document.id,
                "document_name": s.document.document_name,
                "status": s.status,
                "work_service_id": s.work_service.id,
                "work_service_name": s.work_service.service_name,
            })

        return Response({
            "assignment_id": assignment_id,
            "work_service_id": int(work_service_id) if work_service_id else None,
            "employees": data
        }, status=status.HTTP_200_OK)

##############################################################################################
# DASHBOARD APIs
##############################################################################################

from datetime import datetime, timedelta
from django.db.models import Count, Q
from .serializers import (
    ClientCountSerializer, AssignmentStatusCountSerializer,
    DocumentSubmissionStatusCountSerializer, WorkStatusCountSerializer,
    EmployeeWorkCountSerializer
)



class ClientCountDashboardAPIView(APIView):
    """Get client count statistics"""
    def get(self, request):
        total_clients = Client.objects.filter(is_active=True).count()
        
        # Current month clients
        now = datetime.now()
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        current_month_clients = Client.objects.filter(
            is_active=True,
            created_at__gte=current_month_start
        ).count()
        
        # Previous month clients
        previous_month_end = current_month_start - timedelta(days=1)
        previous_month_start = previous_month_end.replace(day=1)
        previous_month_clients = Client.objects.filter(
            is_active=True,
            created_at__gte=previous_month_start,
            created_at__lte=previous_month_end
        ).count()
        
        data = {
            'total_clients': total_clients,
            'current_month_clients': current_month_clients,
            'previous_month_clients': previous_month_clients
        }
        
        serializer = ClientCountSerializer(data)
        return Response({
            "message": "Client count retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class AssignmentStatusCountDashboardAPIView(APIView):
    """Get assignment count by status"""
    def get(self, request):
        assignments = Assignment.objects.filter(is_deleted=False)
        
        total = assignments.count()
        pending = assignments.filter(status='Pending').count()
        in_progress = assignments.filter(status='In Progress').count()
        completed = assignments.filter(status='Completed').count()
        cancelled = assignments.filter(status='Cancelled').count()
        
        data = {
            'total_assignments': total,
            'pending_count': pending,
            'in_progress_count': in_progress,
            'completed_count': completed,
            'cancelled_count': cancelled
        }
        
        serializer = AssignmentStatusCountSerializer(data)
        return Response({
            "message": "Assignment status count retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class DocumentSubmissionStatusCountDashboardAPIView(APIView):
    """Get document submission count by status"""
    def get(self, request):
        submissions = AssignmentDocumentSubmission.objects.all()
        
        total = submissions.count()
        pending = submissions.filter(status='Pending').count()
        submitted = submissions.filter(status='Submitted').count()
        
        data = {
            'total_documents': total,
            'pending_count': pending,
            'submitted_count': submitted
        }
        
        serializer = DocumentSubmissionStatusCountSerializer(data)
        return Response({
            "message": "Document submission status count retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class WorkStatusCountDashboardAPIView(APIView):
    """Get work count by status"""
    def get(self, request):
        works = Work.objects.filter(is_deleted=False)
        
        total = works.count()
        pending = works.filter(status='Pending').count()
        in_progress = works.filter(status='In Progress').count()
        completed = works.filter(status='Completed').count()
        cancelled = works.filter(status='Cancelled').count()
        
        data = {
            'total_works': total,
            'pending_count': pending,
            'in_progress_count': in_progress,
            'completed_count': completed,
            'cancelled_count': cancelled
        }
        
        serializer = WorkStatusCountSerializer(data)
        return Response({
            "message": "Work status count retrieved successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


class EmployeeWorkCountDashboardAPIView(APIView):
    """Get work count assigned to each employee"""
    def get(self, request):
        # Get all employees with their work counts
        employee_work_counts = User.objects.annotate(
            work_count=Count('assigned_works')
        ).filter(
            assigned_works__isnull=False
        ).values('id', 'full_name', 'work_count').distinct()
        
        # Convert to list of dicts for serializer
        data_list = [
            {
                'employee_id': item['id'],
                'employee_name': item['full_name'],
                'work_count': item['work_count']
            }
            for item in employee_work_counts
        ]
        
        serializer = EmployeeWorkCountSerializer(data_list, many=True)
        
        return Response({
            "message": "Employee work count retrieved successfully",
            "total_employees": len(data_list),
            "data": serializer.data
        }, status=status.HTTP_200_OK)


# class AssignmentChatSendAPIView(APIView):
#     def post(self, request):

#         assignment_id = request.data.get("assignment_id")
#         sender_id = request.data.get("sender_id")
#         message = request.data.get("message", "")
#         parent_id = request.data.get("parent_id")

#         if not message and not request.FILES:
#             return Response(
#                 {"error": "Message or file required"},
#                 status=400
#             )

#         # 🔐 Check assignment exists
#         assignment = Assignment.objects.filter(
#             id=assignment_id,
#             is_deleted=False
#         ).first()

#         if not assignment:
#             return Response({"error": "Assignment not found"}, status=404)

#         chat = AssignmentChatMessage.objects.create(
#             assignment_id=assignment_id,
#             sender_id=sender_id,
#             message=message,
#             parent_id=parent_id
#         )

#         for file in request.FILES.getlist("files"):
#             ChatAttachment.objects.create(
#                 message=chat,
#                 file=file,
#                 file_name=file.name
#             )

#         return Response(
#             {"message": "Message sent successfully"},
#             status=201
#         )

##########################################################################################################
class AssignmentChatSendAPIView(APIView):
    def post(self, request):

        assignment_id = request.data.get("assignment_id")
        work_service_id = request.data.get("work_service_id")
        sender_id = request.data.get("sender_id")
        message = request.data.get("message", "")
        parent_id = request.data.get("parent_id")

        if not message and not request.FILES:
            return Response({"error": "Message or file required"}, status=400)

        assignment = Assignment.objects.filter(
            id=assignment_id,
            is_deleted=False
        ).first()

        if not assignment:
            return Response({"error": "Assignment not found"}, status=404)

        chat = AssignmentChatMessage.objects.create(
            assignment_id=assignment_id,
            work_service_id=work_service_id,  # ✅ FIXED
            sender_id=sender_id,
            message=message,
            parent_id=parent_id
        )

        for file in request.FILES.getlist("files"):
            ChatAttachment.objects.create(
                message=chat,
                file=file,
                file_name=file.name
            )

        return Response({"message": "Message sent successfully"}, status=201)


#########################################################################################################

# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status

# from .models import AssignmentChatMessage
# from .models import Assignment
# from userauth.models import User

# class AssignmentChatListAPIView(APIView):
#     def get(self, request, assignment_id):

#         # Check assignment exists
#         assignment = Assignment.objects.filter(
#             id=assignment_id,
#             is_deleted=False
#         ).first()

#         if not assignment:
#             return Response(
#                 {"error": "Assignment not found"},
#                 status=status.HTTP_404_NOT_FOUND
#             )

#         chats = AssignmentChatMessage.objects.select_related(
#             "sender"
#         ).prefetch_related(
#             "seen_by",
#             "attachments",
#             "replies"
#         ).filter(
#             assignment_id=assignment_id
#         ).order_by("created_at")

#         response = []

#         for chat in chats:
#             response.append({
#                 "id": chat.id,
#                 "message": chat.message,
#                 "sender_id": chat.sender.id,
#                 "sender_name": chat.sender.full_name,
#                 "sender_role": chat.sender.role.lower(),   # admin / staff
#                 "parent_id": chat.parent_id,
#                 "seen_by": list(chat.seen_by.values_list("id", flat=True)),
#                 "attachments": [
#                     {
#                         "file_name": f.file_name,
#                         "file_url": f.file.url
#                     }
#                     for f in chat.attachments.all()
#                 ],
#                 "created_at": chat.created_at.strftime("%d/%m/%Y, %I:%M %p")
#             })

#         return Response(
#             {
#                 "assignment_id": assignment_id,
#                 "assignment_name": assignment.assignment_name,
#                 "messages": response
#             },
#             status=status.HTTP_200_OK
#         )

from zoneinfo import ZoneInfo
from django.utils import timezone

IST = ZoneInfo("Asia/Kolkata")

class AssignmentChatListAPIView(APIView):
    def get(self, request, assignment_id, work_service_id):

        # Check assignment exists
        assignment = Assignment.objects.filter(
            id=assignment_id,
            is_deleted=False
        ).first()

        if not assignment:
            return Response(
                {"error": "Assignment not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        chats = AssignmentChatMessage.objects.select_related(
            "sender", "work_service"
        ).prefetch_related(
            "seen_by",
            "attachments",
            "replies"
        ).filter(
            assignment_id=assignment_id,
            work_service_id=work_service_id   # ✅ FILTER BY BOTH
        ).order_by("created_at")

        response = []

        for chat in chats:
            ist_time = timezone.localtime(chat.created_at, IST)
            response.append({
                "id": chat.id,
                "message": chat.message,
                "sender_id": chat.sender.id,
                "sender_name": chat.sender.full_name,
                "sender_role": chat.sender.role.lower(),
                "parent_id": chat.parent_id,
                "work_service_id": chat.work_service_id,  # ✅
                "seen_by": list(chat.seen_by.values_list("id", flat=True)),
                "attachments": [
                    {
                        "file_name": f.file_name,
                        "file_url": f.file.url
                    }
                    for f in chat.attachments.all()
                ],
                "created_at": ist_time.strftime("%d/%m/%Y, %I:%M %p")  # ✅ IST time
            })

        return Response(
            {
                "assignment_id": assignment_id,
                "work_service_id": work_service_id,
                "assignment_name": assignment.assignment_name,
                "messages": response
            },
            status=status.HTTP_200_OK
        )

class AssignmentChatSeenAPIView(APIView):
    def post(self, request, message_id):

        user_id = request.data.get("user_id")

        if not user_id:
            return Response(
                {"error": "user_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate user
        user = User.objects.filter(id=user_id, is_active=True).first()
        if not user:
            return Response(
                {"error": "Invalid user"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate message
        message = AssignmentChatMessage.objects.filter(id=message_id).first()
        if not message:
            return Response(
                {"error": "Message not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Add seen status
        message.seen_by.add(user)

        return Response(
            {"message": "Message marked as seen"},
            status=status.HTTP_200_OK
        )


#############################################################################################
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from userauth.models import User
from .models import Work


class EmployeeDiaryAPIView(APIView):
    def get(self, request, employee_id):

        # Validate employee
        employee = User.objects.filter(id=employee_id, is_active=True).first()
        if not employee:
            return Response(
                {"error": "Employee not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        works = Work.objects.select_related(
            "assignment",
            "assignment__client",
            "work_service"
        ).filter(
            assigned_employees__id=employee_id,
            is_deleted=False
        )

        work_list = []

        for work in works:
            assignment = work.assignment
            client = assignment.client

            work_list.append({
                "work_id": work.id,
                "work_service_id": work.work_service_id,   # ✅ ADDED
                "work_service_name": work.work_service.service_name,  # ✅ OPTIONAL
                "work_status": work.status,
                "price": float(work.price),
                "advance_payment": float(work.advance_payment),
                "work_mode": work.work_mode,
                "created_at": work.created_at.strftime("%Y-%m-%d"),

                "assignment": {
                    "assignment_id": assignment.id,
                    "assignment_name": assignment.assignment_name,
                    "assignment_date": assignment.assignment_date.strftime("%Y-%m-%d"),
                    "assignment_status": assignment.status,
                },

                "client": {
                    "client_id": client.id,
                    "client_name": client.client_name,
                    "phone": client.phone,
                    "email": client.email,
                    "gst_number": client.gst_number,
                }
            })

        return Response({
            "employee_id": employee.id,
            "employee_name": employee.full_name,
            "total_works": works.count(),
            "works": work_list
        }, status=status.HTTP_200_OK)

##################################################################################################

# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from django.utils.dateparse import parse_date

# from userauth.models import User
# from .models import Work


# class EmployeeDiaryAPIView(APIView):
#     def get(self, request, employee_id):

#         # Validate employee
#         employee = User.objects.filter(id=employee_id, is_active=True).first()
#         if not employee:
#             return Response(
#                 {"error": "Employee not found"},
#                 status=status.HTTP_404_NOT_FOUND
#             )

#         # ✅ Get date from query params
#         date_str = request.query_params.get("date")  # format: YYYY-MM-DD

#         works = Work.objects.select_related(
#             "assignment",
#             "assignment__client",
#             "work_service"
#         ).filter(
#             assigned_employees__id=employee_id,
#             is_deleted=False
#         )

#         # ✅ Apply date filter if provided
#         if date_str:
#             date_obj = parse_date(date_str)
#             if not date_obj:
#                 return Response(
#                     {"error": "Invalid date format. Use YYYY-MM-DD"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
#             works = works.filter(created_at__date=date_obj)

#         work_list = []

#         for work in works:
#             assignment = work.assignment
#             client = assignment.client

#             work_list.append({
#                 "work_id": work.id,
#                 "work_service_id": work.work_service_id,
#                 "work_service_name": work.work_service.service_name,
#                 "work_status": work.status,
#                 "price": float(work.price),
#                 "advance_payment": float(work.advance_payment),
#                 "work_mode": work.work_mode,
#                 "created_at": work.created_at.strftime("%Y-%m-%d"),

#                 "assignment": {
#                     "assignment_id": assignment.id,
#                     "assignment_name": assignment.assignment_name,
#                     "assignment_date": assignment.assignment_date.strftime("%Y-%m-%d"),
#                     "assignment_status": assignment.status,
#                 },

#                 "client": {
#                     "client_id": client.id,
#                     "client_name": client.client_name,
#                     "phone": client.phone,
#                     "email": client.email,
#                     "gst_number": client.gst_number,
#                 }
#             })

#         return Response({
#             "employee_id": employee.id,
#             "employee_name": employee.full_name,
#             "filter_date": date_str if date_str else "all",
#             "total_works": works.count(),
#             "works": work_list
#         }, status=status.HTTP_200_OK)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.dateparse import parse_date

from userauth.models import User
from .models import Work


class EmployeeDiaryAPIView(APIView):
    def get(self, request, employee_id):

        # Validate employee
        employee = User.objects.filter(id=employee_id, is_active=True).first()
        if not employee:
            return Response(
                {"error": "Employee not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # ✅ Get date from query params
        date_str = request.query_params.get("date")  # format: YYYY-MM-DD

        works = Work.objects.select_related(
            "assignment",
            "assignment__client",
            "work_service"
        ).filter(
            assigned_employees__id=employee_id,
            is_deleted=False
        )

        # ✅ Apply date filter if provided
        if date_str:
            date_obj = parse_date(date_str)
            if not date_obj:
                return Response(
                    {"error": "Invalid date format. Use YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            works = works.filter(created_at__date=date_obj)

        work_list = []

        for work in works:
            assignment = work.assignment
            client = assignment.client

            work_list.append({
                "work_id": work.id,
                "work_service_id": work.work_service_id,
                "work_service_name": work.work_service.service_name,
                "work_status": work.status,
                "price": float(work.price),
                "advance_payment": float(work.advance_payment),
                "work_mode": work.work_mode,
                "created_at": work.created_at.strftime("%Y-%m-%d"),

                "assignment": {
                    "assignment_id": assignment.id,
                    "assignment_name": assignment.assignment_name,
                    "assignment_date": assignment.assignment_date.strftime("%Y-%m-%d"),
                    "assignment_status": assignment.status,
                },

                "client": {
                    "client_id": client.id,
                    "client_name": client.client_name,
                    "phone": client.phone,
                    "email": client.email,
                    "gst_number": client.gst_number,
                }
            })

        return Response({
            "employee_id": employee.id,
            "employee_name": employee.full_name,
            "filter_date": date_str if date_str else "all",
            "total_works": works.count(),
            "works": work_list
        }, status=status.HTTP_200_OK)

##################################################################################################

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# from assignments.models import Assignment
# from work_services.models import WorkService
# from works.models import Work
# from documents.models import Document, AssignmentDocumentSubmission


class DocumentSummaryAPIView(APIView):
    def get(self, request):

        assignment_id = request.query_params.get("assignment_id")
        employee_id = request.query_params.get("employee_id")
        work_service_id = request.query_params.get("work_service_id")

        # ✅ Validate query params
        if not assignment_id or not employee_id or not work_service_id:
            return Response(
                {"error": "assignment_id, employee_id, and work_service_id are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ Get Assignment
        assignment = Assignment.objects.filter(id=assignment_id).first()
        if not assignment:
            return Response({"error": "Assignment not found"}, status=404)

        # ✅ Get Work Service
        work_service = WorkService.objects.filter(id=work_service_id, is_deleted=False).first()
        if not work_service:
            return Response({"error": "Work service not found"}, status=404)

        # ✅ Get Work Mode from Work table
        work = Work.objects.filter(
            assignment_id=assignment_id,
            work_service_id=work_service_id,
            is_deleted=False
        ).first()

        work_mode = work.work_mode if work else None

        # ✅ Total documents
        total_documents = Document.objects.filter(
            work_service_id=work_service_id
        ).count()

        # ✅ Submitted documents (distinct)
        submitted_documents = AssignmentDocumentSubmission.objects.filter(
            assignment_id=assignment_id,
            employee_id=employee_id,
            status="Submitted",
            document__work_service_id=work_service_id
        ).values("document_id").distinct().count()

        return Response({
            "assignment_id": int(assignment_id),
            "employee_id": int(employee_id),
            "work_service_id": int(work_service_id),

            "assignment_name": assignment.assignment_name,
            "work_service_name": work_service.service_name,
            "work_mode": work_mode,   # ✅ ADDED

            "documents": {
                "total_documents": total_documents,
                "submitted_documents": submitted_documents,
                "pending_documents": total_documents - submitted_documents
            }
        }, status=status.HTTP_200_OK)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status



class UpdateAssignmentWorkStatusAPIView(APIView):
    def post(self, request):

        assignment_id = request.data.get("assignment_id")
        employee_id = request.data.get("employee_id")
        work_service_id = request.data.get("work_service_id")
        new_status = request.data.get("status")  # Pending / In Progress / Completed

        # ✅ Validate status
        if new_status not in ["Pending", "In Progress", "Completed"]:
            return Response(
                {"error": "Invalid status value"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ Validate assignment
        assignment = Assignment.objects.filter(id=assignment_id, is_deleted=False).first()
        if not assignment:
            return Response({"error": "Assignment not found"}, status=404)

        # ✅ Find works for this employee + assignment + service
        works = Work.objects.filter(
            assignment_id=assignment_id,
            work_service_id=work_service_id,
            assigned_employees__id=employee_id,
            is_deleted=False
        )

        if not works.exists():
            return Response(
                {"error": "No works found for this employee"},
                status=404
            )

        # ✅ Update work status
        updated_works = works.update(status=new_status)

        # ✅ Recalculate assignment status (SMART LOGIC)
        all_works = Work.objects.filter(
            assignment_id=assignment_id,
            is_deleted=False
        )

        if all_works.filter(status="In Progress").exists():
            assignment.status = "In Progress"
        elif all_works.filter(status="Pending").exists():
            assignment.status = "Pending"
        else:
            assignment.status = "Completed"

        assignment.save()

        return Response({
            "message": "Status updated successfully",
            "assignment_id": assignment_id,
            "work_service_id": work_service_id,
            "employee_id": employee_id,
            "updated_works": updated_works,
            "assignment_status": assignment.status,
            "work_status": new_status
        }, status=200)


from django.utils.dateparse import parse_date



# daily chat api by prasad

class EmployeeDailyChatSendAPIView(APIView):
    """
    1. POST API to send a daily chat/remark
    Input: employee_id, message, date (YYYY-MM-DD)
    """
    def post(self, request):
        employee_id = request.data.get("employee_id")
        message = request.data.get("message")
        date_str = request.data.get("date")

        if not employee_id or not message:
            return Response({"error": "employee_id and message are required"}, status=400)

        # Validate User
        user = User.objects.filter(id=employee_id).first()
        if not user:
            return Response({"error": "Employee not found"}, status=404)

        # Use provided date or default to today
        target_date = parse_date(date_str) if date_str else timezone.now().date()

        remark = EmployeeDailyRemark.objects.create(
            employee=user,
            message=message,
            date=target_date
        )

        return Response({
            "message": "Remark sent successfully",
            "data": EmployeeDailyRemarkSerializer(remark).data
        }, status=201)


class EmployeeDailyChatHistoryAPIView(APIView):
    """
    2. GET API to view chat history by date and employee_id
    URL: /api/employee-diary/chat/history/<employee_id>/?date=YYYY-MM-DD
    """
    def get(self, request, employee_id):
        date_str = request.query_params.get("date")
        
        if not date_str:
            return Response({"error": "date parameter is required (YYYY-MM-DD)"}, status=400)

        target_date = parse_date(date_str)
        if not target_date:
            return Response({"error": "Invalid date format"}, status=400)

        # Fetch messages for that employee on that specific work date
        history = EmployeeDailyRemark.objects.filter(
            employee_id=employee_id,
            date=target_date
        ).select_related('employee').order_by('created_at')

        serializer = EmployeeDailyRemarkSerializer(history, many=True)
        
        return Response({
            "employee_id": employee_id,
            "date": date_str,
            "count": history.count(),
            "history": serializer.data
        }, status=200)