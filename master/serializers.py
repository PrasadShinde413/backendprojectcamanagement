from rest_framework import serializers
from .models import Client, EmployeeDailyRemark

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'

##################################################################################################

from rest_framework import serializers
from .models import WorkService, Document

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'document_name', 'is_checked', 'created_at']


class DocumentWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id','document_name']


class WorkServiceSerializer(serializers.ModelSerializer):
    documents = DocumentWriteSerializer(many=True, required=False)

    class Meta:
        model = WorkService
        fields = '__all__'

    def update(self, instance, validated_data):
        documents_data = validated_data.pop('documents', [])

        # 🔹 Update WorkService fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # 🔹 Handle Documents
        existing_docs = {doc.id: doc for doc in instance.documents.all()}
        sent_doc_ids = []

        for doc_data in documents_data:
            doc_id = doc_data.get('id')

            if doc_id and doc_id in existing_docs:
                # UPDATE
                doc = existing_docs[doc_id]
                for attr, value in doc_data.items():
                    setattr(doc, attr, value)
                doc.save()
                sent_doc_ids.append(doc_id)

            else:
                # CREATE
                Document.objects.create(
                    work_service=instance,
                    **doc_data
                )

        # 🔹 OPTIONAL: Delete missing documents
        for doc_id, doc in existing_docs.items():
            if doc_id not in sent_doc_ids:
                doc.delete()

        return instance



class WorkServiceCreateSerializer(serializers.ModelSerializer):
    documents = DocumentWriteSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = WorkService
        fields = ['service_name', 'description', 'is_recurring', 'documents']

    def create(self, validated_data):
        documents_data = validated_data.pop('documents', [])
        work_service = WorkService.objects.create(**validated_data)
        
        # Create documents for this work service
        for doc_data in documents_data:
            Document.objects.create(work_service=work_service, **doc_data)
        
        return work_service


from rest_framework import serializers
from .models import Assignment

class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = '__all__'


from rest_framework import serializers
from .models import Work

class WorkSerializer(serializers.ModelSerializer):
    assigned_employees = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )

    class Meta:
        model = Work
        fields = '__all__'

    def create(self, validated_data):
        employees = validated_data.pop('assigned_employees')
        work = Work.objects.create(**validated_data)
        work.assigned_employees.set(employees)
        return work

    def update(self, instance, validated_data):
        employees = validated_data.pop('assigned_employees', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if employees is not None:
            instance.assigned_employees.set(employees)

        return instance


from rest_framework import serializers
from .models import Work
from userauth.models import User

class BulkWorkCreateSerializer(serializers.ModelSerializer):
    assigned_employees = serializers.ListField(
        child=serializers.IntegerField()
    )

    class Meta:
        model = Work
        fields = [
            'assignment',
            'work_service',
            'price',
            'advance_payment',
            'work_mode',
            'assigned_employees'
        ]

    def validate_assigned_employees(self, employee_ids):
        valid_ids = set(
            User.objects.filter(
                id__in=employee_ids,
                is_active=True
            ).values_list('id', flat=True)
        )

        missing = set(employee_ids) - valid_ids
        if missing:
            raise serializers.ValidationError(
                f"Invalid employee IDs: {list(missing)}"
            )

        return employee_ids


###############################################################################################

# from rest_framework import serializers
# from .models import Work
# from userauth.models import User


# class BulkWorkSerializer(serializers.ModelSerializer):
#     assigned_employees = serializers.ListField(
#         child=serializers.IntegerField()
#     )

#     class Meta:
#         model = Work
#         fields = [
#             'assignment',
#             'work_service',
#             'price',
#             'advance_payment',
#             'work_mode',
#             'assigned_employees'
#         ]

#     def validate_assigned_employees(self, employee_ids):
#         valid_ids = set(
#             User.objects.filter(
#                 id__in=employee_ids,
#                 is_active=True
#             ).values_list('id', flat=True)
#         )

#         missing = set(employee_ids) - valid_ids
#         if missing:
#             raise serializers.ValidationError(
#                 f"Invalid employee IDs: {list(missing)}"
#             )

#         return employee_ids

#     def create(self, validated_data):
#         employees = validated_data.pop("assigned_employees")
#         work = Work.objects.create(**validated_data)
#         work.assigned_employees.set(employees)
#         return work


from rest_framework import serializers
from .models import Work
from userauth.models import User


class BulkWorkSerializer(serializers.ModelSerializer):
    assigned_employees = serializers.ListField(
        child=serializers.IntegerField()
    )
    document_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        write_only=True
    )
    # 🔄 NEW: Support recurring assignments
    is_recurring = serializers.BooleanField(required=False, write_only=True)

    class Meta:
        model = Work
        fields = [
            'assignment',
            'work_service',
            'price',
            'advance_payment',
            'work_mode',
            'assigned_employees',
            'document_ids',
            'is_recurring'  # 🔄 NEW
        ]

    def validate_assigned_employees(self, employee_ids):
        valid_ids = set(
            User.objects.filter(
                id__in=employee_ids,
                is_active=True
            ).values_list('id', flat=True)
        )

        missing = set(employee_ids) - valid_ids
        if missing:
            raise serializers.ValidationError(
                f"Invalid employee IDs: {list(missing)}"
            )
        return employee_ids

    def create(self, validated_data):
        employees = validated_data.pop("assigned_employees")
        document_ids = validated_data.pop("document_ids", [])
        is_recurring = validated_data.pop("is_recurring", False)  # 🔄 NEW

        work = Work.objects.create(**validated_data)
        work.assigned_employees.set(employees)

        # 👇 Store extras for view usage
        work._document_ids = document_ids
        work._is_recurring = is_recurring  # 🔄 NEW
        work._employees = employees  # 🔄 NEW - store for bulk API
        return work

