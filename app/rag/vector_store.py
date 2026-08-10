import os

from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

INDEX_NAME = "partner-intelligence"

class PineconeVectorStore:

    def __init__(self):
        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            raise RuntimeError("PINECONE_API_KEY is not set")

        self.client = Pinecone(api_key=api_key)
        self.index = self.client.Index(INDEX_NAME)

    def upsert(self, chunks, embeddings):
        vectors = []

        for chunk, embedding in zip(chunks, embeddings):
            vectors.append(
                {
                    "id": chunk.chunk_id,
                    "values": embedding,
                    "metadata": {
                        "document_id": chunk.document_id,
                        "document_name": chunk.document_name,
                        "document_type": chunk.document_type,
                        "section": chunk.section,
                        "content": chunk.content,
                        "partner_id": chunk.partner_id or "",
                        "partner_name": chunk.partner_name or "",
                    },
                }
            )

        self.index.upsert(vectors=vectors)
        return len(vectors)

    def search(self, query_embedding, top_k=5, filter=None):
        return self.index.query(vector=query_embedding, top_k=top_k, include_metadata=True, filter=filter)

    def delete_document(self, document_id):
        self.index.delete(filter={"document_id": document_id})
