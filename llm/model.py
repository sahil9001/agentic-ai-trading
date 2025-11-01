"""LLM model initialization and configuration."""
import os
from langchain_deepseek import ChatDeepSeek
from dotenv import load_dotenv

load_dotenv()  # optional, for local .env files

def get_model(temperature: float = 0):
    """Initialize and return the DeepSeek-R1 chat model.
    
    Note: DeepSeek-R1 may not support temperature parameter,
    but we keep it for compatibility with the interface.
    """
    api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Missing DEEPSEEK_API_KEY or OPENAI_API_KEY environment variable.")
    
    return ChatDeepSeek(
        model="deepseek-reasoner",
        temperature=temperature
        # other params...
    )
