
from django.urls import path
from apps.authentication import views  # Ensure views are properly imported
from apps.authentication.views import verify_email,register_view
import uuid

urlpatterns = [
    path("register/", views.register_view, name="register"),  # Register route
    path("verify-email/<uuid:token>/", verify_email, name="verify_email"),  # Email verification route
]                                                                                                            

