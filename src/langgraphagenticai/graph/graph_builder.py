from langgraph.graph import StateGraph, END, MessagesState
from langgraph.prebuilt import tools_condition,ToolNode
from langchain_core.prompts import ChatPromptTemplate
import datetime
#module import
from src.langgraphagenticai.node.ai_news_node import AINewsNode
from src.langgraphagenticai.node import travel_planner_node
from src.langgraphagenticai.node.customer_support_chatbot import Customer_Support_Bot
from src.langgraphagenticai.tools.customtool import book_appointment, cancel_appointment, get_next_available_appointment
from src.langgraphagenticai.tools.search_tool import create_tool_node, get_tools
from src.langgraphagenticai.node.chatbot_with_tool_node import ChatbotWithToolNode
from src.langgraphagenticai.node.basic_chatbot_node import BasicChatbotNode
from src.langgraphagenticai.state.state import State
from src.langgraphagenticai.node.travel_planner_node import TravelPlannerNode

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
    
    def travel_planner_build_graph(self):
        """
            Builds a standalone travel planning graph with itinerary generation.
        """
        # Initialize the Travel Planner node
        travel_planner_node = TravelPlannerNode(self.llm)

        # Add the Travel Planner node to the graph
        self.graph_builder.add_node("travel_planner", travel_planner_node.process)

        # Set the entry point to the Travel Planner node
        self.graph_builder.set_entry_point("travel_planner")

        # Define the edge to end the graph after the Travel Planner completes
        self.graph_builder.add_edge("travel_planner", END)
    
    # Helper methods -  START       
    # Nodes
    def call_caller_model(self,state: MessagesState):
        state["current_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        response = self.caller_model.invoke(state)
        return {"messages": [response]}
    
     # Edges
    def should_continue_caller(self,state: MessagesState):
        messages = state["messages"]
        last_message = messages[-1]
        if not last_message.tool_calls:
            return "end"
        else:
            return "continue"
        
    
    # Helper method - END     
    def appointment_receptionist_bot_build_graph(self):
        caller_tools = [book_appointment, get_next_available_appointment, cancel_appointment]
        tool_node = ToolNode(caller_tools)

        caller_pa_prompt = """You are a personal assistant, and need to help the user to book or cancel appointments, you should check the available appointments before booking anything. Be extremely polite, so much so that it is almost rude.
        Current time: {current_time}
        """

        caller_chat_template = ChatPromptTemplate.from_messages([
            ("system", caller_pa_prompt),
            ("placeholder", "{messages}"),
        ])

        self.caller_model = caller_chat_template | self.llm.bind_tools(caller_tools)

        # Add Nodes
        self.graph_builder.add_node("agent", self.call_caller_model)
        self.graph_builder.add_node("action", tool_node)

        # Add Edges
        self.graph_builder.add_conditional_edges(
            "agent",
            self.should_continue_caller,
            {
                "continue": "action",
                "end": END,
            },
        )
        self.graph_builder.add_edge("action", "agent")

        # Set Entry Point and build the graph
        self.graph_builder.set_entry_point("agent")

    def customer_support_build_graph(self):
        obj_cs_bot = Customer_Support_Bot(llm=self.llm)
        self.graph_builder = obj_cs_bot.chat_bot()
        
    def ai_news_build_graph(self):
        # Initialize the AINewsNode
        ai_news_node = AINewsNode(self.llm)

        self.graph_builder.add_node("fetch_news", ai_news_node.fetch_news)
        self.graph_builder.add_node("summarize_news", ai_news_node.summarize_news)
        self.graph_builder.add_node("save_result", ai_news_node.save_result)

        self.graph_builder.set_entry_point("fetch_news")
        self.graph_builder.add_edge("fetch_news", "summarize_news")
        self.graph_builder.add_edge("summarize_news", "save_result")
        self.graph_builder.add_edge("save_result", END)

    def setup_graph(self, usecase: str):
        """
        Sets up the graph for the selected use case.
        """
        if usecase == "Basic Chatbot":
            self.basic_chatbot_build_graph()
        elif usecase == "Chatbot with Tool":
            self.chatbot_with_tool_build_graph()
        elif usecase == "Travel Planner":
            self.travel_planner_build_graph()
        elif usecase == "Appointment Receptionist":
            self.appointment_receptionist_bot_build_graph()
        elif usecase =="Customer Support":
            self.customer_support_build_graph()
        elif usecase =="AI News":
            self.ai_news_build_graph()
        else:
            raise ValueError("Invalid use case selected.")
        return self.graph_builder.compile()
