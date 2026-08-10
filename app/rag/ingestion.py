from app.rag.pdf_reader import extract_text_from_pdf
from app.rag.chunker import chunk_document
from app.rag.embedding import generate_embeddings
from app.rag.vector_store import PineconeVectorStore
from app.rag.models import DocumentMetadata


class RAGIngestionService:

    def __init__(self):
        self.vector_store = PineconeVectorStore()

    def ingest_document(self, file_path, metadata):
        text = extract_text_from_pdf(file_path)

        if not text.strip():
            raise ValueError(f"No text extracted from {file_path}")

        chunks = chunk_document(text=text, metadata=metadata)

        if not chunks:
            raise ValueError(f"No chunks generated from {file_path}")

        texts = [chunk.content for chunk in chunks]

        embeddings = generate_embeddings(texts)

        count = self.vector_store.upsert(chunks=chunks, embeddings=embeddings)

        return {
            "document_id": metadata.document_id,
            "document_name": metadata.document_name,
            "chunks_created": len(chunks),
            "vectors_stored": count,
        }
