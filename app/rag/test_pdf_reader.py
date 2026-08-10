import os

from app.rag.pdf_reader import extract_text_from_pdf

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

PDF_PATH = os.path.join(PROJECT_ROOT, "data", "generated", "documents", "P001.pdf")


text = extract_text_from_pdf(PDF_PATH)

print("=" * 60)
print("EXTRACTED PDF TEXT")
print("=" * 60)
print(text)
