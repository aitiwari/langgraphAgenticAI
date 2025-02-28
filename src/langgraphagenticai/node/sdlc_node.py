import streamlit as st

class SDLCNode:
    def __init__(self, llm):
        self.llm = llm

    def generate_user_stories(self, state: dict) -> dict:
        prompt = f"""
        Generate comprehensive user stories based on the following requirements:
        {state['requirements']}
        
        {f"PO Feedback to incorporate: {state['po_feedback']}" if state.get('po_feedback') else ""}
        
        Format the user stories in Markdown with clear acceptance criteria.
        """
        
        response = self.llm.invoke(prompt)
        
        st.session_state.state["user_stories"] = response.content
        st.session_state.state["current_step"] = "po_approval"
        return {"user_stories": response.content, "current_step": "po_approval"}

    def po_approval(self, state: dict) -> dict:
        return {"current_step": "po_approval"}

    def generate_code(self, state: dict) -> dict:
        prompt = f"""
        Generate production-quality code based on these user stories:
        {state['user_stories']}
        
        {f"Review Feedback to incorporate: {state['review_feedback']}" if state.get('review_feedback') else ""}
        
        Include proper error handling, comments, and follow best practices.
        """
        
        response = self.llm.invoke(prompt)
        st.session_state.state["generated_code"] = response.content 
        return {"generated_code": response.content, "current_step": "code_review"}