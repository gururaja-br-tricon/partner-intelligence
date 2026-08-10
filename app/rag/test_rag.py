import os
import sys

sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
)

from app.rag.chunker import chunk_partner_pdf, list_partner_pdfs
from app.rag.vector_store import (
    Chunk,
    LocalVectorStore,
    cosine_similarity,
)

DOCUMENTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "data",
    "generated",
    "documents",
)


def test_list_partner_pdfs():
    pdfs = list_partner_pdfs(DOCUMENTS_DIR)
    assert len(pdfs) == 10
    assert all(p.endswith(".pdf") for p in pdfs)


def test_chunk_partner_pdf_sections_are_extracted():
    chunks = chunk_partner_pdf(os.path.join(DOCUMENTS_DIR, "P001.pdf"))
    assert len(chunks) >= 10
    assert chunks[0]["partner_id"] == "P001"
    assert chunks[0]["heading"] == "Company Overview"
    assert len(chunks[0]["text"]) > 40


def test_chunk_partner_pdf_contains_core_capabilities():
    chunks = chunk_partner_pdf(os.path.join(DOCUMENTS_DIR, "P001.pdf"))
    headings = [c["heading"] for c in chunks]
    assert "Core Capabilities" in headings
    assert "Key Strengths" in headings


def test_cosine_similarity_identical_is_one():
    scores = cosine_similarity([1.0, 0.0], [[1.0, 0.0], [0.0, 1.0]])
    assert abs(scores[0] - 1.0) < 1e-6
    assert abs(scores[1]) < 1e-6


def test_local_vector_store_roundtrip(tmp_path):
    store_path = str(tmp_path / "chunks.json")
    store = LocalVectorStore(store_path)

    store.add_chunks(
        [
            Chunk("P001", 0, "Heading", "text one", [1.0, 0.0]),
            Chunk("P002", 0, "Heading", "text two", [0.0, 1.0]),
        ]
    )

    reloaded = LocalVectorStore(store_path)

    assert reloaded.count() == 2

    results = reloaded.search([1.0, 0.0], top_k=1)

    assert len(results) == 1
    assert results[0]["chunk"].partner_id == "P001"