################################################################################################
from rest_framework import serializers
from .models import Work


class BulkWorkReadSerializer(serializers.ModelSerializer):
    assigned_employees = serializers.SerializerMethodField()

    class Meta:
        model = Work
        fields = [
            "id",
            "assignment",
            "work_service",
            "price",
            "advance_payment",
            "work_mode",
            "status",
            "assigned_employees",
        ]

    def get_assigned_employees(self, obj):
        return list(
            obj.assigned_employees.values(
                "id",
                "full_name",
                "email",
                "phone_no"
            )
        )


# ============================= ASSIGNMENT DOCUMENT SUBMISSION SERIALIZERS =============================

from .models import AssignmentDocumentSubmission
from django.utils import timezone




class AssignmentDocumentSubmissionSerializer(serializers.ModelSerializer):
    document_name = serializers.CharField(source='document.document_name', read_only=True)
    
    class Meta:
        model = AssignmentDocumentSubmission
        fields = ['id','document_id' ,'document_name', 'work_service_id', 'status', 'submitted_date', 'return_date', 'return_reason']


class DocumentSubmitSerializer(serializers.ModelSerializer):
    document_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True)
    
    class Meta:
        model = AssignmentDocumentSubmission
        fields = ['document_ids']

    def create(self, validated_data):
        document_ids = validated_data.pop('document_ids')
        assignment_id = self.context.get('assignment_id')
        
        submissions = []
        for doc_id in document_ids:
            submission, created = AssignmentDocumentSubmission.objects.get_or_create(
                assignment_id=assignment_id,
                document_id=doc_id,
                defaults={'status': 'Submitted', 'submitted_date': timezone.now()}
            )
            if not created:
                submission.status = 'Submitted'
                submission.submitted_date = timezone.now()
                submission.return_date = None
                submission.return_reason = None
                submission.save()
            submissions.append(submission)
        
        return submissions


class DocumentReturnSerializer(serializers.Serializer):
    document_ids = serializers.ListField(child=serializers.IntegerField())
    return_reason = serializers.CharField(max_length=500, required=False, allow_blank=True)


# ============================= DASHBOARD SERIALIZERS =============================

from django.db.models import Count
from datetime import datetime

class ClientCountSerializer(serializers.Serializer):
    total_clients = serializers.IntegerField()
    current_month_clients = serializers.IntegerField()
    previous_month_clients = serializers.IntegerField()
    month = serializers.SerializerMethodField()
    
    def get_month(self, obj):
        return datetime.now().strftime("%B %Y")


class AssignmentStatusCountSerializer(serializers.Serializer):
    total_assignments = serializers.IntegerField()
    pending_count = serializers.IntegerField()
    in_progress_count = serializers.IntegerField()
    completed_count = serializers.IntegerField()
    cancelled_count = serializers.IntegerField()


class DocumentSubmissionStatusCountSerializer(serializers.Serializer):
    total_documents = serializers.IntegerField()
    pending_count = serializers.IntegerField()
    submitted_count = serializers.IntegerField()


class WorkStatusCountSerializer(serializers.Serializer):
    total_works = serializers.IntegerField()
    pending_count = serializers.IntegerField()
    in_progress_count = serializers.IntegerField()
    completed_count = serializers.IntegerField()
    cancelled_count = serializers.IntegerField()


class EmployeeWorkCountSerializer(serializers.Serializer):
    employee_id = serializers.IntegerField()
    employee_name = serializers.CharField()
    work_count = serializers.IntegerField()


# ============================= ASSIGNMENT DETAILS SERIALIZER =============================

class UserSimpleSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ['id', 'full_name']


class DocumentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'document_name', 'is_checked']


class WorkServiceDetailSerializer(serializers.ModelSerializer):
    documents = DocumentDetailSerializer(many=True, read_only=True)
    document_count = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkService
        fields = ['id', 'service_name', 'documents', 'document_count']
    
    def get_document_count(self, obj):
        return obj.documents.count()


class WorkDetailForAssignmentSerializer(serializers.ModelSerializer):
    work_service = WorkServiceDetailSerializer(read_only=True)
    assigned_employees = UserSimpleSerializer(many=True, read_only=True)
    
    class Meta:
        model = Work
        fields = ['id', 'work_service', 'assigned_employees', 'price', 'advance_payment', 'work_mode', 'status']


class AssignmentDetailSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.client_name', read_only=True)
    works = WorkDetailForAssignmentSerializer(many=True, read_only=True)
    assignment_status = serializers.CharField(source='status', read_only=True)
    total_documents = serializers.SerializerMethodField()
    
    class Meta:
        model = Assignment
        fields = ['id', 'assignment_name', 'client_name', 'assignment_status', 'number_of_assignment', 'works', 'total_documents']
    
    def get_total_documents(self, obj):
        total = 0
        for work in obj.works.all():
            total += work.work_service.documents.count()
        return total


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



# ============================= employee daily remark =============================

class EmployeeDailyRemarkSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='employee.full_name', read_only=True)
    is_employee = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeDailyRemark
        fields = ['id', 'employee', 'sender_name', 'message', 'date', 'is_employee', 'created_at']

    def get_is_employee(self, obj):
        # Useful for frontend styling (bubbles on right/left)
        return obj.employee.role.lower() != 'admin'