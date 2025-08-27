import PyPDF2

def pdf_to_text(pdf_path):
    text = ""
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

# Example usage
pdf_path = "example.pdf"
pdf_text = pdf_to_text("./app/services/sample.pdf")
print(pdf_text)
