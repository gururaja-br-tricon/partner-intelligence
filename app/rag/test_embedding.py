import os

from app.rag.pdf_reader import extract_text_from_pdf
from app.rag.chunker import chunk_document
from app.rag.embedding import generate_embedding

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

PDF_PATH = os.path.join(PROJECT_ROOT, "data", "generated", "documents", "P001.pdf")


text = extract_text_from_pdf(PDF_PATH)

chunks = chunk_document(
    text=text, partner_id="P001", partner_name="Nexora Technologies"
)

chunk = chunks[0]

embedding = generate_embedding(chunk["content"])

print("=" * 60)
print("EMBEDDING TEST")
print("=" * 60)

print("Section:", chunk["section"])
print("Embedding dimensions:", len(embedding))
print("First 5 values:", embedding[:5])
