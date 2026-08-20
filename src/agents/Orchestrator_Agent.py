from langchain.agents import create_agent
from src.utils.model import get_model
from langchain.agents.middleware import ModelCallLimitMiddleware
from src.utils.model import getSystemPrompt

def orchestratorAgent():
    return create_agent(
        model=get_model(),
        tools=[],
        middleware=[
            ModelCallLimitMiddleware(
                thread_limit= 8,
                run_limit=5
            )
        ],
        system_prompt=getSystemPrompt("multi_model_rag")
    )