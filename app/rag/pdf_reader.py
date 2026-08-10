import pymupdf


def extract_text_from_pdf(pdf_path):
    document = pymupdf.open(pdf_path)

    pages = []

    for page in document:
        text = page.get_text()

        if text.strip():
            pages.append(text)

    document.close()

    return "\n".join(pages)
