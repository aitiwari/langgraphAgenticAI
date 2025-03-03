# sdlc_feedback.py
import streamlit as st

class SDLCUI:
    def render(self):
        if "state" not in st.session_state:
            st.session_state.state = {"current_step": "user_input"}
        state = st.session_state.state

        st.markdown(f"**Current Step:** {state['current_step'].replace('_', ' ').title()}")

        step_method = getattr(self, f"render_{state['current_step']}", None)
        if step_method:
            step_method(state)
        else:
            st.error(f"Unknown step: {state['current_step']}")

    def render_requirements(self, state):
        st.markdown("### Requirements Input")
        requirements = st.text_area("Enter your requirements:", height=200)
        if st.button("Submit Requirements"):
            state["requirements"] = requirements
            state["current_step"] = "generate_user_stories"
            st.session_state.state["current_step"] = "generate_user_stories"
       
            
            

    def render_generate_user_stories(self, state):
        st.markdown("### Generated User Stories")
        if st.session_state.state['user_stories']!='':
            with st.expander("View User Stories"):
                st.markdown(st.session_state.state['user_stories'])
            if st.button("Continue to Product Owner Review"):
                state["current_step"] = "product_owner_review"
                st.session_state.state["current_step"] = "product_owner_review"
            # st.rerun()

    def render_product_owner_review(self, state):
        st.markdown("### Product Owner Review")
        with st.expander("View Current User Stories"):
            st.markdown(state.get("user_stories", ""))
        st.markdown("### Review Actions")
        feedback = st.text_area("Feedback:", height=150, key='Feedback')
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚀 Approve Design Phase", key="approve_design"):
                state["decision"] = "approved"
                state["current_step"] = "create_design_docs"
                st.session_state.user_decision = "approve"
                st.session_state.graph_stage = "resumed"
                st.rerun()
        with col2:
            if st.button("🔧 Request Revisions", key="request_revisions"):
                state["decision"] = "feedback"
                state["po_feedback"] = feedback
                state["current_step"] = "revise_user_stories"
                st.rerun()

    def render_create_design_docs(self, state):
        st.markdown("### Design Documents")
        with st.expander("View Design Documents"):
            st.markdown(state.get("design_docs", ""))
        if st.button("Proceed to Design Review"):
            state["current_step"] = "design_review"
            st.rerun()

    def render_design_review(self, state):
        st.markdown("### Design Review")
        with st.expander("View Design Documents"):
            st.markdown(state.get("design_docs", ""))
        st.markdown("### Review Actions")
        feedback = st.text_area("Design Feedback:", height=150, key="design_feedback")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚀 Approve Implementation", key="approve_implementation"):
                state["decision"] = "approved"
                state["current_step"] = "generate_code"
                st.session_state.user_decision = "approve"
                st.session_state.graph_stage = "resumed"
                st.rerun()
        with col2:
            if st.button("🔧 Request Design Changes", key="request_design_changes"):
                state["decision"] = "feedback"
                state["design_feedback"] = feedback
                state["current_step"] = "create_design_docs"
                st.rerun()

    def render_generate_code(self, state):
        st.markdown("### Generated Code")
        with st.expander("View Code Implementation"):
            st.code(state.get("code", ""), language='python')
        if st.button("Proceed to Code Review"):
            state["current_step"] = "code_review"
            st.rerun()

    def render_code_review(self, state):
        st.markdown("### Code Review")
        with st.expander("View Current Code"):
            st.code(state.get("code", ""), language='python')
        st.markdown("### Review Actions")
        feedback = st.text_area("Code Feedback:", height=150, key="code_feedback")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚀 Approve for Security Review", key="approve_security"):
                state["decision"] = "approved"
                state["current_step"] = "security_review"
                st.session_state.user_decision = "approve"
                st.session_state.graph_stage = "resumed"
                st.rerun()
        with col2:
            if st.button("🔧 Request Code Fixes", key="request_code_fixes"):
                state["decision"] = "feedback"
                state["review_feedback"] = feedback
                state["current_step"] = "fix_code_after_code_review"
                st.rerun()

    def render_security_review(self, state):
        st.markdown("### Security Review")
        with st.expander("View Code for Security Audit"):
            st.code(state.get("code", ""), language='python')
        st.markdown("### Security Findings")
        feedback = st.text_area("Security Feedback:", height=150, key="security_feedback")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚀 Approve for Testing", key="approve_testing"):
                state["decision"] = "approved"
                state["current_step"] = "write_test_cases"
                st.session_state.user_decision = "approve"
                st.session_state.graph_stage = "resumed"
                st.rerun()
        with col2:
            if st.button("🔧 Request Security Fixes", key="request_security_fixes"):
                state["decision"] = "feedback"
                state["security_feedback"] = feedback
                state["current_step"] = "fix_code_after_security"
                st.rerun()

    def render_write_test_cases(self, state):
        st.markdown("### Test Cases")
        with st.expander("View Test Cases"):
            st.markdown(state.get("test_cases", ""))
        if st.button("Proceed to Test Review"):
            state["current_step"] = "test_cases_review"
            st.rerun()

    def render_test_cases_review(self, state):
        st.markdown("### Test Cases Review")
        with st.expander("View Current Test Cases"):
            st.markdown(state.get("test_cases", ""))
        st.markdown("### Review Actions")
        feedback = st.text_area("Test Feedback:", height=150, key="test_feedback")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚀 Final Approval", key="final_approve"):
                state["decision"] = "approved"
                state["current_step"] = "end"
                st.rerun()
        with col2:
            if st.button("🔧 Improve Test Cases", key="request_test_fixes"):
                state["decision"] = "feedback"
                state["test_feedback"] = feedback
                state["current_step"] = "fix_test_cases"
                st.rerun()

    def render_end(self, state):
        st.success("✅ SDLC Process Completed Successfully!")
        with st.expander("Requirements"):
            st.write(state.get("requirements", ""))
        with st.expander("User Stories"):
            st.write(state.get("user_stories", ""))
        with st.expander("Design Documents"):
            st.write(state.get("design_docs", ""))
        with st.expander("Design Feedback"):
            st.write(state.get("design_feedback", ""))
        with st.expander("Generated Code"):
            st.write(state.get("generate_code", ""))
        with st.expander("Test Cases"):
            st.write(state.get("test_cases", ""))
        with st.expander("PO Feedback"):
            st.write(state.get("po_feedback", ""))
        with st.expander("Review Feedback"):
            st.write(state.get("review_feedback", ""))
        with st.expander("Security Feedback"):
            st.write(state.get("security_feedback", ""))
        with st.expander("Test Feedback"):
            st.write(state.get("test_feedback", ""))
                
            
            
        with st.expander("Final Artifacts", expanded=True):
            st.markdown("### Download Assets")
            st.download_button("📥 Requirements", 
                            data=state.get("requirements", ""), 
                            file_name="requirements.md")
            st.download_button("📥 User Stories", 
                            data=state.get("user_stories", ""), 
                            file_name="user_stories.md")
            st.download_button("📥 Design Documents", 
                            data=state.get("design_docs", ""), 
                            file_name="design_docs.md")
            st.download_button("📥 Generated Code", 
                            data=state.get("code", ""), 
                            file_name="generated_code.md")
            st.download_button("📥 Test Cases", 
                            data=state.get("test_cases", ""), 
                            file_name="test_cases.md")
            st.download_button("📥 Product Owner Feedback", 
                            data=state.get("po_feedback", ""), 
                            file_name="po_feedback.md")
            st.download_button("📥 Design Feedback", 
                            data=state.get("design_feedback", ""), 
                            file_name="design_feedback.md")
            st.download_button("📥 Code Review Feedback", 
                            data=state.get("review_feedback", ""), 
                            file_name="code_review_feedback.md")
            st.download_button("📥 Security Feedback", 
                            data=state.get("security_feedback", ""), 
                            file_name="security_feedback.md")
            st.download_button("📥 Test Cases Feedback", 
                            data=state.get("test_feedback", ""), 
                            file_name="test_feedback.md")

                
        if st.button("🔄 Restart Process"):
            st.session_state.clear()
            st.rerun()
