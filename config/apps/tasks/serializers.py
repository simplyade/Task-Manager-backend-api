from rest_framework import serializers
from .models import Project, Task, Comment, Collaboration, Notification,Task
from apps.authentication.models import User



class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"

class CollaborationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collaboration
        fields = "__all__"

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"



class TaskAssignmentSerializer(serializers.Serializer):
    task_id = serializers.IntegerField()
    assignee_id = serializers.IntegerField()
