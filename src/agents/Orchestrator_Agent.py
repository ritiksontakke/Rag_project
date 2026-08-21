from langchain.agents import create_agent
from src.utils.model import get_model
# from langchain.agents.middleware import ModelCallLimitMiddleware
from src.utils.model import getSystemPrompt
from src.agents.document_management_agent import documentmanagmentAgent
from src.agents.knowledge_agent import knowledgeAgent
from src.agents.upload_agent import uploadDocumentAgent

def orchestratorAgent():
    return create_agent(
        model=get_model(),
        tools=[documentmanagmentAgent, knowledgeAgent, uploadDocumentAgent],
        system_prompt=getSystemPrompt("multi_model_rag"),
        # middleware=[
        #     ModelCallLimitMiddleware(
        #         thread_limit= 8,
        #         run_limit=5
        #     )
        # ],
    )