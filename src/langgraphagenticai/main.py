from src.langgraphagenticai.LLMS.groqllm import GroqLLM
from src.langgraphagenticai.graph.graph_builder import GraphBuilder
from src.langgraphagenticai.ui.streamlitui.loadui import LoadStreamlitUI

import streamlit as st
from langchain_core.messages import HumanMessage,AIMessage,ToolMessage


# MAIN Function START
def load_langgraph_agenticai_app():
    
    # load ui
    ui = LoadStreamlitUI()
    user_input = ui.load_streamlit_ui()

    # Text input for user message
    user_message = st.chat_input("Enter your message:")
    if user_message:
        # Configure LLM
        obj_llm_config = GroqLLM(user_controls_input=user_input)
        model = obj_llm_config.get_llm_model()

        # Initialize and set up the graph based on use case
        usecase = user_input['selected_usecase']
        graph_builder = GraphBuilder(model)
        graph = graph_builder.setup_graph(usecase)
        
        # Display output in UI
        if usecase =="Basic Chatbot":
            for event in graph.stream({'messages':("user",user_message)}):
                print(event.values())
                for value in event.values():
                    print(value['messages'])
                    with st.chat_message("user"):
                        st.write(user_message)
                    with st.chat_message("assistant"):
                        st.write(value["messages"].content)
        elif usecase =="Chatbot with Tool":
            # Prepare state and invoke the graph
            initial_state = {"messages": [user_message]}
            res = graph.invoke(initial_state)
            for message in res['messages']:
                if type(message) == HumanMessage:
                    with st.chat_message("user"):
                        st.write(message.content)
                elif type(message)==ToolMessage:
                    with st.chat_message("ai"):
                        st.write("Tool Call Start")
                        st.write(message.content)
                        st.write("Tool Call End")
                elif type(message)==AIMessage and message.content:
                    with st.chat_message("assistant"):
                        st.write(message.content)
        
        # display graph
        if graph:
            st.write('state graph - workflow')
            st.image(graph.get_graph(xray=True).draw_mermaid_png())
                        
       
                
                        
                    
                


            

        
                
                
                