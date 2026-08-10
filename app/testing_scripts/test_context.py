from app.rag.context import RAGContextBuilder


builder = RAGContextBuilder()

# questions = [
#     "What are Nexora's strongest technology capabilities?",
#     "Which partners have strong cybersecurity capabilities?",
#     "Which partner focuses on generative AI?",
#     "What differentiates Nexora from other technology partners?",
#     "What is P001's strategic focus?"
# ]

# for question in questions:
#     print()
#     print("=" * 60)
#     print("QUESTION:", question)
#     print("=" * 60)

#     contexts = builder.build_context(query=question, top_k=10)

#     for context in contexts:
#         print()
#         print("Partner:", context["partner_name"])
#         print("Section:", context["section"])
#         print("Score:", context["score"])
#         print("Content:", context["content"])

contexts = builder.build_context(
    query="What is P001's strategic focus?",
    top_k=5,
    partner_id="P001"
)
for context in contexts:
    print()
    print(f"query = What is P001's strategic focus? | partner_id = P001")
    print("Partner:", context["partner_name"])
    print("Section:", context["section"])
    print("Score:", context["score"])
    print("Content:", context["content"])


contexts = builder.build_context(
    query="Which partners have strong cybersecurity capabilities?",
    top_k=5
)

for context in contexts:
    print()
    print(f"query = Which partners have strong cybersecurity capabilities? | partner_id = None")
    print("Partner:", context["partner_name"])
    print("Section:", context["section"])
    print("Score:", context["score"])
    print("Content:", context["content"])
