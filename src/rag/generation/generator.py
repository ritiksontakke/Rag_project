from src.utils.model import get_model


def generate_answer(
    query: str,
    documents: list,
):

    context = "\n\n".join(
        document["content"]
        for document in documents
        if document.get("content")
    )

    prompt = f"""
You are a company knowledge assistant.

Answer the user's question using ONLY
the provided context.

If the answer is not present in the
context, say that the information is
not available in the company documents.

Context:

{context}

Question:

{query}

Answer:
"""

    model = get_model()

    response = model.invoke(prompt)

    return response.content