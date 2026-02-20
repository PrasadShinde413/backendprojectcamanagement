from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import check_password
from .models import User
from .serializers import UserRegistrationSerializer, LoginSerializer

class RegisterAPIView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User registered successfully"},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(username=username, is_active=True)
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid username or inactive account"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_password_reset:
            return Response({
                "error": "First-time reset required",
                "require_reset": True,
                "email": user.email
            }, status=status.HTTP_403_FORBIDDEN)
        
        if not check_password(password, user.password):
            return Response({"error": "Invalid password"}, status=401)

        return Response({
            "message": "Login successful",
            "user": {
                "id": user.id,
                "full_name": user.full_name,
                "role": user.role,
                "email": user.email,
                'address': user.address,
                'phone_no': user.phone_no,
            }
        }, status=status.HTTP_200_OK)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import UserSerializer, UserUpdateSerializer


class UserListAPIView(APIView):
    def get(self, request):
        users = User.objects.all().order_by('-created_at')
        serializer = UserSerializer(users, many=True)
        return Response({
            "count": users.count(),
            "data": serializer.data
        }, status=status.HTTP_200_OK)

class UserDetailAPIView(APIView):
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserUpdateAPIView(APIView):
    def put(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = UserUpdateSerializer(
            user, data=request.data, partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User updated successfully"},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


import random
from .models import User, PasswordResetOTP
from django.core.mail import send_mail
from django.conf import settings
from .serializers import RequestOTPSerializer, VerifyOTPSerializer, ResetPasswordSerializer

# Step 1: Send OTP
class RequestOTPAPIView(APIView):
    def post(self, request):
        email = request.data.get('email')
        
        # Check if user exists
        if not User.objects.filter(email=email).exists():
            return Response({"error": "Email not found in our records"}, status=404)

        # Generate 6-digit OTP
        otp = str(random.randint(100000, 999999))
        
        # Save OTP to DB (Delete old one first)
        PasswordResetOTP.objects.filter(email=email).delete()
        PasswordResetOTP.objects.create(email=email, otp=otp)
        
        # SEND THE EMAIL
        subject = 'Verification Code - CA Management System'
        message = f'Your OTP for password reset is: {otp}. It is valid for 10 minutes.'
        
        try:
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER if hasattr(settings, 'EMAIL_HOST_USER') else 'prasadshindeking@gmail.com',
                [email],
                fail_silently=False,
            )
            return Response({"message": "OTP sent successfully"}, status=200)
        except Exception as e:
            return Response({"error": f"Email sending failed: {str(e)}"}, status=500)

# Step 2: Verify OTP
class VerifyOTPAPIView(APIView):
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            
            otp_record = PasswordResetOTP.objects.filter(email=email, otp=otp).last()
            
            if otp_record and otp_record.is_valid():
                return Response({"message": "OTP verified successfully."}, status=200)
            return Response({"error": "Invalid or expired OTP."}, status=400)
        return Response(serializer.errors, status=400)

# Step 3: Set New Password
class ResetPasswordAPIView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            new_password = serializer.validated_data['new_password']
            
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.is_password_reset = True # 👈 Now the user can log in
            user.save()
            
            # Clean up the OTP
            PasswordResetOTP.objects.filter(email=email).delete()
            
            return Response({"message": "Password reset successful. You can now login."}, status=200)
        return Response(serializer.errors, status=400)