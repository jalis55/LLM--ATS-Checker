
import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()


def get_model(
    model_name: str | None = None,
    temperature: float = 0.2,
    max_retries: int = 3,
    timeout: float = 60.0,
    max_tokens: int | None = None,
) -> ChatGroq:

    if not os.getenv("GROQ_API_KEY"):
        raise ValueError("GROQ_API_KEY is not set")

    return ChatGroq(
        model=model_name or os.getenv(
            "AI_MODEL", "openai/gpt-oss-120b"
        ),
        temperature=temperature,
        max_retries=max_retries,
        timeout=timeout,
        max_tokens=max_tokens,
    )
