import os

from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

load_dotenv()

api_key = os.getenv("PINECONE_API_KEY")

if not api_key:
    raise RuntimeError("PINECONE_API_KEY is not set")


INDEX_NAME = "partner-intelligence"

pc = Pinecone(api_key=api_key)


if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_NAME,
        dimension=768,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )

    print(f"Created Pinecone index: {INDEX_NAME}")
else:
    print(f"Pinecone index already exists: {INDEX_NAME}")
