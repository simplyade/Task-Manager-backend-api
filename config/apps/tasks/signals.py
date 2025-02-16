from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from .models import Comment, Notification,Task
from apps.authentication.models import User
from datetime import timedelta
from django.contrib.auth import get_user_model
import re

User = get_user_model()

# Mention Notification Signal
@receiver(post_save, sender=Comment)
def notify_mentions(sender, instance, **kwargs):
    """
    Detects mentions in comments and creates notifications.
    """
    mentioned_usernames = re.findall(r'@(\w+)', instance.content) # Extract @mentions
    mentioned_users = User.objects.filter(username_in=mentioned_usernames)
    for user in mentioned_users:
        if user:
            Notification.objects.create(
                user=user,
                message=f"You were mentioned by  {instance.user.username} in a comment.",
                notification_type="mention",
            )
            
# Task Deadline Reminder Signal
@receiver(post_save, sender=Task)
def notify_task_deadline(sender, instance, **kwargs):
    """
    Notify users if a task deadline is approaching.
    """
    if instance.deadline and instance.deadline - now() <= timedelta(hours=24):  # 24-hour reminder
        for assignee in instance.assignees.all():
            Notification.objects.create(
                user=assignee,
                message=f"Reminder: Task '{instance.title}' is due soon!",
                notification_type="deadline"
            )
