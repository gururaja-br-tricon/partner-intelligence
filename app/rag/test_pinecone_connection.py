import os

from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

api_key = os.getenv("PINECONE_API_KEY")

if not api_key:
    raise RuntimeError("PINECONE_API_KEY is not set")

pc = Pinecone(api_key=api_key)

print("Pinecone connection successful")
print("Indexes:", pc.list_indexes().names())
