import re

from langchain_core.documents import Document


def chunk_documents(documents):

    chunks = []

    for document in documents:

        text = document.page_content

        parts = re.split(
            r"(?m)(?=^\s*\d+\)\s*)",
            text,
        )

        for part in parts:

            part = part.strip()

            if not part:
                continue

            chunks.append(
                Document(
                    page_content=part,
                    metadata=document.metadata.copy(),
                )
            )

    return chunks