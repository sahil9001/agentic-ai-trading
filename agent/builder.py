"""Agent graph builder and compilation."""

from langchain.agents import create_agent
from agent.tools import get_tools
from llm.model import get_model


def build_agent(temperature: float = 0, system_prompt: str | None = None):
    """Build and compile the agent using LangChain's create_agent.
    
    Args:
        temperature: Model temperature for randomness (default: 0)
        system_prompt: Optional system prompt for the agent
        
    Returns:
        Compiled LangChain agent
    """
    # Initialize model
    model = get_model(temperature=temperature)
    
    # Get tools
    tools = get_tools()
    
    # Create agent using LangChain's create_agent
    # If system_prompt is provided, it will be passed as a system message
    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt=system_prompt,
    )
    
    return agent

