from app.rag.retriever import RAGRetriever

retriever = RAGRetriever()


query = "What are Nexora's strongest technology capabilities?"


results = retriever.search(query=query, top_k=5)


print("=" * 60)
print("SEARCH RESULTS")
print("=" * 60)


for index, match in enumerate(results["matches"], start=1):
    print()
    print(f"--- RESULT {index} ---")
    print("Score:", match["score"])

    metadata = match["metadata"]

    print("Partner:", metadata.get("partner_name"))
    print("Section:", metadata.get("section"))
    print("Content:", metadata.get("content"))
