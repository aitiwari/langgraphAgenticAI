from langgraph.graph import StateGraph
from src.langgraphagenticai.node.basic_chatbot_node import BasicChatbotNode
from src.langgraphagenticai.state.state import State

class GraphBuilder:
    """
    Manages the creation and setup of the StateGraph based on use cases.
    """
    def __init__(self,model):
        self.llm = model
        self.graph_builder = StateGraph(State)

    def setup_graph(self, usecase: str):
        """
        Sets up the graph for the selected use case.
        """
        if usecase == "Basic Chatbot":
            self.basic_chatbot_node = BasicChatbotNode(self.llm)
            self.graph_builder.add_node("chatbot", self.basic_chatbot_node.process)
            self.graph_builder.set_entry_point("chatbot")
            self.graph_builder.set_finish_point("chatbot")
        else:
            raise ValueError("Invalid use case selected.")
        return self.graph_builder.compile()
