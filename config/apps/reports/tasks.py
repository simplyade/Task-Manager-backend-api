from celery import shared_task
from django.core.mail import EmailMessage
from .utils import generate_csv_report

@shared_task
def send_scheduled_report(email):
    csv_report = generate_csv_report()
    email = EmailMessage(
        subject="Scheduled Task Report",
        body="Attached is the latest task report.",
        to=[email],
    )
    email.attach("report.csv", csv_report.content, "text/csv")
    email.send()
