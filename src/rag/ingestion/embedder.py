from langchain_huggingface import HuggingFaceEmbeddings


_embeddings = None


def get_embeddings():
    global _embeddings

    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-en-v1.5",
            model_kwargs={
                "device": "cpu",
            },
            encode_kwargs={
                "normalize_embeddings": True,
            },
        )

    return _embeddings


def create_embeddings(texts: list[str]) -> list[list[float]]:
    return get_embeddings().embed_documents(texts)


def create_document_embeddings(documents):
    texts = [
        document.page_content
        for document in documents
    ]

    return get_embeddings().embed_documents(texts)