"""Google Gemini LLM client using LangChain"""

import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from typing import Optional

logger = logging.getLogger(__name__)

# Global LLM instance
_llm_client: Optional[ChatGoogleGenerativeAI] = None


def get_gemini_client() -> ChatGoogleGenerativeAI:
    """
    Get or create the Gemini LLM client
    Uses connection pooling for efficiency
    """
    global _llm_client

    if _llm_client is None:
        from app.config import get_settings

        settings = get_settings()
        logger.info("Initializing Gemini LLM client")

        _llm_client = ChatGoogleGenerativeAI(
            model="gemini-pro",
            google_api_key=settings.google_api_key,
            temperature=settings.agent_temperature,
        )

    return _llm_client


async def query_llm(
    query: str,
    system_prompt: str = "",
    temperature: Optional[float] = None,
) -> str:
    """
    Query the LLM with a prompt
    Includes error handling and retries
    """
    from app.config.settings import get_settings

    settings = get_settings()
    llm = get_gemini_client()

    # Override temperature if provided
    if temperature is not None:
        llm.temperature = temperature

    try:
        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=query))

        response = await llm.ainvoke(messages)
        return response.content

    except Exception as e:
        logger.error(f"LLM query failed: {str(e)}")
        raise
