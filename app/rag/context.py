from app.rag.retriever import RAGRetriever


class RAGContextBuilder:

    def __init__(self):
        self.retriever = RAGRetriever()

    def build_context(self, query, top_k=5, partner_id=None):
        results = self.retriever.search(query=query, top_k=top_k, partner_id=partner_id)

        contexts = []

        for match in results["matches"]:
            metadata = match["metadata"]

            contexts.append(
                {
                    "score": match["score"],
                    "partner_id": metadata.get("partner_id"),
                    "partner_name": metadata.get("partner_name"),
                    "section": metadata.get("section"),
                    "content": metadata.get("content"),
                }
            )

        return contexts
