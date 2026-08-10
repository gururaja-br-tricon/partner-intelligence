import os
from dotenv import load_dotenv

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DOCUMENTS_DIR = os.path.join(PROJECT_ROOT, "data", "generated", "documents")

load_dotenv()

class Settings:
    def __init__(self):


        self.llm_provider = os.getenv("LLM_PROVIDER", "groq").strip().lower()

        self.groq_api_key = os.getenv("GROQ_API_KEY", "").strip()
        self.groq_chat_model = os.getenv("GROQ_CHAT_MODEL", "openai/gpt-oss-120b")
        self.groq_embedding_model = os.getenv(
            "GROQ_EMBEDDING_MODEL", "nomic-embed-text-v1.5"
        )

        self.qwen_base_url = os.getenv("QWEN_BASE_URL", "").strip()
        self.qwen_api_key = os.getenv("QWEN_API_KEY", "").strip()
        self.qwen_chat_model = os.getenv("QWEN_CHAT_MODEL", "qwen")
        self.qwen_embedding_model = os.getenv("QWEN_EMBEDDING_MODEL", "bge-m3")

        self.mcp_url = os.getenv("MCP_URL", "http://127.0.0.1:8000/mcp")

        self.memory_turns = int(os.getenv("MEMORY_TURNS", "6"))
        self.cache_threshold = float(os.getenv("CACHE_THRESHOLD", "0.95"))
        self.rag_top_k = int(os.getenv("RAG_TOP_K", "5"))

        self.snowflake_account = os.getenv("SNOWFLAKE_ACCOUNT", "")
        self.snowflake_user = os.getenv("SNOWFLAKE_USER", "")
        self.snowflake_password = os.getenv("SNOWFLAKE_PASSWORD", "")
        self.snowflake_warehouse = os.getenv("SNOWFLAKE_WAREHOUSE", "")
        self.snowflake_database = os.getenv("SNOWFLAKE_DATABASE", "")
        self.snowflake_schema = os.getenv("SNOWFLAKE_SCHEMA", "")

        self.doc_chunks_table = os.getenv(
            "DOC_CHUNKS_TABLE", "PARTNER_DOC_CHUNKS"
        )

    @property
    def chat_model(self):
        if self.llm_provider == "qwen":
            return self.qwen_chat_model
        return self.groq_chat_model

    @property
    def embedding_model(self):
        if self.llm_provider == "qwen":
            return self.qwen_embedding_model
        return self.groq_embedding_model


settings = Settings()
