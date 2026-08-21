from src.rag.retrieval.qdrant_search import (
    search_documents,
)


RELEVANCE_THRESHOLD = 0.65


def retrieval_pipeline(
    query: str,
    department: str,
    limit: int = 3,
):
    results = search_documents(
        query=query,
        department=department,
        limit=limit,
    )

    documents = []

    for result in results:
        score = result.score

        if score is None or score < RELEVANCE_THRESHOLD:
            continue

        payload = result.payload or {}

        documents.append(
            {
                "content": payload.get("content", ""),
                "page": payload.get("page", 0),
                "source": payload.get("source"),
                "department": payload.get("department"),
                "score": score,
            }
        )

    return documents