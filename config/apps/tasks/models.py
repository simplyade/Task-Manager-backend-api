from django.db import models
from apps.authentication.models import User



# 1️ Project Model (Grouping of tasks)
class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="projects")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# 2️ Task Model (Core task entity)
class Task(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("accepted", "Accepted"),
    ]
    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="medium")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    deadline = models.DateTimeField(null=True, blank=True)
    reminder_time = models.DateTimeField(null=True, blank=True)  #  Task reminders
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks", null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks_created")
    assignees = models.ManyToManyField(User, related_name="tasks_assigned", blank=True)  #  Multiple assignees
    tags = models.JSONField(default=list, blank=True)  #  List of task tags
    is_deleted = models.BooleanField(default=False)  #  Soft delete
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def delete(self, *args, **kwargs):
        """Soft delete task instead of permanent removal"""
        self.is_deleted = True
        self.save()

    def __str__(self):
        return f"{self.title} - {self.status}"

# 3️  Comment Model (For task discussions)
class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="task_comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="task_comments")
    content = models.TextField(default="No content")  #  Set default value
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.content[:30]}"

# 4️ Collaboration Model (For team assignments)
class Collaboration(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="collaborators")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=[("admin", "Admin"), ("member", "Member")])

    class Meta:
        unique_together = ("project", "user")  #  Prevent duplicate user assignments

    def __str__(self):
        return f"{self.user.username} - {self.role} in {self.project.name}"

# 5️ Notifications Model (For mentions, task updates, deadlines)
class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ("mention", "Mention"),
        ("deadline", "Deadline Reminder"),
        ("task_update", "Task Update"),
        ("general", "General"),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default="general")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:50]}"




