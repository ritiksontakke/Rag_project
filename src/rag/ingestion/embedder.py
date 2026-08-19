from langchain_huggingface import (
    HuggingFaceEmbeddings,
)


embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5",
)


def create_embeddings(
    chunks,
):

    texts = [
        chunk.page_content
        for chunk in chunks
    ]

    vectors = embeddings.embed_documents(
        texts
    )

    return vectors