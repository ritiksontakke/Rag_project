from src.rag.retrieval.pipeline import (
    retrieval_pipeline,
)

from src.rag.generation.generator import (
    generate_answer,
)


def rag_pipeline(
    query: str,
    department: str,
):

    # --------------------------------
    # 1. RETRIEVE
    # --------------------------------

    results = retrieval_pipeline(
        query=query,
        department=department,
        limit=5,
    )

    if not results:

        return {
            "answer": (
                "I could not find relevant "
                "information in your department "
                "knowledge base."
            ),
            "sources": [],
        }

    # --------------------------------
    # 2. BUILD CONTEXT
    # --------------------------------

    context_parts = []
    sources = []

    for result in results:

        content = result.get(
            "content",
            "",
        )

        context_parts.append(
            content
        )

        sources.append(
            {
                "source": result.get(
                    "source"
                ),
                "page": result.get(
                    "page"
                ),
                "score": result.get(
                    "score"
                ),
            }
        )

    context = "\n\n".join(
        context_parts
    )

    # --------------------------------
    # 3. GENERATE
    # --------------------------------

    answer = generate_answer(
        query=query,
        context=context,
    )

    return {
        "answer": answer,
        "sources": sources,
    }