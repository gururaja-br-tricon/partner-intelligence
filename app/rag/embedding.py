from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-mpnet-base-v2"

model = SentenceTransformer(MODEL_NAME)

#for one chunk/query
def generate_embedding(text):
    embedding = model.encode(text, normalize_embeddings=True)

    return embedding.tolist()

#multiple chunks efficiently in a batch
def generate_embeddings(texts):
    embeddings = model.encode(texts, normalize_embeddings=True)

    return embeddings.tolist()
