import os

from app.rag.pdf_reader import extract_text_from_pdf
from app.rag.chunker import chunk_document
from app.rag.models import DocumentMetadata

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

PDF_PATH = os.path.join(PROJECT_ROOT, "data", "generated", "documents", "P001.pdf")


text = extract_text_from_pdf(PDF_PATH)

metadata = DocumentMetadata(
    document_id="P001",
    document_name="P001.pdf",
    document_type="partner_profile",
    partner_id="P001",
    partner_name="Nexora Technologies"
)

chunks = chunk_document(
    text=text,
    metadata=metadata
)
print("=" * 60)
print(f"TOTAL CHUNKS: {len(chunks)}")
print("=" * 60)

for index, chunk in enumerate(chunks, start=1):
    print(f"\n--- CHUNK {index} ---")
    print(f"Partner: {chunk.partner_name}")
    print(f"Section: {chunk.section}")
    print(f"Content: {chunk.content}")
