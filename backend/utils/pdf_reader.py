import PyPDF2
import io

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extracts text from a PDF file.
    We use PyPDF2 because it's lightweight, free, and handles
    standard PDFs well. For scanned PDFs we'd need OCR (Tesseract)
    but CVs are almost always text-based.
    """
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text.strip()