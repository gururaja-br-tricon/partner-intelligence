import os

from app.llm.provider import LLMProvider
from app.rag.chunker import chunk_partner_pdf, list_partner_pdfs
from app.rag.vector_store import (
    Chunk,
    LocalVectorStore,
    SnowflakeVectorStore,
    VectorStore,
)


def get_active_store():
    from app.repository.snowflake_partner_repository import (
        SnowflakePartnerRepository,
    )

    repository = SnowflakePartnerRepository()
    return SnowflakeVectorStore(repository)


def build_index(
    documents_dir: str,
    provider: LLMProvider,
    store: VectorStore | None = None,
    local_store_path: str | None = None,
) -> int:
    if store is None:
        if local_store_path:
            store = LocalVectorStore(local_store_path)
        else:
            try:
                store = get_active_store()
            except Exception:
                raise RuntimeError(
                    "No vector store resolved. Pass local_store_path or "
                    "configure/resolve Snowflake."
                )

    pdf_paths = list_partner_pdfs(documents_dir)

    total_chunks = 0

    for pdf_path in pdf_paths:
        sections = chunk_partner_pdf(pdf_path)

        rows = [s["text"] for s in sections]

        embeddings = provider.embed_many(rows) if rows else []

        chunks = [
            Chunk(
                partner_id=section["partner_id"],
                chunk_index=section["chunk_index"],
                heading=section["heading"],
                text=section["text"],
                embedding=embedding,
            )
            for section, embedding in zip(sections, embeddings)
        ]

        store.add_chunks(chunks)
        total_chunks += len(chunks)

    return total_chunks


def search_documents(
    query: str,
    provider: LLMProvider,
    store: VectorStore,
    top_k: int = 5,
):
    query_embedding = provider.embed(query)
    return store.search(query_embedding, top_k)


def default_documents_dir(project_root: str | None = None) -> str:
    if project_root is None:
        project_root = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
    return os.path.join(project_root, "data", "generated", "documents")
