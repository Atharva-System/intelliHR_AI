import PyPDF2
from docx import Document
import os

def pdf_to_text(file_path):
    text = ""
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == ".pdf":
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                    
    elif ext in [".docx", ".doc"]:
        doc = Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
            
    else:
        raise ValueError(f"Unsupported file type: {ext}")
    
    return text