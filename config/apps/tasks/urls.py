from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    CustomTokenObtainPairView,
    ProjectViewSet,
    TaskViewSet,
    CommentViewSet,
    CollaborationViewSet,
    NotificationViewSet,
    TaskAssignmentViewSet

)

# DRF Router (Auto-generates CRUD endpoints for task management)
router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'collaborations', CollaborationViewSet, basename='collaboration')
router.register(r'notifications', NotificationViewSet, basename='notification')

router.register(r'assign-task', TaskAssignmentViewSet, basename="assign-task")

# URL patterns
urlpatterns = [
    # Authentication Endpoints
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
   # Task Management Endpoints (Auto-Generated)
    path('', include(router.urls)),  # Includes ViewSet endpoints
]
