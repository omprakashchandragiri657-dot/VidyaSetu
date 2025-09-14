from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from django.conf import settings
from django.http import HttpResponse
from io import BytesIO
import os


def generate_student_portfolio(student_profile):
    """
    Generate a PDF portfolio for a student containing all their approved achievements
    """
    buffer = BytesIO()
    
    # Create the PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18
    )
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        textColor=colors.darkblue
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=14,
        spaceAfter=8,
        textColor=colors.darkgreen
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6
    )
    
    # Build the content
    story = []
    
    # Title
    title = Paragraph("Student Achievement Portfolio", title_style)
    story.append(title)
    story.append(Spacer(1, 20))
    
    # Student Information
    student_info = Paragraph("Student Information", heading_style)
    story.append(student_info)
    
    student_data = [
        ['Name:', f"{student_profile.user.get_full_name()}"],
        ['Student ID:', student_profile.student_id],
        ['Email:', student_profile.user.email],
        ['College:', student_profile.user.college.name],
        ['Course:', student_profile.course],
        ['Branch:', student_profile.branch or 'N/A'],
        ['Year of Admission:', str(student_profile.year_of_admission)],
    ]
    
    if student_profile.phone_number:
        student_data.append(['Phone:', student_profile.phone_number])
    
    student_table = Table(student_data, colWidths=[2*inch, 4*inch])
    student_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(student_table)
    story.append(Spacer(1, 20))
    
    # Achievements Section
    achievements = student_profile.achievements.filter(status='approved').order_by('-date_achieved')
    
    if achievements.exists():
        achievements_title = Paragraph("Approved Achievements", heading_style)
        story.append(achievements_title)
        story.append(Spacer(1, 12))
        
        for i, achievement in enumerate(achievements, 1):
            # Achievement title
            achievement_title = Paragraph(f"{i}. {achievement.title}", subheading_style)
            story.append(achievement_title)
            
            # Achievement details
            achievement_data = [
                ['Category:', achievement.get_category_display()],
                ['Date Achieved:', achievement.date_achieved.strftime('%B %d, %Y')],
                ['Approved By:', achievement.approved_by.get_full_name() if achievement.approved_by else 'N/A'],
                ['Approved On:', achievement.approved_at.strftime('%B %d, %Y at %I:%M %p') if achievement.approved_at else 'N/A'],
            ]
            
            achievement_table = Table(achievement_data, colWidths=[1.5*inch, 4.5*inch])
            achievement_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(achievement_table)
            
            # Description
            description = Paragraph(f"<b>Description:</b><br/>{achievement.description}", normal_style)
            story.append(description)
            
            # Evidence file info
            if achievement.evidence_file:
                evidence_info = Paragraph(f"<b>Evidence:</b> {achievement.evidence_file.name}", normal_style)
                story.append(evidence_info)
            
            story.append(Spacer(1, 15))
    else:
        no_achievements = Paragraph("No approved achievements found.", normal_style)
        story.append(no_achievements)
    
    # Footer
    story.append(Spacer(1, 30))
    footer = Paragraph(
        f"Generated on {student_profile.user.college.name} Student Hub System",
        ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER,
            textColor=colors.grey
        )
    )
    story.append(footer)
    
    # Build PDF
    doc.build(story)
    
    # Get the value of the BytesIO buffer and write it to the response
    pdf = buffer.getvalue()
    buffer.close()
    
    return pdf


def create_pdf_response(pdf_content, filename):
    """
    Create an HTTP response with PDF content
    """
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.write(pdf_content)
    return response
