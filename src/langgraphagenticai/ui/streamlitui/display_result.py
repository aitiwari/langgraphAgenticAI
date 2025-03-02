import uuid
import streamlit as st
from langchain_core.messages import HumanMessage,AIMessage,ToolMessage
import json

from langgraph.types import interrupt, Command

from src.langgraphagenticai.ui.streamlitui.sdlcfeedback import SDLCUI
from src.langgraphagenticai.tools.customtool import APPOINTMENTS
from src.langgraphagenticai.tools.customer_support_tools import customers_database, data_protection_checks

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
        elif usecase == "Travel Planner":
            self._display_travel_planner_results()
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
        elif usecase == "Customer Support":
            
            main_col, right_col = st.columns([2, 1])
            response = graph.invoke({
                'messages': user_message
            })
            with  main_col:
                st.session_state.message_history = response['messages']
                for i in range(1, len(st.session_state.message_history) + 1):
                    this_message = st.session_state.message_history[-i]
                    if isinstance(this_message, AIMessage):
                        message_box = st.chat_message('assistant')
                    else:
                        message_box = st.chat_message('user')
                    if this_message.content:
                        message_box.markdown(this_message.content)
            # 3. State variables
            with right_col:
                st.title('customers database')
                st.write(customers_database)
                st.title('data protection checks')
                st.write(data_protection_checks) 
        elif usecase == "AI News":
            frequency = self.user_message
            with st.spinner("Fetching and summarizing news... ⏳"):
                result = graph.invoke({"messages": frequency})
                try:
                    # Read the markdown file
                    AI_NEWS_PATH = f"./AINews/{frequency.lower()}_summary.md"
                    with open(AI_NEWS_PATH, "r") as file:
                        markdown_content = file.read()

                    # Display the markdown content in Streamlit
                    st.markdown(markdown_content, unsafe_allow_html=True)
                except FileNotFoundError:
                    st.error(f"News Not Generated or File not found: {AI_NEWS_PATH}")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    
                
                with open(AI_NEWS_PATH, 'r') as f:
                    st.download_button(
                        "💾 Download Summary",
                        f.read(),
                        file_name=AI_NEWS_PATH,
                        mime="text/markdown"
                    )
                st.success(f"✅ Summary saved to {AI_NEWS_PATH}")
         
        elif usecase == "SDLC Workflow":
            initial_state = self.user_message
            # Invoke the workflow node for generating user stories
            
            if 'graph_config' not in st.session_state:
                st.session_state.graph_config = {"configurable": {"thread_id": uuid.uuid4()}}
           
            # Create a placeholder to show output or interrupts.
            output_placeholder = st.empty()
                
            ui = SDLCUI()
            col1, col2 = st.columns(2)  # Create two columns
            st.session_state.state['Final_Result'] = []
            if 'Final_Result' not in st.session_state:
                st.session_state['Final_Result'] = []
            with col1:
                st.subheader('Final Result')
                
            with col2:
                st.subheader('human in loop : __interrupt__')
            if  st.session_state.graph_stage =='initial' and 'current_step' in st.session_state.state and st.session_state.state['current_step']!='' :
                graph_stream = graph.stream(st.session_state["state"], config=st.session_state.graph_config )
                if graph_stream:
                    
                    for event in graph_stream:
                            with col1:
                                if "__interrupt__" not in event:
                                    for d in event.values():
                                        st.session_state.state["Final_Result"].append(d)
                                        if d:
                                            for key, value in d.items():
                                                with st.expander(label=key):
                                                    st.markdown(value)
                            with col2:
                                if "__interrupt__" in event:
                                    st.session_state.graph_stage = "waiting"
                                    st.rerun()
                                    break
                else:
                    st.session_state.graph_stage = "finished"
            # --- Stage 2: Display Human Input UI ---
            if st.session_state.graph_stage == "waiting":
                with col2:
                    col2_1, col2_2 = st.columns(2)
                    st.info(f"Current Steps : {st.session_state.state['current_step']}")

                    feedback = st.text_area("Feedback (enter text to reject)", key="feedback_input")
                    with col2_1:
                        if st.button("✅ Approve"):
                            st.session_state.user_decision = "approve"
                            st.session_state.graph_stage = "resumed"
                            st.rerun()
                    with col2_2:
                        if st.button("📝 Request Change"):
                            st.session_state.user_decision = feedback if feedback else "reject"
                            st.session_state.graph_stage = "resumed"
                            st.rerun()
                            
                    if st.session_state.graph_stage == "waiting":
                        st.stop()

            # --- Stage 3: Resume Graph Execution ---
            # When resuming after interrupt
            if st.session_state.graph_stage == "resumed":
                resume_state = {
                    "human_decision": st.session_state.user_decision,
                }
                for event in graph.stream(
                    st.session_state["state"],
                    config=st.session_state.thread_config
                ):
                    with col1:
                        if "__interrupt__" not in event:
                            for d in event.values():
                                st.session_state.state["Final_Result"].append(d)
                                if d:
                                    for key, value in d.items():
                                        with st.expander(label=key):
                                            st.markdown(value)
                    with col2:
                        if "__interrupt__" in event:
                            st.session_state.graph_stage = "waiting"
                            st.rerun()
                            break
                                
                        
                # Determine if the workflow has reached the finish point (fix_test_cases node reached).
                if st.session_state.state['current_step']=='completed' and any(isinstance(event, dict) and event.get("fix_test_cases") ):
                    st.session_state.graph_stage = "finished"
                    ui.render_end(state=st.session_state.state)
                else:
                    st.session_state.graph_stage = "initial"
                st.rerun()

            # --- Stage 4: Workflow Finished ---
            if st.session_state.graph_stage == "finished":
                st.write("### Workflow Complete")
                ui.render_end(state=st.session_state.state)
                if graph:
                    st.write('state graph - workflow')
                    st.image(graph.get_graph(xray=True).draw_mermaid_png())
            
            
    def _display_travel_planner_results(self):
        # Extract travel parameters from message
        CONVERSATION=[]
        CONVERSATION.append(HumanMessage(content=str(self.user_message), type="human"))
        state = {
                "messages": CONVERSATION,
            }
        print(state)
        # Invoke the graph
        response = self.graph.invoke(state)

        # Display results
        main_col, side_col = st.columns([3, 1])
        
        with main_col:
            st.subheader("✈️ Travel Itinerary")
            if type(response['messages'][1]) == AIMessage:
                self._display_itinerary_details(response['messages'][1].content)
            else:
                st.warning("No itinerary generated yet.")

        with side_col:
            st.subheader("📌 Travel Details")
            st.json({
                "📍 Source": self.user_message.get('source', ''),
                "📍 Destination": self.user_message.get('city', ''),
                "📅 Dates": f"{self.user_message.get('start_date', '')} to {self.user_message.get('end_date', '')}",
                "🎯 Interests": self.user_message.get('interests', ''),
                "🧑‍💻 User Addition Request": self.user_message.get('user_message', '')
            })

    def _display_itinerary_details(self, itinerary_content):
        """
        Displays the itinerary details in a structured format.
        """
        with st.expander("📅 Full Itinerary"):
            # Parse the itinerary content
            sections = {
                "Destination": itinerary_content
            }
            
            # Display destination and dates
            st.markdown(f"{sections['Destination']}")
           
    def _display_tool_calls(self, message):
        """
        Displays details of tool calls made during the itinerary generation.
        """
        with st.expander("⚙️ System Operations"):
            st.markdown("**🔧 Tool Execution Details**")
            st.json({
                "Tool Used": message.name,
                "Parameters": message.additional_kwargs,
                "Result": message.content
            })