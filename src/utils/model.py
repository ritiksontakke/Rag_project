from langchain_openai import ChatOpenAI


def get_model():

    return ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
    )