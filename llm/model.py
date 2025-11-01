"""LLM model initialization and configuration."""
import os
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv

load_dotenv()  # optional, for local .env files

def get_model(temperature: float = 0):
    """Initialize and return the chat model."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Missing OPENAI_API_KEY environment variable.")
    
    return init_chat_model(
        "gpt-5-mini",
        model_provider="openai",
        api_key=api_key,
        temperature=temperature
    )
