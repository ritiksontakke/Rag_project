import uuid

from qdrant_client.models import PointStruct

from src.core.config import (
    qdrant_client,
    COLLECTION_NAME,
)


def store_chunks(
    chunks,
    vectors,
    department: str,
    uploaded_by: str,
):

    points = []

    for index, (chunk, vector) in enumerate(
        zip(chunks, vectors)
    ):

        point = PointStruct(
            id=str(uuid.uuid4()),

            vector=vector,

            payload={
                "department": department,
                "uploaded_by": uploaded_by,
                "content": chunk.page_content,
                "page": chunk.metadata.get(
                    "page",
                    0,
                ),
                "chunk_index": index,
                "source": chunk.metadata.get(
                    "source"
                ),
            },
        )

        points.append(point)

    qdrant_client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
    )

    return {
        "chunks_uploaded": len(points),
        "department": department,
    }