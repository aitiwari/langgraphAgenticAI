from langgraph.graph import StateGraph, END, MessagesState
from langgraph.prebuilt import tools_condition,ToolNode
from langchain_core.prompts import ChatPromptTemplate
import datetime
from langgraph.types import interrupt, Command
from langgraph.checkpoint.memory import MemorySaver
import streamlit as st
#module import

from src.langgraphagenticai.node.sdlc_node import SDLCNode
from src.langgraphagenticai.node.ai_news_node import AINewsNode
from src.langgraphagenticai.node import travel_planner_node
from src.langgraphagenticai.node.customer_support_chatbot import Customer_Support_Bot
from src.langgraphagenticai.tools.customtool import book_appointment, cancel_appointment, get_next_available_appointment
from src.langgraphagenticai.tools.search_tool import create_tool_node, get_tools
from src.langgraphagenticai.node.chatbot_with_tool_node import ChatbotWithToolNode
from src.langgraphagenticai.node.basic_chatbot_node import BasicChatbotNode
from src.langgraphagenticai.state.state import State , SDLCState
from src.langgraphagenticai.node.travel_planner_node import TravelPlannerNode

class GraphBuilder:
    """
    Manages the creation and setup of the StateGraph based on use cases.
    """
    def __init__(self,model):
        self.llm = model
        self.graph_builder = StateGraph(State)
        self.sdlc_graph_builder = StateGraph(SDLCState)
        
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
    
    
    def sdlc_workflow_build_graph(self):
        sdlc_wf_node = SDLCNode(self.llm)
        self.graph_builder = self.sdlc_graph_builder
        try:

            # Add all primary workflow nodes.
            nodes = [
                ("generate_user_stories", sdlc_wf_node.generate_user_stories),
                ("product_owner_review", sdlc_wf_node.product_owner_review),
                ("create_design_docs", sdlc_wf_node.create_design_docs),
                ("revise_user_stories", sdlc_wf_node.revise_user_stories),
                ("design_review", sdlc_wf_node.design_review),
                ("generate_code", sdlc_wf_node.generate_code),
                ("code_review", sdlc_wf_node.code_review),
                ("security_review", sdlc_wf_node.security_review),
                ("fix_code_after_code_review", sdlc_wf_node.fix_code_after_code_review),
                ("fix_code_after_security", sdlc_wf_node.fix_code_after_security),
                ("write_test_cases", sdlc_wf_node.write_test_cases),
                ("test_cases_review", sdlc_wf_node.test_cases_review),
                ("fix_test_cases", sdlc_wf_node.fix_test_cases),
            ]

            # Helper functions to wrap review nodes.
            def human_loop_node(review_field):
                def node(state):
                    # Trigger an interrupt to surface the LLM-generated review.
                    if st.session_state.user_decision is not  "approve":
                        value = interrupt({
                            "__interrupt__": True,
                            "review": state.get(review_field, ""),
                            "instruction": f"Please review the '{review_field}'. Approve or provide feedback to reject."
                        })
                    else :
                        value = st.session_state.user_decision
                        st.session_state.user_decision = ''
                    return {"human_decision": value}
                return node

            def decision_node(previous_node):
                def node(state):
                    if state.get("human_decision") == "approve":
                        state["decision"] = "approve"
                    else:
                        state["decision"] = "reject"
                        state["feedback"] = state.get("human_decision")
                    return state
                return node

            review_nodes = ["product_owner_review", "design_review", "code_review", "test_cases_review"]
            additional_nodes = []
            for review in review_nodes:
                additional_nodes.append((f"human_loop_{review}", human_loop_node(review)))
                # Set the previous node for rejection (adjust as needed):
                if review == "product_owner_review":
                    prev = "generate_user_stories"
                elif review == "design_review":
                    prev = "revise_user_stories"
                elif review == "code_review":
                    prev = "generate_code"
                elif review == "test_cases_review":
                    prev = "write_test_cases"
                additional_nodes.append((f"decision_{review}", decision_node(prev)))

            # Add all nodes to the graph.
            for node_name, node_func in nodes + additional_nodes:
                self.graph_builder.add_node(node_name, node_func)

            # Set entry point.
            if st.session_state.graph_stage == 'resumed':
                self.graph_builder.set_entry_point(st.session_state.state['current_step'])
            else:   
                self.graph_builder.set_entry_point("generate_user_stories")

            # ---- Build Flow Edges ----

            # Wrap product_owner_review:
            self.graph_builder.add_edge("generate_user_stories", "product_owner_review")
            self.graph_builder.add_edge("product_owner_review", "human_loop_product_owner_review")
            self.graph_builder.add_edge("human_loop_product_owner_review", "decision_product_owner_review")
            self.graph_builder.add_conditional_edges(
                "decision_product_owner_review",
                lambda state: "approve" if state.get("decision") == "approve" else "reject",
                {
                    "approve": "create_design_docs",
                    "reject": "generate_user_stories"
                }
            )

            # Wrap design_review:
            self.graph_builder.add_edge("revise_user_stories", "design_review")
            self.graph_builder.add_edge("design_review", "human_loop_design_review")
            self.graph_builder.add_edge("human_loop_design_review", "decision_design_review")
            self.graph_builder.add_conditional_edges(
                "decision_design_review",
                lambda state: "approve" if state.get("decision") == "approve" else "reject",
                {
                    "approve": "generate_code",
                    "reject": "revise_user_stories"
                }
            )

            # Wrap code_review:
            self.graph_builder.add_edge("generate_code", "code_review")
            self.graph_builder.add_edge("code_review", "human_loop_code_review")
            self.graph_builder.add_edge("human_loop_code_review", "decision_code_review")
            self.graph_builder.add_conditional_edges(
                "decision_code_review",
                lambda state: "approve" if state.get("decision") == "approve" else "reject",
                {
                    "approve": "security_review",
                    "reject": "generate_code"
                }
            )

            # Wrap test_cases_review:
            self.graph_builder.add_edge("write_test_cases", "test_cases_review")
            self.graph_builder.add_edge("test_cases_review", "human_loop_test_cases_review")
            self.graph_builder.add_edge("human_loop_test_cases_review", "decision_test_cases_review")
            self.graph_builder.add_conditional_edges(
                "decision_test_cases_review",
                lambda state: "approve" if state.get("decision") == "approve" else "reject",
                {
                    "approve": "fix_test_cases",
                    "reject": "write_test_cases"
                }
            )

            # Other sequential edges.
            self.graph_builder.add_edge("create_design_docs", "revise_user_stories")
            self.graph_builder.add_edge("security_review", "fix_code_after_code_review")
            self.graph_builder.add_edge("fix_code_after_code_review", "fix_code_after_security")
            self.graph_builder.add_edge("fix_code_after_security", "write_test_cases")

            # Set finish point at the end of the workflow.
            self.graph_builder.set_finish_point("fix_test_cases")
        except Exception as e:
            print(e)

        self.graph_builder


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
        elif usecase =="SDLC Workflow":
            checkpointer = MemorySaver()
            self.sdlc_workflow_build_graph()
            return self.graph_builder.compile(checkpointer=checkpointer)
        else:
            raise ValueError("Invalid use case selected.")
        return self.graph_builder.compile()
