import streamlit as st
import os
from datetime import date

from src.langgraphagenticai.ui.uiconfigfile import Config
from langchain_core.messages import AIMessage, HumanMessage


class LoadStreamlitUI:
    def __init__(self):
        self.config =  Config() # config
        self.user_controls = {}


    def load_streamlit_ui(self):
        st.set_page_config(page_title= "🤖 " + self.config.get_page_title(), layout="wide")
        st.header("🤖 " + self.config.get_page_title())
        st.session_state.timeframe = ''
        st.session_state.IsFetchButtonClicked = False
        
        

        with st.sidebar:
            # Get options from config
            llm_options = self.config.get_llm_options()
            usecase_options = self.config.get_usecase_options()

            # LLM selection
            self.user_controls["selected_llm"] = st.selectbox("Select LLM", llm_options)

            if self.user_controls["selected_llm"] == 'Groq':
                # Model selection
                model_options = self.config.get_groq_model_options()
                self.user_controls["selected_groq_model"] = st.selectbox("Select Model", model_options)
                # API key input
                self.user_controls["GROQ_API_KEY"] = st.session_state["GROQ_API_KEY"] = st.text_input("API Key",
                                                                                                      type="password")
                # Validate API key
                if not self.user_controls["GROQ_API_KEY"]:
                    st.warning("⚠️ Please enter your GROQ API key to proceed.")
                   
            
            # Use case selection
            self.user_controls["selected_usecase"] = st.selectbox("Select Usecases", usecase_options)
            
            if self.user_controls["selected_usecase"] =="Chatbot with Tool" or self.user_controls["selected_usecase"] =="AI News" :
            # API key input
                os.environ["TAVILY_API_KEY"] = self.user_controls["TAVILY_API_KEY"] = st.session_state["TAVILY_API_KEY"] = st.text_input("TAVILY API KEY",
                                                                                                      type="password")
                
        if self.user_controls['selected_usecase'] == "Appointment Receptionist":
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Appointment Manager")
            with col2:
                st.subheader("Appointments")
                    
        elif self.user_controls['selected_usecase']=="Customer Support":
            st.subheader('Flower Shop Chatbot' + '💐')
            greeting="Hi 🙋🏻‍♀️, I am the flower shop chatbot. How can I help?"

            if 'message_history' not in st.session_state:
                st.session_state.message_history = [AIMessage(content=greeting)]
                
            with st.chat_message("assistant"):
                st.write(greeting) 
                
             # 1. Buttons for chat - Clear Button
            
        

            with  st.sidebar:
                if st.button('Clear Chat'):
                    st.session_state.message_history = []

        elif self.user_controls['selected_usecase']=="Travel Planner":
            st.subheader("✈️ AI Travel Planner")
            col1, col2 = st.columns(2)

            with col1:
                source = st.text_input("📍 Source", value="London", help="Enter your travel source")
                destination = st.text_input("📍 Destination", value="Goa", help="Enter your travel destination")
                preferences = st.text_area(
                    "🎯 Travel Preferences",
                    placeholder="E.g., I prefer beach destinations, luxury stays, and adventure activities.",
                    help="Describe your travel preferences"
                )

            with col2:
                start_date = st.date_input("📅 Start Date", value=date.today(), help="Select your travel start date")
                end_date = st.date_input("📅 End Date", value=date.today(), help="Select your travel end date")

            if destination and preferences and start_date and end_date:
                self.user_controls.update({
                "source": source,
                "destination": destination,
                "preferences": preferences,
                "start_date": start_date,
                "end_date": end_date,
            })
          
        elif self.user_controls['selected_usecase']=="AI News":
            st.subheader("📰 AI News Explorer ")
            
            with st.sidebar:
                time_frame = st.selectbox(
                    "📅 Select Time Frame",
                    ["Daily", "Weekly", "Monthly"],
                    index=0
                )
            
            if st.button("🔍 Fetch Latest AI News", use_container_width=True):
                st.session_state.IsFetchButtonClicked = True
                st.session_state.timeframe = time_frame
            else :
                st.session_state.IsFetchButtonClicked = False
                    
        return self.user_controls
