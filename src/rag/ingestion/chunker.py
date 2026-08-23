import re

from langchain_core.documents import Document


def chunk_documents(
    documents,
    chunk_size=1200,
    chunk_overlap=200,
):
    chunks = []

    for document in documents:

        text = document.page_content.strip()

        if not text:
            continue

        # First split by numbered sections/headings.
        sections = re.split(
            r"(?m)(?=^\s*\d+(?:\.\d+)*[\.\)]\s+)",
            text,
        )

        for section in sections:

            section = section.strip()

            if not section:
                continue

            # If section is already small, keep it together.
            if len(section) <= chunk_size:

                chunks.append(
                    Document(
                        page_content=section,
                        metadata=document.metadata.copy(),
                    )
                )

                continue

            # Split large sections into overlapping chunks.
            start = 0

            while start < len(section):

                end = start + chunk_size

                chunk_text = section[start:end].strip()

                if chunk_text:

                    chunks.append(
                        Document(
                            page_content=chunk_text,
                            metadata=document.metadata.copy(),
                        )
                    )

                next_start = end - chunk_overlap

                if next_start <= start:
                    break

                start = next_start

    return chunks