from app.rag.embedding import generate_embedding
from app.rag.vector_store import PineconeVectorStore


class RAGRetriever:

    def __init__(self):
        self.vector_store = PineconeVectorStore()

    def search(self, query, top_k=5, partner_id=None):
        query_embedding = generate_embedding(query)

        filter = None

        if partner_id:
            filter = {"partner_id": partner_id}

        results = self.vector_store.search(
            query_embedding=query_embedding, top_k=top_k, filter=filter
        )

        return results
