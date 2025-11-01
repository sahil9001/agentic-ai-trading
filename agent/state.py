"""State definition for the agent workflow."""

from langchain.messages import AnyMessage
from typing_extensions import TypedDict, Annotated
import operator


class MessagesState(TypedDict):
    """State schema for the agent workflow.
    
    Attributes:
        messages: List of messages in the conversation
        llm_calls: Number of LLM calls made during execution
    """
    messages: Annotated[list[AnyMessage], operator.add]
    llm_calls: int

