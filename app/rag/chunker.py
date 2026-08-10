from app.rag.models import DocumentChunk

SECTION_NAMES = [
    "Company Overview",
    "Business Focus",
    "Industries Served",
    "Geographic Presence",
    "Core Capabilities",
    "Technology Expertise",
    "Services Offered",
    "Partner Ecosystem",
    "Certifications & Expertise",
    "Typical Customer Profile",
    "Key Strengths",
    "Differentiators",
    "Recent Initiatives",
    "Strategic Focus",
    "Summary",
]


def chunk_document(text, metadata):
    chunks = []

    current_section = None
    current_content = []

    lines = text.splitlines()

    for line in lines:
        line = line.strip()

        if not line:
            continue

        if line in SECTION_NAMES:
            if current_section and current_content:
                chunks.append(
                    DocumentChunk(
                        chunk_id=f"{metadata.document_id}-{len(chunks)}",
                        document_id=metadata.document_id,
                        document_name=metadata.document_name,
                        document_type=metadata.document_type,
                        section=current_section,
                        content=" ".join(current_content),
                        partner_id=metadata.partner_id,
                        partner_name=metadata.partner_name,
                    )
                )

            current_section = line
            current_content = []

        elif current_section:
            current_content.append(line)

    if current_section and current_content:
        chunks.append(
            DocumentChunk(
                chunk_id=f"{metadata.document_id}-{len(chunks)}",
                document_id=metadata.document_id,
                document_name=metadata.document_name,
                document_type=metadata.document_type,
                section=current_section,
                content=" ".join(current_content),
                partner_id=metadata.partner_id,
                partner_name=metadata.partner_name,
            )
        )

    return chunks
