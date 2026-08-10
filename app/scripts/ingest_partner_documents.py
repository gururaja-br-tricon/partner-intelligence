import os
from app.config import DOCUMENTS_DIR
from app.rag.ingestion import RAGIngestionService
from app.rag.models import DocumentMetadata
from app.repository.snowflake_partner_repository import SnowflakePartnerRepository

partner_repository = SnowflakePartnerRepository()
service = RAGIngestionService()

for filename in sorted(os.listdir(DOCUMENTS_DIR)):

    if not filename.lower().endswith(".pdf"):
        continue

    document_id = os.path.splitext(filename)[0]
    file_path = os.path.join(DOCUMENTS_DIR, filename)

    partner_name = None

    partner = partner_repository.get_partner(document_id)

    if partner:
        partner_name = partner["PARTNER_NAME"]
        print(f"Partner metadata found: {document_id} - {partner_name}")
    else:
        print(f"Partner metadata not found: {document_id}. " "Continuing ingestion.")

    metadata = DocumentMetadata(
        document_id=document_id,
        document_name=filename,
        document_type="partner_profile",
        partner_id=document_id,
        partner_name=partner_name,
    )

    result = service.ingest_document(file_path=file_path, metadata=metadata)
    print(result)
