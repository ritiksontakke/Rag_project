from src.core.config import (
    qdrant_client,
    COLLECTION_NAME,
)

from src.rag.ingestion.embedder import (
    create_embeddings,
)


def search_documents(
    query: str,
    department: str,
    limit: int = 10,
):

    query_vector = create_embeddings(
        [query]
    )[0]
    department = department.strip().lower()
    

    results = qdrant_client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        query_filter={
            "must": [
                {
                    "key": "department",
                    "match": {
                        "value": department,
                    },
                }
            ]
        },
        limit=limit,
        with_payload=True,
    )


    for result in results.points:

        payload = result.payload or {}

        print(
            "SCORE:",
            result.score,
            "| PAGE:",
            payload.get("page"),
            "| CONTENT:",
            str(payload.get("content", ""))[:200],
        )

    return results.points