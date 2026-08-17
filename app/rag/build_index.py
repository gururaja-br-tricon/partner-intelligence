import os
import sys

sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
)

from app.config import settings
from app.llm.openai_compatible import get_provider
from app.rag.pipeline import build_index, default_documents_dir

LOCAL_STORE_DEFAULT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "generated",
    "doc_chunks.json",
)
SNOWFLAKE_STORE = "snowflake"


def main():
    store_target = os.getenv("RAG_STORE", "local").strip().lower()

    provider = get_provider()

    if store_target == SNOWFLAKE_STORE:
        print("Building RAG index in Snowflake PARTNER_DOC_CHUNKS via numpy cosine.")
        total = build_index(
            documents_dir=default_documents_dir(),
            provider=provider,
        )
    else:
        print(f"Building RAG index locally at: {LOCAL_STORE_DEFAULT}")
        total = build_index(
            documents_dir=default_documents_dir(),
            provider=provider,
            local_store_path=LOCAL_STORE_DEFAULT,
        )

    print(f"Indexed {total} document chunks.")


if __name__ == "__main__":
    main()
