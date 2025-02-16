import csv
import pdfkit
from django.http import HttpResponse
from django.template.loader import render_to_string
from .models import Report

def generate_csv_report():
    reports = Report.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reports.csv"'
    writer = csv.writer(response)
    writer.writerow(['Title', 'Type', 'Created By', 'Created At'])
    for report in reports:
        writer.writerow([report.title, report.report_type, report.created_by, report.created_at])
    return response

def generate_pdf_report():
    reports = Report.objects.all()
    html = render_to_string('reports/report_template.html', {'reports': reports})
    pdf = pdfkit.from_string(html, False)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    return response
