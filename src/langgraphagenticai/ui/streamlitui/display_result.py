import streamlit as st
from langchain_core.messages import HumanMessage,AIMessage,ToolMessage

from src.langgraphagenticai.tools.customtool import APPOINTMENTS

class DisplayResultStreamlit:
    def __init__(self,usecase,graph,user_message):
        self.usecase= usecase
        self.graph = graph
        self.user_message = user_message
    
    
    def display_result_on_ui(self):
        usecase= self.usecase
        graph = self.graph
        user_message = self.user_message
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
        elif usecase == "Appointment Receptionist":
            CONVERSATION=[]
            CONVERSATION.append(HumanMessage(content=user_message, type="human"))
            state = {
                "messages": CONVERSATION,
            }
            print(state)
            new_state = graph.invoke(state)
            CONVERSATION.extend(new_state["messages"][len(CONVERSATION):])
            col1, col2 = st.columns(2)
            with col1:
                for message in CONVERSATION:
                    if message and message.content:
                        if type(message) == HumanMessage:
                            with st.chat_message("user"):
                                st.write(message.content)
                        else:
                            with st.chat_message("assistant"):
                                st.write(message.content)
                            
            with col2:
                st.header("Appointments")
                st.write(APPOINTMENTS)
        # display graph
        if graph:
            st.write('state graph - workflow')
            st.image(graph.get_graph(xray=True).draw_mermaid_png())