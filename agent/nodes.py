"""Node functions for the agent workflow."""

from langchain.messages import SystemMessage, ToolMessage
from agent.state import MessagesState
from agent.tools import get_tools_by_name


def create_llm_call_node(model_with_tools):
    """Create the LLM call node function.
    
    Args:
        model_with_tools: Model instance bound with tools
        
    Returns:
        Node function that can be used in the graph
    """
    def llm_call(state: MessagesState):
        """LLM decides whether to call a tool or not.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with new message and incremented LLM call count
        """
        return {
            "messages": [
                model_with_tools.invoke(
                    [
                        SystemMessage(
                            content="You are a helpful assistant tasked with performing arithmetic on a set of inputs."
                        )
                    ]
                    + state["messages"]
                )
            ],
            "llm_calls": state.get('llm_calls', 0) + 1
        }
    
    return llm_call


def create_tool_node():
    """Create the tool execution node function.
    
    Returns:
        Node function that can be used in the graph
    """
    tools_by_name = get_tools_by_name()
    
    def tool_node(state: MessagesState):
        """Performs the tool call.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with tool execution results
        """
        result = []
        for tool_call in state["messages"][-1].tool_calls:
            tool = tools_by_name[tool_call["name"]]
            observation = tool.invoke(tool_call["args"])
            result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
        return {"messages": result}
    
    return tool_node

