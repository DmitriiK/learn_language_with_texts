import io
import os
import requests
import re
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT

from src.data_classes.bilingual_text import BilingualText


def generate_bilingual_pdf(bilingual_text: BilingualText) -> bytes:
    """Generate a PDF with bilingual text formatting with proper Unicode support.

    Args:
        bilingual_text: A BilingualText object containing paragraphs with source
                        and target text.

    Returns:
        bytes: The generated PDF as bytes.
    """
    buffer = io.BytesIO()
    font_name = get_fonts()

    # Create the PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72,
        encoding='utf-8'
    )

    # Create styles with the Unicode-compatible font
    styles = getSampleStyleSheet()
    normal_style = ParagraphStyle(
        'NormalText',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=12,
        leading=18,
        alignment=TA_LEFT,
        encoding='utf-8'
    )

    elements = []

    # Add document title and language info
    elements.append(
        Paragraph(f"Source Language: {bilingual_text.source_language}",
                  normal_style)
    )
    elements.append(
        Paragraph(f"Target Language: {bilingual_text.target_language}",
                  normal_style)
    )
    elements.append(Spacer(1, 20))

    for paragraph_index, paragraph in enumerate(bilingual_text.paragraphs):
        # First format: each syntagma with its translation in green
        is_first_syntagma = True
        previous_ends_with_sentence_end = False
        
        for i, syntagma in enumerate(paragraph.Sintagmas):
            # Check if this syntagma starts with a dash for dialog (including em-dash)
            starts_with_dash = bool(re.match(r'^(-{1,2}|—)\s', syntagma.source_text))
            
            # Handle special characters for XML
            source = (
                syntagma.source_text
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )

            line = source
            if syntagma.target_text:
                target = (
                    syntagma.target_text
                    .replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                )
                line += f' <font color="green">({target})</font>'

            # Add a line break before dialog lines when needed
            needs_line_break = starts_with_dash and (is_first_syntagma or previous_ends_with_sentence_end)
            
            if needs_line_break:
                # Instead of adding <br/>, create a new paragraph for dialog lines
                elements.append(Spacer(1, 12))
            
            elements.append(Paragraph(line, normal_style))
            
            # Update tracking variables for the next iteration
            # Consider colon as sentence ending for dialog purposes
            previous_ends_with_sentence_end = bool(re.search(r'[.!?…:]+$', syntagma.source_text))
            is_first_syntagma = False

        # Add space between the translated section and full paragraph
        elements.append(Spacer(1, 20))

        # Second format: just the source text paragraph without translations
        # Process the text to add line breaks for dialogs
        source_paragraphs = []
        current_paragraph = []
        is_first = True
        prev_ends_with_sentence_end = False
        
        for i, s in enumerate(paragraph.Sintagmas):
            text = s.source_text
            starts_with_dash = bool(re.match(r'^(-{1,2}|—)\s', text))
            
            # If we need a line break, finish the current paragraph and start a new one
            if starts_with_dash and (is_first or prev_ends_with_sentence_end):
                if current_paragraph:  # Only process if we have content
                    source_paragraphs.append(" ".join(current_paragraph))
                    current_paragraph = []
            
            current_paragraph.append(text)
            prev_ends_with_sentence_end = bool(re.search(r'[.!?…:]+$', text))
            is_first = False
        
        # Add the last paragraph if any content remains
        if current_paragraph:
            source_paragraphs.append(" ".join(current_paragraph))
        
        # Add each paragraph separately with proper XML escaping
        for source_text in source_paragraphs:
            escaped_text = (
                source_text
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )
            elements.append(Paragraph(escaped_text, normal_style))

        # Add space between different paragraphs
        if paragraph_index < len(bilingual_text.paragraphs) - 1:
            elements.append(Spacer(1, 30))

    # Add questions and answers if available
    if bilingual_text.questions:
        # Add a section header and some space
        elements.append(Spacer(1, 30))
        elements.append(
            Paragraph("<b>Questions and Answers</b>",
                      ParagraphStyle(
                          'SectionHeader',
                          parent=normal_style,
                          fontSize=14,
                          leading=20,
                          spaceAfter=10
                      ))
        )
        elements.append(Spacer(1, 10))
        
        # Create a style for questions and answers
        question_style = ParagraphStyle(
            'Question',
            parent=normal_style,
            fontSize=12,
            leading=16,
            fontName=font_name,
            spaceAfter=5,
            leftIndent=10
        )
        
        answer_style = ParagraphStyle(
            'Answer',
            parent=normal_style,
            fontSize=11,
            leading=16,
            fontName=font_name,
            leftIndent=20,
            spaceBefore=3,
            spaceAfter=15,
            textColor='#333333'
        )
        
        for i, qa in enumerate(bilingual_text.questions):
            # Escape XML entities in question and answer
            question_text = (
                qa.question
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )
            
            answer_text = (
                qa.answer
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )
            
            # Add the question with numbering
            elements.append(
                Paragraph(f"<b>{i + 1}. {question_text}</b>", question_style)
            )
            
            # Add the answer
            elements.append(
                Paragraph(f"{answer_text}", answer_style)
            )

    # Build the PDF document
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


def get_fonts():
    # Create fonts directory if it doesn't exist
    fonts_dir = os.path.join(os.path.dirname(__file__), "fonts")
    if not os.path.exists(fonts_dir):
        os.makedirs(fonts_dir)

    # Use a specific font that fully supports Turkish characters
    # First check if we already have the font
    font_path = os.path.join(fonts_dir, "NotoSans-Regular.ttf")
    
    # If the font doesn't exist, download it
    if not os.path.exists(font_path):
        font_url = (
            "https://github.com/googlefonts/noto-fonts/raw/main/"
            "hinted/ttf/NotoSans/NotoSans-Regular.ttf"
        )
        response = requests.get(font_url)
        if response.status_code == 200:
            with open(font_path, "wb") as f:
                f.write(response.content)
    
    # Register the font with ReportLab
    font_name = "NotoSans"
    try:
        pdfmetrics.registerFont(TTFont(font_name, font_path))
    except Exception:
        # If for some reason we can't use the downloaded font, fall back to default
        font_name = "Helvetica"
    return font_name
