from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)


def create_embeddings(texts: list[str]) -> list[list[float]]:
    return embeddings.embed_documents(texts)


def create_document_embeddings(documents):
    texts = [
        document.page_content
        for document in documents
    ]

    return embeddings.embed_documents(texts)