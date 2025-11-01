"""Edge and routing logic for the agent workflow."""

from typing import Literal
from langgraph.graph import END
from agent.state import MessagesState


def should_continue(state: MessagesState) -> Literal["tool_node", END]:
    """Decide if we should continue the loop or stop based upon whether the LLM made a tool call.
    
    Args:
        state: Current workflow state
        
    Returns:
        Either "tool_node" to continue or END to stop
    """
    messages = state["messages"]
    last_message = messages[-1]

    # If the LLM makes a tool call, then perform an action
    if last_message.tool_calls:
        return "tool_node"

    # Otherwise, we stop (reply to the user)
    return END

