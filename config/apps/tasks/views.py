from rest_framework import viewsets, permissions, filters,status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Project, Task, Comment, Collaboration, Notification
from .serializers import (
    ProjectSerializer,
    TaskSerializer,
    CommentSerializer,
    CollaborationSerializer,
    NotificationSerializer,
    TaskAssignmentSerializer
)
from rest_framework_simplejwt.views import TokenObtainPairView
from .permissions import IsProjectOwner
from .models import Project
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from apps.authentication.models import User
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN


class TaskAssignmentViewSet(viewsets.ViewSet):
    """
    API endpoint to assign tasks dynamically.
    """
    permission_classes = [IsAuthenticated, IsProjectOwner]

    def create(self, request):
        serializer = TaskAssignmentSerializer(data=request.data)
        if serializer.is_valid():
            task = get_object_or_404(Task, id=serializer.validated_data['task_id'])
            assignee = get_object_or_404(User, id=serializer.validated_data['assignee_id'])

            # Ensure the user has permission to assign
            if task.project.owner != request.user:
                return Response({"error": "Only project owners can assign tasks."}, status=status.HTTP_403_FORBIDDEN)

            task.assignees.add(assignee)
            task.save()

            return Response({"message": "Task assigned successfully."}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    
# Custom Login View (Moved from authentication/views.py)
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT Authentication View - returns user details with token.
    """
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




# Custom Filter for Projects
class ProjectFilter(django_filters.FilterSet):
    created_at = django_filters.DateFilter(field_name="created_at", lookup_expr="date")  # Exact date filter
    created_before = django_filters.DateFilter(field_name="created_at", lookup_expr="lte")  # Before date
    created_after = django_filters.DateFilter(field_name="created_at", lookup_expr="gte")  # After date

    class Meta:
        model = Project
        fields = ["created_at", "owner"]

class ProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing projects.
    """
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated, IsProjectOwner]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    search_fields = ["name", "description"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]
    filterset_fields = ["created_at", "owner"]  #  Enable filtering by owner and date

    def get_queryset(self):
        """
        Return only projects owned by the authenticated user.
        """
        return Project.objects.filter(owner=self.request.user)



class TaskViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing tasks.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "priority", "project"]
    search_fields = ["title", "description"]
    ordering_fields = ["deadline", "created_at"]
    ordering = ["-created_at"]
    
    @action(detail=True, methods=["post"], url_path="assign")
    def assign_task(self, request, pk=None):
        """
        Assign a task to one or more users (Only Project Owners or Admins).
        """
        task = self.get_object()
        user_ids = request.data.get("user_ids", [])

        # Ensure the requester is a project owner or admin
        if task.project.owner != request.user and not request.user.is_superuser:
            return Response({"error": "Only project owners or admins can assign tasks."}, status=status.HTTP_403_FORBIDDEN)

        # Fetch users and ensure they exist
        users = User.objects.filter(id__in=user_ids)
        if not users.exists():
            return Response({"error": "No valid users found."}, status=status.HTTP_400_BAD_REQUEST)

        # Assign users to the task
        task.assignees.set(users)
        task.save()

        return Response({
            "message": "Users assigned successfully.",
            "assigned_users": [{"id": user.id, "username": user.username} for user in users]
        }, status=status.HTTP_200_OK)

    


class CommentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing comments on tasks.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["task"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]


class CollaborationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing project collaborations.
    """
    queryset = Collaboration.objects.all()
    serializer_class = CollaborationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["project", "role"]
    ordering_fields = ["project"]
    ordering = ["project"]


class NotificationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing notifications.
    """
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["user", "is_read"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]
