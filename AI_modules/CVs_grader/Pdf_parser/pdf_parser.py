from pdfminer.high_level import extract_text
def read_pdf(pdf_path):
    text = extract_text(pdf_path)
    return text
