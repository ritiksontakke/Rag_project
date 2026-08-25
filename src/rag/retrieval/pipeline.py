from src.rag.retrieval.qdrant_search import (
    search_documents,
)


RELEVANCE_THRESHOLD = 0.40


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

    print("\n========== RETRIEVAL PIPELINE ==========")
    print("QUERY:", query)
    print("DEPARTMENT:", repr(department))
    print("QDRANT RESULTS:", len(results))

    documents = []

    for result in results:
        score = result.score
        payload = result.payload or {}

        print("\n--- RESULT ---")
        print("SCORE:", score)
        print("PAYLOAD DEPARTMENT:", repr(
            payload.get("department")
        ))
        print("SOURCE:", payload.get("source"))

        if score is None or score < RELEVANCE_THRESHOLD:
            print("❌ FILTERED OUT")
            continue

        print("✅ ACCEPTED")

        documents.append(
            {
                "content": payload.get("content", ""),
                "page": payload.get("page", 0),
                "source": payload.get("source"),
                "department": payload.get("department"),
                "score": score,
            }
        )

    print("\nFINAL DOCUMENTS:", len(documents))
    print("========================================\n")

    return documents