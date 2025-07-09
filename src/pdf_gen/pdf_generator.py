import io
import os
import requests
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
        for syntagma in paragraph.Sintagmas:
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

            elements.append(Paragraph(line, normal_style))

        # Add space between the translated section and full paragraph
        elements.append(Spacer(1, 20))

        # Second format: just the source text paragraph without translations
        source_only_parts = [s.source_text for s in paragraph.Sintagmas]
        source_only = " ".join(source_only_parts)
        source_only = (
            source_only
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

        elements.append(Paragraph(source_only, normal_style))

        # Add space between different paragraphs
        if paragraph_index < len(bilingual_text.paragraphs) - 1:
            elements.append(Spacer(1, 30))

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
