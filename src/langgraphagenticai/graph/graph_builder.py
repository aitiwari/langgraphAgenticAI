from langgraph.graph import StateGraph
from langgraph.prebuilt import tools_condition

from src.langgraphagenticai.tools.search_tool import create_tool_node, get_tools
from src.langgraphagenticai.node.chatbot_with_tool_node import ChatbotWithToolNode
from src.langgraphagenticai.node.basic_chatbot_node import BasicChatbotNode
from src.langgraphagenticai.state.state import State

class GraphBuilder:
    """
    Manages the creation and setup of the StateGraph based on use cases.
    """
    def __init__(self,model):
        self.llm = model
        self.graph_builder = StateGraph(State)
        
    def basic_chatbot_build_graph(self):
        """
        Builds a basic chatbot graph using LangGraph.

        This method initializes a chatbot node using the `BasicChatbotNode` class 
        and integrates it into the graph. The chatbot node is set as both the 
        entry and exit point of the graph.
        """
        self.basic_chatbot_node = BasicChatbotNode(self.llm)
        self.graph_builder.add_node("chatbot", self.basic_chatbot_node.process)
        self.graph_builder.set_entry_point("chatbot")
        self.graph_builder.set_finish_point("chatbot")

    def chatbot_with_tool_build_graph(self):
        """
        Builds an advanced chatbot graph with tool integration.

        This method creates a chatbot graph that includes both a chatbot node 
        and a tool node. It defines tools, initializes the chatbot with tool 
        capabilities, and sets up conditional and direct edges between nodes. 
        The chatbot node is set as the entry point.
        """
        # Define tools and tool node
        tools = get_tools()
        tool_node = create_tool_node(tools)

        # Define LLM
        llm = self.llm

        # Define chatbot node
        obj_chatbot_with_node = ChatbotWithToolNode(llm)
        chatbot_node = obj_chatbot_with_node.create_chatbot(tools)

        # Add nodes
        self.graph_builder.add_node("chatbot", chatbot_node)
        self.graph_builder.add_node("tools", tool_node)

        # Define conditional and direct edges
        self.graph_builder.add_conditional_edges("chatbot", tools_condition)
        self.graph_builder.add_edge("tools", "chatbot")

        # Set entry point and compile graph
        self.graph_builder.set_entry_point("chatbot")


    def setup_graph(self, usecase: str):
        """
        Sets up the graph for the selected use case.
        """
        if usecase == "Basic Chatbot":
            self.basic_chatbot_build_graph()
        elif usecase == "Chatbot with Tool":
            self.chatbot_with_tool_build_graph()
        else:
            raise ValueError("Invalid use case selected.")
        return self.graph_builder.compile()
