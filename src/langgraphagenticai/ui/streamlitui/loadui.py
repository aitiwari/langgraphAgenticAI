import streamlit as st
import os

from src.langgraphagenticai.ui.configfile import Config


class LoadStreamlitUI:
    def __init__(self):
        self.config =  Config() # config
        self.user_controls = {}

    def load_streamlit_ui(self):
        st.set_page_config(page_title= "🤖 " + self.config.get_page_title(), layout="wide")
        st.header("🤖 " + self.config.get_page_title())

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
                
            
            # Use case selection
            self.user_controls["selected_usecase"] = st.selectbox("Select Usecases", usecase_options)
            
            if self.user_controls["selected_usecase"] =="Chatbot with Tool":
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
            # TODO :: to be removed
            st.warning("⌛Revamp is in progress...")

        return self.user_controls
