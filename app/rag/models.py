from dataclasses import dataclass
from typing import Optional


@dataclass
class DocumentMetadata:
    document_id: str
    document_name: str
    document_type: str
    partner_id: Optional[str] = None
    partner_name: Optional[str] = None


@dataclass
class DocumentChunk:
    chunk_id: str
    document_id: str
    document_name: str
    document_type: str
    section: str
    content: str
    partner_id: Optional[str] = None
    partner_name: Optional[str] = None