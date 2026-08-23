from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import os
from langfuse import Langfuse
from langfuse.langchain import CallbackHandler
from openai import OpenAI

load_dotenv()
langfuse = Langfuse()
langfuse_handler = CallbackHandler()

def get_openai_model():
    return ChatOpenAI(
        model="gpt-5.4-nano",
        api_key=os.getenv("OPENAI_API_KEY"),
        streaming=True,
    )

def get_model():
    return get_openai_model()

def get_tavily_api_key():
    return os.getenv("TAVILY_API_KEY")
# Get production prompt
# prompt = langfuse.get_prompt("multi_model_rag")

# # Get by label
# # You can use as many labels as you'd like to identify different deployment targets
# prompt = langfuse.get_prompt("multi_model_rag", label="production")
# prompt = langfuse.get_prompt("multi_model_rag", label="latest")

# # Get by version number, usually not recommended as it requires code changes to deploy new prompt versions
# langfuse.get_prompt("multi_model_rag", version=1)




def getSystemPrompt(prompt_name: str = "multi_model_rag"):
    try:
        prompt = langfuse.get_prompt(
            prompt_name,
            label="production"  # or "latest"
        )

        # Depending on Langfuse version
        return prompt.prompt

    except Exception as e:
        print(f"Failed to load prompt: {e}")

        return """
        You are an Orchestrator Agent.
        Route tasks to the correct sub-agent.
        Never hallucinate.
        """

def getdocsubagent(prompt_name: str = "ducument_sub_agent"):
    try:
        prompt = langfuse.get_prompt(
            prompt_name,
            label="production"  # or "latest"
        )

        # Depending on Langfuse version
        return prompt.prompt

    except Exception as e:
        print(f"Failed to load prompt: {e}")

        return """
        You are an document subAgent.
        Route tasks to the correct sub-agent.
        Never hallucinate.
        """

def getKnowledsubagent(prompt_name: str = "KnowledgeAgent"):
    try:
        prompt = langfuse.get_prompt(
            prompt_name,
            label="production"  # or "latest"
        )

        # Depending on Langfuse version
        return prompt.prompt

    except Exception as e:
        print(f"Failed to load prompt: {e}")

        return """
        You are an  KnowledgeAgent.
        Route tasks to the correct sub-agent.
        Never hallucinate.
        """

def getuploadsubagent(prompt_name: str = "UploadDocumentAgent"):
    try:
        prompt = langfuse.get_prompt(
            prompt_name,
            label="production"  # or "latest"
        )

        # Depending on Langfuse version
        return prompt.prompt

    except Exception as e:
        print(f"Failed to load prompt: {e}")

        return """
        You are an  KnowledgeAgent.
        Route tasks to the correct sub-agent.
        Never hallucinate.
        """