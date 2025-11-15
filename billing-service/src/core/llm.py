from llm_platform_client import LLMClient

llm = LLMClient("http://llm-gateway:9000")


async def ask_llm(question: str):
    return await llm.chat(question)
