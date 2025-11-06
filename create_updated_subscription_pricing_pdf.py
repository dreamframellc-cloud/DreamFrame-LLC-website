"""
Create Updated Subscription Pricing Guide with Fast Turnaround Options
Comprehensive PDF with new speed tiers and automation levels
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.platypus.flowables import HRFlowable
from datetime import datetime
import os

def create_updated_subscription_pricing_pdf():
    """Create comprehensive subscription pricing PDF with fast turnaround options"""
    
    filename = "DreamFrame_Updated_Subscription_Pricing_Guide.pdf"
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=108,
        bottomMargin=72
    )
    
    # Custom styles
    styles = getSampleStyleSheet()
    
    # Title style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor('#1a1a1a'),
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Header style
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=20,
        spaceBefore=20,
        textColor=colors.HexColor('#2c3e50'),
        alignment=TA_LEFT,
        fontName='Helvetica-Bold'
    )
    
    # Subheader style
    subheader_style = ParagraphStyle(
        'CustomSubHeader',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=15,
        spaceBefore=15,
        textColor=colors.HexColor('#34495e'),
        alignment=TA_LEFT,
        fontName='Helvetica-Bold'
    )
    
    # Body style
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=12,
        textColor=colors.HexColor('#2c3e50'),
        alignment=TA_JUSTIFY,
        fontName='Helvetica'
    )
    
    # Highlight style
    highlight_style = ParagraphStyle(
        'Highlight',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=12,
        textColor=colors.HexColor('#e74c3c'),
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Build document content
    story = []
    
    # Title page
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("DREAMFRAME LLC", title_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("UPDATED SUBSCRIPTION PRICING GUIDE", 
                          ParagraphStyle('Subtitle', parent=styles['Title'], fontSize=16, 
                                       textColor=colors.HexColor('#7f8c8d'), alignment=TA_CENTER)))
    
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("With Fast Turnaround Service", 
                          ParagraphStyle('SubtitleEmphasis', parent=styles['Title'], fontSize=14, 
                                       textColor=colors.HexColor('#e74c3c'), alignment=TA_CENTER, fontName='Helvetica-Bold')))
    
    story.append(Spacer(1, 1*inch))
    
    # Date and version
    story.append(Paragraph(f"Updated: {datetime.now().strftime('%B %d, %Y')}", 
                          ParagraphStyle('Date', parent=styles['Normal'], fontSize=10, 
                                       textColor=colors.HexColor('#95a5a6'), alignment=TA_CENTER)))
    
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Version 2.0 - Fast Turnaround Edition", 
                          ParagraphStyle('Version', parent=styles['Normal'], fontSize=10, 
                                       textColor=colors.HexColor('#95a5a6'), alignment=TA_CENTER)))
    
    story.append(PageBreak())
    
    # Executive Summary
    story.append(Paragraph("Executive Summary", header_style))
    story.append(Paragraph(
        "DreamFrame LLC has revolutionized our video production service with the introduction of comprehensive "
        "fast turnaround options. Our new subscription model now includes three speed tiers: RUSH (2-4 hours), "
        "EXPRESS (same-day), and STANDARD (1-2 days), powered by advanced AI automation pipelines.",
        body_style
    ))
    
    story.append(Paragraph(
        "This updated pricing guide reflects our enhanced service capabilities, featuring intelligent automation "
        "levels, dynamic pricing multipliers, and industry-leading delivery times while maintaining our "
        "commitment to quality and customer satisfaction.",
        body_style
    ))
    
    story.append(Spacer(1, 0.3*inch))
    
    # Key Features Highlight Box
    key_features_data = [
        ['🚀 RUSH Delivery', '2-4 Hours', 'Full AI Automation'],
        ['⚡ EXPRESS Delivery', 'Same Day', 'AI-Assisted Production'],
        ['📅 STANDARD Delivery', '1-2 Days', 'Human Quality Control'],
        ['🤖 Automation Pipeline', '288+ Projects/Day', '95% On-Time Delivery'],
        ['💰 Dynamic Pricing', '2x RUSH | 1.5x EXPRESS', 'Real-Time Quotes']
    ]
    
    key_features_table = Table(key_features_data, colWidths=[2*inch, 1.5*inch, 2*inch])
    key_features_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#ecf0f1')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7'))
    ]))
    
    story.append(key_features_table)
    story.append(Spacer(1, 0.5*inch))
    
    # Subscription Plans Overview
    story.append(Paragraph("Subscription Plans Overview", header_style))
    
    # Plans comparison table
    plans_data = [
        ['Feature', 'Starter Plan', 'Professional Plan', 'Enterprise Plan'],
        ['Monthly Price', '$29/month', '$79/month', '$199/month'],
        ['Annual Price', '$290/year (2 months free)', '$790/year (2 months free)', '$1,990/year (2 months free)'],
        ['VideoGrams/Month', '10 included', '25 included', '100 included'],
        ['Quick Clips/Month', '5 included', '15 included', '50 included'],
        ['Family Memories/Month', '2 included', '8 included', '25 included'],
        ['Military Tributes/Month', '1 included', '5 included', '15 included'],
        ['Wedding Stories/Month', '1 included', '3 included', '10 included'],
        ['RUSH Priority Access', '❌', '✅ Limited', '✅ Unlimited'],
        ['EXPRESS Priority', '✅ Limited', '✅ Included', '✅ Unlimited'],
        ['AI Automation Level', 'Standard', 'AI-Assisted', 'Full Automation'],
        ['Support Level', 'Email', 'Priority Email', 'Phone + Dedicated Rep']
    ]
    
    plans_table = Table(plans_data, colWidths=[2.2*inch, 1.6*inch, 1.6*inch, 1.6*inch])
    plans_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
        ('BACKGROUND', (1, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#ecf0f1'))
    ]))
    
    story.append(plans_table)
    story.append(PageBreak())
    
    # Fast Turnaround Pricing Details
    story.append(Paragraph("Fast Turnaround Pricing Structure", header_style))
    
    story.append(Paragraph("Speed Tier Multipliers", subheader_style))
    story.append(Paragraph(
        "Our dynamic pricing system applies speed multipliers to base subscription rates, "
        "ensuring fair pricing while maintaining premium service quality at accelerated delivery speeds.",
        body_style
    ))
    
    # Speed pricing table
    speed_pricing_data = [
        ['Service Type', 'Base Price', 'STANDARD (1-2 days)', 'EXPRESS (same day)', 'RUSH (2-4 hours)'],
        ['VideoGrams (5 sec)', '$50', '$50 (1.0x)', '$75 (1.5x)', '$100 (2.0x)'],
        ['Quick Clips (15 sec)', '$75', '$75 (1.0x)', '$135 (1.8x)', '$187 (2.5x)'],
        ['Family Memories (60 sec)', '$200', '$200 (1.0x)', '$400 (2.0x)', '$600 (3.0x)'],
        ['Military Tributes (120 sec)', '$300', '$300 (1.0x)', '$600 (2.0x)', '$900 (3.0x)'],
        ['Wedding Stories (180 sec)', '$500', '$500 (1.0x)', '$1,000 (2.0x)', '$1,500 (3.0x)']
    ]
    
    speed_pricing_table = Table(speed_pricing_data, colWidths=[1.8*inch, 1*inch, 1.4*inch, 1.4*inch, 1.4*inch])
    speed_pricing_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#c0392b')),
        ('BACKGROUND', (4, 1), (4, -1), colors.HexColor('#fff5f5')),  # RUSH column highlight
        ('BACKGROUND', (3, 1), (3, -1), colors.HexColor('#fff8f0')),  # EXPRESS column highlight
        ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#f8f9fa'))
    ]))
    
    story.append(speed_pricing_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Automation Pipeline Details
    story.append(Paragraph("Automation Pipeline Technology", subheader_style))
    
    automation_data = [
        ['Automation Level', 'Project Types', 'Delivery Time', 'Quality Score', 'Capacity/Hour'],
        ['Full Automation', 'VideoGrams, Simple Clips', '15-30 minutes', '92% AI Quality', '12 projects'],
        ['AI-Assisted', 'Family Memories, Complex Clips', '30-90 minutes', '95% Hybrid Quality', '4 projects'],
        ['Manual Quality', 'Military Tributes, Weddings', '2-6 hours', '98% Human Quality', '0.5 projects']
    ]
    
    automation_table = Table(automation_data, colWidths=[1.5*inch, 1.8*inch, 1.2*inch, 1.2*inch, 1.3*inch])
    automation_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#2980b9')),
        ('BACKGROUND', (1, 1), (-1, -1), colors.HexColor('#f0f8ff'))
    ]))
    
    story.append(automation_table)
    story.append(Spacer(1, 0.5*inch))
    
    # Production Capacity Metrics
    story.append(Paragraph("Production Capacity & Performance Metrics", subheader_style))
    
    metrics_data = [
        ['Metric', 'Current Performance', 'Target Goal', 'Industry Benchmark'],
        ['Daily Project Capacity', '288+ projects', '350 projects', '150 projects'],
        ['RUSH Order Capacity', '58 projects/day', '70 projects/day', '20 projects/day'],
        ['On-Time Delivery Rate', '95%', '98%', '85%'],
        ['Customer Quality Rating', '4.8/5 stars', '4.9/5 stars', '4.2/5 stars'],
        ['Automation Efficiency Gain', '30% time savings', '40% time savings', '15% time savings'],
        ['Average Turnaround Reduction', '67% faster', '75% faster', '25% faster']
    ]
    
    metrics_table = Table(metrics_data, colWidths=[2*inch, 1.6*inch, 1.6*inch, 1.8*inch])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#229954')),
        ('BACKGROUND', (1, 1), (1, -1), colors.HexColor('#f0fff0')),  # Performance highlight
        ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#f8f9fa'))
    ]))
    
    story.append(metrics_table)
    story.append(PageBreak())
    
    # Service Descriptions
    story.append(Paragraph("Enhanced Service Descriptions", header_style))
    
    services = [
        {
            'name': 'VideoGrams (5-second promotional videos)',
            'description': 'Ultra-short promotional content optimized for social media impact. Perfect for business announcements, product reveals, and brand awareness campaigns.',
            'automation': 'Full AI automation with brand template application',
            'rush_time': '15 minutes',
            'features': ['AI content analysis', 'Auto frame extraction', 'Brand overlay application', 'Music sync optimization']
        },
        {
            'name': 'Quick Clips (15-second dynamic content)',
            'description': 'Short-form content ideal for social media platforms. Combines multiple photos or short video segments into engaging promotional material.',
            'automation': 'AI-assisted production with human creative oversight',
            'rush_time': '30 minutes',
            'features': ['Scene detection', 'Auto-editing', 'Transition effects', 'Social media optimization']
        },
        {
            'name': 'Family Memories (60-second emotional storytelling)',
            'description': 'Heartwarming family stories that preserve precious moments. Combines photos, videos, and music to create lasting memories.',
            'automation': 'AI-assisted with human emotional guidance',
            'rush_time': '90 minutes',
            'features': ['Story flow optimization', 'Music matching', 'Color grading', 'Emotional arc development']
        },
        {
            'name': 'Military Tributes (120-second honor presentations)',
            'description': 'Respectful tributes honoring military service and sacrifice. Created with appropriate reverence and patriotic styling.',
            'automation': 'Human-guided production with AI assistance',
            'rush_time': '180 minutes',
            'features': ['Respectful editing standards', 'Patriotic music selection', 'Honor guard effects', 'Memorial formatting']
        },
        {
            'name': 'Wedding Stories (180-second romantic narratives)',
            'description': 'Beautiful wedding highlights capturing the magic of special days. Professional quality with cinematic storytelling.',
            'automation': 'Premium human production with AI enhancement',
            'rush_time': '240 minutes',
            'features': ['Cinematic editing', 'Romantic music scoring', 'Color harmony optimization', 'Professional transitions']
        }
    ]
    
    for service in services:
        story.append(Paragraph(service['name'], subheader_style))
        story.append(Paragraph(service['description'], body_style))
        
        # Service details table
        service_details = [
            ['Automation Level', service['automation']],
            ['RUSH Delivery Time', service['rush_time']],
            ['Key Features', ' • '.join(service['features'])]
        ]
        
        service_table = Table(service_details, colWidths=[1.5*inch, 5.5*inch])
        service_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        
        story.append(service_table)
        story.append(Spacer(1, 0.2*inch))
    
    story.append(PageBreak())
    
    # Billing and Usage Terms
    story.append(Paragraph("Billing and Usage Terms", header_style))
    
    story.append(Paragraph("Monthly Subscription Limits", subheader_style))
    story.append(Paragraph(
        "Each subscription plan includes a specific number of projects per service type. "
        "Additional projects beyond the monthly limit are billed at the per-project rate with applicable speed multipliers.",
        body_style
    ))
    
    story.append(Paragraph("Speed Priority Access", subheader_style))
    story.append(Paragraph(
        "• RUSH priority is limited to Enterprise subscribers and available as add-on for Professional plans\n"
        "• EXPRESS priority is included in Professional and Enterprise plans, limited access for Starter plans\n"
        "• STANDARD delivery is available to all subscription tiers without additional charges",
        body_style
    ))
    
    story.append(Paragraph("Overage Pricing", subheader_style))
    story.append(Paragraph(
        "Projects exceeding monthly limits are charged at standard per-project rates plus applicable speed multipliers. "
        "Subscribers receive 10% discount on overage charges compared to non-subscriber rates.",
        body_style
    ))
    
    story.append(Paragraph("Annual Billing Benefits", subheader_style))
    story.append(Paragraph(
        "Annual subscribers receive two months free (equivalent to 16.7% savings) and priority customer support. "
        "Annual plans also include additional speed priority allocations and enhanced automation features.",
        body_style
    ))
    
    # Contact and Implementation
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Implementation and Support", subheader_style))
    story.append(Paragraph(
        "Our fast turnaround system is fully operational and ready for immediate use. "
        "All subscribers gain access to real-time quote calculators, automation status tracking, "
        "and instant delivery notifications through our enhanced customer portal.",
        body_style
    ))
    
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Contact Information", subheader_style))
    story.append(Paragraph(
        "For subscription inquiries, custom enterprise solutions, or technical support:\n\n"
        "DreamFrame LLC\n"
        "Email: sales@dreamframellc.com\n"
        "Website: dreamframellc.com\n"
        "Fast Turnaround Service: dreamframellc.com/fast-turnaround",
        body_style
    ))
    
    # Footer
    story.append(Spacer(1, 0.5*inch))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#bdc3c7')))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(
        f"© {datetime.now().year} DreamFrame LLC. All rights reserved. Updated Subscription Pricing Guide v2.0",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, 
                      textColor=colors.HexColor('#95a5a6'), alignment=TA_CENTER)
    ))
    
    # Build the PDF
    doc.build(story)
    return filename

if __name__ == "__main__":
    filename = create_updated_subscription_pricing_pdf()
    print(f"Updated subscription pricing PDF created: {filename}")