"""
Script to convert systemPrompt.txt to systemPrompt.pdf
This allows easy modification of the system prompt via text file.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
import os

def create_pdf_from_txt(txt_path: str, pdf_path: str):
    """
    Convert a text file to a formatted PDF.
    
    Args:
        txt_path: Path to the input text file
        pdf_path: Path to the output PDF file
    """
    # Read the text file
    with open(txt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create PDF
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=0.75*inch,
        rightMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor='#1f77b4',
        spaceAfter=12,
        spaceBefore=12
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor='#2ca02c',
        spaceAfter=8,
        spaceBefore=8
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=12,
        textColor='#d62728',
        spaceAfter=6,
        spaceBefore=6
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=10,
        leading=14,
        spaceAfter=6
    )
    
    code_style = ParagraphStyle(
        'CustomCode',
        parent=styles['Code'],
        fontSize=9,
        fontName='Courier',
        leftIndent=20,
        spaceAfter=6
    )
    
    # Build content
    story = []
    lines = content.split('\n')
    in_code_block = False
    
    for line in lines:
        # Handle code blocks
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            continue
        
        if in_code_block:
            # Format as code
            story.append(Paragraph(line.replace('<', '&lt;').replace('>', '&gt;'), code_style))
            continue
        
        # Handle headings
        if line.startswith('# ') and not line.startswith('##'):
            text = line[2:].strip()
            story.append(Paragraph(text, title_style))
        elif line.startswith('## '):
            text = line[3:].strip()
            story.append(Paragraph(text, heading_style))
        elif line.startswith('### '):
            text = line[4:].strip()
            story.append(Paragraph(text, subheading_style))
        elif line.strip() == '':
            story.append(Spacer(1, 0.1*inch))
        else:
            # Regular text
            text = line.strip()
            if text:
                # Handle special characters
                text = text.replace('<', '&lt;').replace('>', '&gt;')
                story.append(Paragraph(text, body_style))
    
    # Build PDF
    doc.build(story)
    print(f"✅ PDF created successfully: {pdf_path}")


if __name__ == "__main__":
    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define paths
    txt_path = os.path.join(script_dir, "systemPrompt.txt")
    pdf_path = os.path.join(script_dir, "systemPrompt.pdf")
    
    # Check if text file exists
    if not os.path.exists(txt_path):
        print(f"❌ Error: {txt_path} not found!")
        exit(1)
    
    # Check if PDF already exists
    if os.path.exists(pdf_path):
        print(f"ℹ️  Existing PDF found: {pdf_path}")
        print(f"   This file will be overwritten...")
    
    # Convert to PDF
    print(f"\n📄 Converting {txt_path} to PDF...")
    create_pdf_from_txt(txt_path, pdf_path)
    print(f"✅ System prompt PDF is ready at: {pdf_path}")
    print(f"   The optimizer will use this file on next initialization.")
