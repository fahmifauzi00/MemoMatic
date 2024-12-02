from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

def create_docx(minutes_data: dict) -> str:
    doc = Document()
    
    # Add title
    title = doc.add_heading(minutes_data['title'], 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Add sections
    for section in ['summary', 'key_points', 'action_items', 'decisions']:
        if section in minutes_data:
            doc.add_heading(section.title().replace('_', ' '), 1)
            doc.add_paragraph(minutes_data[section])
    
    # Save document
    output_path = "temp/minutes.docx"
    doc.save(output_path)
    return output_path