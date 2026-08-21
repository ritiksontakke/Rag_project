import os
from huggingface_hub import InferenceClient

client = InferenceClient(
    provider="hf-inference",
    api_key=os.environ["HF_TOKEN"],
)

MODEL = "BAAI/bge-small-en-v1.5"


def create_embeddings(texts: list[str]) -> list[list[float]]:
    result = client.feature_extraction(
        texts,
        model=MODEL,
    )

    return result.tolist()