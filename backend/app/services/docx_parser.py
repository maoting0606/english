from docx import Document
from app.services.parser import parse_word_text

def parse_docx(path: str):
    doc = Document(path)
    text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    return parse_word_text(text), text
