"""
Create Professional Subscription Pricing PDF for DreamFrame LLC
"""

import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from subscription_plans import SUBSCRIPTION_PLANS

# DreamFrame brand colors
DREAMFRAME_CYAN = HexColor('#00ffff')
DREAMFRAME_DARK = HexColor('#1a1a1a')
DREAMFRAME_GRAY = HexColor('#2a2a2a')
DREAMFRAME_LIGHT_GRAY = HexColor('#cccccc')

def create_subscription_pricing_pdf():
    """Create comprehensive subscription pricing PDF"""
    
    filename = "DreamFrame_Subscription_Pricing_Guide.pdf"
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=1*inch,
        bottomMargin=1*inch
    )
    
    # Get styles and create custom ones
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=DREAMFRAME_CYAN,
        alignment=TA_CENTER,
        spaceAfter=30,
        fontName='Helvetica-Bold'
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading2'],
        fontSize=18,
        textColor=DREAMFRAME_CYAN,
        alignment=TA_CENTER,
        spaceAfter=20,
        fontName='Helvetica-Bold'
    )
    
    subheader_style = ParagraphStyle(
        'CustomSubHeader',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=black,
        alignment=TA_LEFT,
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        textColor=black,
        alignment=TA_LEFT,
        spaceAfter=12,
        fontName='Helvetica'
    )
    
    price_style = ParagraphStyle(
        'PriceStyle',
        parent=styles['Normal'],
        fontSize=20,
        textColor=DREAMFRAME_CYAN,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Build document content
    story = []
    
    # Title page
    story.append(Paragraph("DREAMFRAME LLC", title_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Subscription Pricing Guide", header_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Professional Video Production Services", body_style))
    story.append(Paragraph("Veteran Owned & Operated", body_style))
    story.append(Spacer(1, 1*inch))
    
    # Introduction
    story.append(Paragraph("Transform Your Memories Into Professional Videos", subheader_style))
    story.append(Paragraph(
        "DreamFrame LLC offers subscription-based video production services designed to bring your memories to life. "
        "Our AI-powered platform combines cutting-edge technology with professional video editing to create stunning "
        "VideoGrams, Quick Clips, and Family Memories that capture your most precious moments.",
        body_style
    ))
    story.append(Spacer(1, 0.5*inch))
    
    # Subscription benefits
    story.append(Paragraph("Why Choose a Subscription?", subheader_style))
    benefits = [
        "Predictable monthly pricing with no surprise costs",
        "Priority processing for all video projects",
        "Access to premium AI video generation technology",
        "Dedicated customer support and project management",
        "Flexible usage limits that scale with your needs",
        "Annual plans include 2 months free (up to $398 in savings)"
    ]
    
    for benefit in benefits:
        story.append(Paragraph(f"• {benefit}", body_style))
    
    story.append(PageBreak())
    
    # Subscription Plans
    story.append(Paragraph("Subscription Plans", title_style))
    story.append(Spacer(1, 0.5*inch))
    
    for plan_id, plan_data in SUBSCRIPTION_PLANS.items():
        # Plan header
        plan_name = plan_data['name']
        if plan_id == 'professional':
            plan_name += " (Most Popular)"
        
        story.append(Paragraph(plan_name, header_style))
        
        # Pricing table
        price_data = [
            ['Billing Cycle', 'Price', 'Annual Savings'],
            ['Monthly', f"${plan_data['monthly_price']}/month", '-'],
            ['Annual', f"${plan_data['annual_price']}/year", f"${(plan_data['monthly_price'] * 12) - plan_data['annual_price']} (2 months free)"]
        ]
        
        price_table = Table(price_data, colWidths=[2*inch, 1.5*inch, 2*inch])
        price_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), DREAMFRAME_CYAN),
            ('TEXTCOLOR', (0, 0), (-1, 0), black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), white),
            ('GRID', (0, 0), (-1, -1), 1, black)
        ]))
        
        story.append(price_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Features
        story.append(Paragraph("What's Included:", subheader_style))
        for feature in plan_data['features']:
            story.append(Paragraph(f"• {feature}", body_style))
        
        story.append(Spacer(1, 0.5*inch))
    
    story.append(PageBreak())
    
    # Service Descriptions
    story.append(Paragraph("Service Descriptions", title_style))
    story.append(Spacer(1, 0.5*inch))
    
    services = {
        'VideoGrams': {
            'description': '5-second promotional videos perfect for social media and quick sharing',
            'features': ['High-impact visual storytelling', 'Social media optimized', 'Quick turnaround']
        },
        'Quick Clips': {
            'description': 'Short-form videos (15-30 seconds) for capturing key moments and highlights',
            'features': ['Dynamic editing', 'Professional transitions', 'Music integration']
        },
        'Family Memories': {
            'description': 'Longer-form videos (1-3 minutes) that tell complete stories of family moments',
            'features': ['Narrative storytelling', 'Multiple photo integration', 'Emotional soundtracks']
        },
        'Military Tributes': {
            'description': 'Honor service members with dignified tribute videos',
            'features': ['Patriotic themes', 'Respectful presentation', 'Veteran-crafted content']
        },
        'Wedding Stories': {
            'description': 'Romantic wedding videos that capture the magic of your special day',
            'features': ['Cinematic quality', 'Romantic styling', 'Professional editing']
        }
    }
    
    for service_name, service_info in services.items():
        story.append(Paragraph(service_name, subheader_style))
        story.append(Paragraph(service_info['description'], body_style))
        for feature in service_info['features']:
            story.append(Paragraph(f"• {feature}", body_style))
        story.append(Spacer(1, 0.2*inch))
    
    story.append(PageBreak())
    
    # Frequently Asked Questions
    story.append(Paragraph("Frequently Asked Questions", title_style))
    story.append(Spacer(1, 0.5*inch))
    
    faqs = [
        {
            'q': 'How does the subscription billing work?',
            'a': 'You are billed monthly or annually based on your chosen plan. Usage resets each billing cycle, and you can upgrade or downgrade at any time.'
        },
        {
            'q': 'What happens if I exceed my monthly limits?',
            'a': 'Additional videos beyond your plan limits can be purchased individually, or you can upgrade to a higher tier for more included videos.'
        },
        {
            'q': 'Can I cancel my subscription anytime?',
            'a': 'Yes, you can cancel your subscription at any time. You will continue to have access until the end of your current billing period.'
        },
        {
            'q': 'How long does video production take?',
            'a': 'VideoGrams: 24-48 hours, Quick Clips: 2-3 days, Family Memories: 3-5 days, Military Tributes and Wedding Stories: 5-7 days.'
        },
        {
            'q': 'What file formats do you accept?',
            'a': 'We accept most common image formats (JPG, PNG, HEIC) and video formats (MP4, MOV, AVI). Files up to 500MB are supported.'
        },
        {
            'q': 'Do you offer refunds?',
            'a': 'We offer a 7-day satisfaction guarantee. If you are not completely satisfied with your video, we will revise it or provide a full refund.'
        }
    ]
    
    for faq in faqs:
        story.append(Paragraph(f"Q: {faq['q']}", subheader_style))
        story.append(Paragraph(f"A: {faq['a']}", body_style))
        story.append(Spacer(1, 0.2*inch))
    
    # Contact Information
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Get Started Today", header_style))
    story.append(Paragraph(
        "Ready to transform your memories into professional videos? Visit our website to choose your plan and "
        "start creating amazing videos today.",
        body_style
    ))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Website: https://dreamframe.replit.app", body_style))
    story.append(Paragraph("Email: contact@dreamframe.com", body_style))
    story.append(Paragraph("Veteran Owned & Operated Since 2024", body_style))
    
    # Build PDF
    doc.build(story)
    
    print(f"✅ Subscription pricing PDF created: {filename}")
    return filename

if __name__ == "__main__":
    create_subscription_pricing_pdf()