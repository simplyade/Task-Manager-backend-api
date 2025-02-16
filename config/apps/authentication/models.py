from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from django.utils.timezone import now, timedelta

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('user', 'User'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    email_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class VerificationToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tokens")
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    token_type = models.CharField(
        max_length=20,
        choices=[("email_verification", "Email Verification"), ("password_reset", "Password Reset")],
    )

    def is_expired(self):
        expiration_time = timedelta(hours=24) if self.token_type == "email_verification" else timedelta(hours=1)
        return now() > self.created_at + expiration_time

    @staticmethod
    def can_request_new_token(user, token_type, wait_time_minutes):
        """Prevent spam by limiting how often a user can request a new token."""
        last_request = VerificationToken.objects.filter(user=user, token_type=token_type).order_by('-created_at').first()
        if last_request and (now() - last_request.created_at).total_seconds() < wait_time_minutes * 60:
            return False  # User must wait longer before requesting a new token
        return True
