from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.http import JsonResponse
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import json
import uuid
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import VerificationToken  # Import new model

User = get_user_model()

# Email verification
@csrf_exempt
def register_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        existing_user = User.objects.filter(email=email).first()
        if existing_user:
            if not existing_user.email_verified:
                return JsonResponse({"error": "Email already registered but not verified. Check your email."}, status=400)
            return JsonResponse({"error": "Email already registered."}, status=400)

        # Create new user
        user = User.objects.create_user(username=username, email=email, password=password)

        # Create verification token
        token = VerificationToken.objects.create(user=user, token_type="email_verification")

        # Send verification email
        verification_link = f"{settings.FRONTEND_URL}/verify-email/?token={token.token}"
        send_mail(
            "Verify Your Email",
            f"Click the link to verify your account: {verification_link}",
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        return JsonResponse({"message": "User registered successfully. Please check your email for verification."})

    return JsonResponse({"error": "POST request required"}, status=400)


@csrf_exempt
def verify_email(request, token):
    verification_token = get_object_or_404(VerificationToken, token=token, token_type="email_verification")

    if verification_token.is_expired():
        return JsonResponse({"error": "Token expired. Request a new verification link."}, status=400)

    user = verification_token.user
    if user.email_verified:
        return JsonResponse({"message": "Email already verified"}, status=400)

    user.email_verified = True
    user.save()

    # Delete the token after verification
    verification_token.delete()

    return JsonResponse({"message": "Email verified successfully."})

# Password reset
@csrf_exempt
def request_password_reset(request):
    if request.method == "POST":
        data = json.loads(request.body)
        email = data.get("email")

        user = User.objects.filter(email=email).first()
        if not user:
            return JsonResponse({"error": "User not found"}, status=404)

        # Check if user can request a new token (15-minute cooldown)
        if not VerificationToken.can_request_new_token(user, "password_reset", wait_time_minutes=15):
            return JsonResponse({"error": "Please wait before requesting another password reset."}, status=429)

        # Delete old password reset tokens for security
        VerificationToken.objects.filter(user=user, token_type="password_reset").delete()

        # Create new password reset token
        token = VerificationToken.objects.create(user=user, token_type="password_reset")

        reset_link = f"{settings.FRONTEND_URL}/reset-password/?token={token.token}"
        send_mail(
            "Password Reset Request",
            f"Click the link to reset your password: {reset_link}",
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        return JsonResponse({"message": "Password reset link sent to your email."})

    return JsonResponse({"error": "POST request required"}, status=400)



@csrf_exempt
def reset_password(request):
    if request.method == "POST":
        data = json.loads(request.body)
        token = data.get("token")
        new_password = data.get("new_password")

        verification_token = VerificationToken.objects.filter(token=token, token_type="password_reset").first()
        if not verification_token:
            return JsonResponse({"error": "Invalid token"}, status=400)

        if verification_token.is_expired():
            return JsonResponse({"error": "Token expired. Request a new password reset link."}, status=400)

        user = verification_token.user
        user.set_password(new_password)
        user.save()

        # Delete the token after use
        verification_token.delete()

        return JsonResponse({"message": "Password reset successful."})

    return JsonResponse({"error": "POST request required"}, status=400)

@csrf_exempt
def resend_verification_email(request):
    if request.method == "POST":
        data = json.loads(request.body)
        email = data.get("email")

        user = User.objects.filter(email=email).first()
        if not user:
            return JsonResponse({"error": "User not found"}, status=404)

        if user.email_verified:
            return JsonResponse({"message": "Email already verified."}, status=400)

        # Check if the user can request a new token (5-minute cooldown)
        if not VerificationToken.can_request_new_token(user, "email_verification", wait_time_minutes=5):
            return JsonResponse({"error": "Please wait before requesting another verification email."}, status=429)

        # Delete old verification tokens
        VerificationToken.objects.filter(user=user, token_type="email_verification").delete()

        # Generate a new verification token
        token = VerificationToken.objects.create(user=user, token_type="email_verification")

        verification_link = f"{settings.FRONTEND_URL}/verify-email/?token={token.token}"
        send_mail(
            "Resend: Verify Your Email",
            f"Click the link to verify your account: {verification_link}",
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        return JsonResponse({"message": "Verification email resent. Check your inbox."})

    return JsonResponse({"error": "POST request required"}, status=400)
# Custom Login View (Optional: Add more user details in response)
class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            user = get_user_model().objects.get(username=request.data['username'])
            response.data.update({
                "id": user.id,
                "username": user.username,
                "role": user.role,
                "email": user.email,
            })
        
        return response