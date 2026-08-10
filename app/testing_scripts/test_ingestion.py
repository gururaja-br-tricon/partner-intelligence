import os

from app.rag.ingestion import RAGIngestionService
from app.rag.models import DocumentMetadata

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

PDF_PATH = os.path.join(PROJECT_ROOT, "data", "generated", "documents", "P001.pdf")


metadata = DocumentMetadata(
    document_id="P001",
    document_name="P001.pdf",
    document_type="partner_profile",
    partner_id="P001",
    partner_name="Nexora Technologies",
)


service = RAGIngestionService()

result = service.ingest_document(file_path=PDF_PATH, metadata=metadata)

print("=" * 60)
print("INGESTION RESULT")
print("=" * 60)

print(result)
