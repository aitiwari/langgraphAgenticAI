from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import ToolNode

def get_tools():
    """
    Returns a list of tools to be used in the chatbot.
    """
    tool = TavilySearchResults( max_results=2)
    return [tool]

def create_tool_node(tools):
    """
    Creates and returns a tool node for the graph.
    """
    return ToolNode(tools=tools)
