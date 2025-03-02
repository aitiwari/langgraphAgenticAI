# sdlc_node.py
import streamlit as st
import logging
from typing import Dict, Any

from src.langgraphagenticai.ui.streamlitui.sdlcfeedback import SDLCUI

# Configure logging for production (adjust level and handlers as necessary)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SDLCNode:
    def __init__(self, llm):
        self.llm = llm
        self.logger = logging.getLogger(self.__class__.__name__)

    def _update_state(self, updates: Dict[str, Any]) -> None:
        """
        Safely update st.session_state['state'] with provided updates.
        """
        try:
            if 'state' not in st.session_state:
                st.session_state['state'] = {}
            st.session_state['state'].update(updates)
        except Exception as e:
            self.logger.exception("Failed to update session state.")
            st.error(f"Error updating session state: {e}")

    def refresh_ui(self):
        try:
            ui = SDLCUI()
            ui.render()
        except Exception as e:
            self.logger.exception("Error refreshing UI.")
            st.error(f"UI Refresh failed: {e}")

    def generate_user_stories(self, state: Dict[str, Any]) -> Dict[str, Any]:
        if st.session_state.state['user_stories'] is not '':
            return {"user_stories": st.session_state.state['user_stories']}
        try:
            prompt = f"""
                Generate comprehensive user stories based on these requirements:
                {state.get('requirements', 'No requirements provided')}

                {f"PO Feedback to incorporate: {state.get('po_feedback', '')}" if state.get('po_feedback') else ""}
                
                Format as Markdown with clear acceptance criteria.
            """
            response = self.llm.invoke(prompt)
            content = getattr(response, 'content', None)
            if content is None:
                raise ValueError("LLM response does not contain content.")
            self._update_state({
                "user_stories": content,
                "current_result": content,
                "current_step": "product_owner_review"
            })
            return {"user_stories": content}
        except Exception as e:
            self.logger.exception("Error in generate_user_stories.")
            st.error(f"Failed to generate user stories: {e}")
            return {"error": str(e)}

    def product_owner_review(self, state: Dict[str, Any]) -> Dict[str, Any]:
        if st.session_state.state['po_feedback'] is not '':
            return {"po_feedback": st.session_state.state['po_feedback']}
        
        try:
            prompt = f"""
                Please review the following user stories and provide your feedback.
                
                User Stories:
                {state.get('user_stories', 'No user stories available')}
                
                If you approve, simply type "approve". Otherwise, provide detailed feedback.
            """
            response = self.llm.invoke(prompt)
            content = getattr(response, 'content', None)
            if content is None:
                raise ValueError("LLM response does not contain content.")
            self._update_state({
                "po_feedback": content,
                "current_result": content,
                "current_step": "create_design_docs"  # Updated to next node
            })
            st.session_state.user_decision = None
            return {"po_feedback": content}
        except Exception as e:
            self.logger.exception("Error in product_owner_review.")
            st.error(f"Product owner review failed: {e}")
            return {"error": str(e)}

    def create_design_docs(self, state: Dict[str, Any]) -> Dict[str, Any]:
        if st.session_state.state['design_docs'] is not '':
            return {"design_docs": st.session_state.state['design_docs']}
        try:
            prompt = f"""
                Create comprehensive design documents for the following user stories:
                {state.get('user_stories', 'No user stories available')}
                
                Include both functional and technical specifications.
                Provide architecture diagrams in Mermaid format.
            """
            response = self.llm.invoke(prompt)
            content = getattr(response, 'content', None)
            if content is None:
                raise ValueError("LLM response does not contain content.")
            self._update_state({
                "design_docs": content,
                "current_result": content,
                "current_step": "revise_user_stories"  # Updated to next node
            })
            return {"design_docs": content}
        except Exception as e:
            self.logger.exception("Error in create_design_docs.")
            st.error(f"Failed to create design documents: {e}")
            return {"error": str(e)}

    def revise_user_stories(self, state: Dict[str, Any]) -> Dict[str, Any]:
        if st.session_state.state['user_stories'] is not '':
            return {"user_stories": st.session_state.state['user_stories']}
        try:
            prompt = f"""
                Revise the user stories based on the following Product Owner feedback:
                
                Original Stories: {state.get('user_stories', 'No stories generated')}
                Feedback: {state.get('po_feedback', 'No feedback provided')}
                
                Please maintain Markdown format and include clear acceptance criteria.
            """
            response = self.llm.invoke(prompt)
            content = getattr(response, 'content', None)
            if content is None:
                raise ValueError("LLM response does not contain content.")
            self._update_state({
                "user_stories": content,
                "current_result": content,
                "current_step": "design_review"  # Updated to next node
            })
            return {"user_stories": content}
        except Exception as e:
            self.logger.exception("Error in revise_user_stories.")
            st.error(f"Failed to revise user stories: {e}")
            return {"error": str(e)}

    def design_review(self, state: Dict[str, Any]) -> Dict[str, Any]:
        if st.session_state.state['design_feedback'] is not '':
            return {"design_feedback": st.session_state.state['design_feedback']}
        try:
            prompt = f"""
                Please review the following design documents and provide your feedback.
                
                Design Documents:
                {state.get('design_docs', 'No design documents available')}
                
                If you approve, type "approve". Otherwise, provide detailed design feedback.
            """
            response = self.llm.invoke(prompt)
            content = getattr(response, 'content', None)
            if content is None:
                raise ValueError("LLM response does not contain content.")
            self._update_state({
                "design_feedback": content,
                "current_result": content,
                "current_step": "generate_code"  # Updated to next node
            })
            st.session_state.user_decision = None
            return {"design_feedback": content}
        except Exception as e:
            self.logger.exception("Error in design_review.")
            st.error(f"Design review failed: {e}")
            return {"error": str(e)}

    def generate_code(self, state: Dict[str, Any]) -> Dict[str, Any]:
        if st.session_state.state['generate_code'] is not '':
            return {"generate_code": st.session_state.state['generate_code']}
            
        try:
            prompt = f"""
                Generate production-quality code for the following design:
                {state.get('design_docs', 'No design documents available')}
                
                {f"Code Review Feedback: {state.get('review_feedback', '')}" if state.get('review_feedback') else ""}
                
                Include error handling, clear comments, and follow best coding practices.
            """
            response = self.llm.invoke(prompt)
            content = getattr(response, 'content', None)
            if content is None:
                raise ValueError("LLM response does not contain content.")
            self._update_state({
                "generate_code": content,
                "current_result": content,
                "current_step": "code_review"  # Updated to next node
            })
            return {"generate_code": content}
        except Exception as e:
            self.logger.exception("Error in generate_code.")
            st.error(f"Failed to generate code: {e}")
            return {"error": str(e)}

    def code_review(self, state: Dict[str, Any]) -> Dict[str, Any]:
        if st.session_state.state['review_feedback'] is not '':
            return {"review_feedback": st.session_state.state['review_feedback']}
        try:
            prompt = f"""
                Please review the following generated code and provide your feedback.
                
                Code:
                {state.get('generated_code', 'No code generated')}
                
                If the code is acceptable, type "approve". Otherwise, provide specific code review feedback.
            """
            response = self.llm.invoke(prompt)
            content = getattr(response, 'content', None)
            if content is None:
                raise ValueError("LLM response does not contain content.")
            self._update_state({
                "code_review": content,
                "current_result": content,
                "current_step": "security_review"  # Updated to next node
            })
            st.session_state.user_decision = None
            return {"review_feedback": content}
        except Exception as e:
            self.logger.exception("Error in code_review.")
            st.error(f"Code review failed: {e}")
            return {"error": str(e)}

    def security_review(self, state: Dict[str, Any]) -> Dict[str, Any]:
        if st.session_state.state['security_feedback'] is not '':
            return {"security_feedback": st.session_state.state['security_feedback']}
        try:
            prompt = f"""
                Please review the following code for potential security vulnerabilities:
                
                Code:
                {state.get('generated_code', 'No code available')}
                
                Provide any security-related feedback.
            """
            response = self.llm.invoke(prompt)
            content = getattr(response, 'content', None)
            if content is None:
                raise ValueError("LLM response does not contain content.")
            self._update_state({
                "security_feedback": content,
                "current_result": content,
                "current_step": "fix_code_after_code_review"  # Updated to next node
            })
            st.session_state.user_decision = None
            return {"security_feedback": content, "current_step": "fix_code_after_code_review"}
        except Exception as e:
            self.logger.exception("Error in security_review.")
            st.error(f"Security review failed: {e}")
            return {"error": str(e)}

    def fix_code_after_code_review(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            prompt = f"""
                Fix the following code based on the code review feedback provided.
                
                Original Code: {state.get('generated_code', 'No code available')}
                Feedback: {state.get('review_feedback', 'No feedback provided')}
                
                Ensure that functionality is preserved while addressing all feedback.
            """
            response = self.llm.invoke(prompt)
            content = getattr(response, 'content', None)
            if content is None:
                raise ValueError("LLM response does not contain content.")
            self._update_state({
                "generated_code": content,
                "current_result": content,
                "current_step": "fix_code_after_security"  # Updated to next node
            })
            st.session_state.user_decision = None
            return {"generated_code": content}
        except Exception as e:
            self.logger.exception("Error in fix_code_after_code_review.")
            st.error(f"Failed to fix code after review: {e}")
            return {"error": str(e)}

    def fix_code_after_security(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            prompt = f"""
                Improve the security of the following code based on the security review feedback:
                
                Code: {state.get('generated_code', 'No code available')}
                Security Feedback: {state.get('security_feedback', 'No security feedback provided')}
                
                Apply best practices for security and fix any vulnerabilities.
            """
            response = self.llm.invoke(prompt)
            content = getattr(response, 'content', None)
            if content is None:
                raise ValueError("LLM response does not contain content.")
            self._update_state({
                "generated_code": content,
                "current_result": content,
                "current_step": "write_test_cases"  # Updated to next node
            })
            return {"generated_code": content}
        except Exception as e:
            self.logger.exception("Error in fix_code_after_security.")
            st.error(f"Failed to fix code for security: {e}")
            return {"error": str(e)}

    def write_test_cases(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            prompt = f"""
                Create  test cases for the following code in brief :
                {state.get('generated_code', 'No code available')}
                
                Include positive, negative, edge, and security test cases.
                Format the tests as a Markdown table with test steps and expected results.
            """
            response = self.llm.invoke(prompt)
            content = getattr(response, 'content', None)
            if content is None:
                raise ValueError("LLM response does not contain content.")
            self._update_state({
                "test_cases": content,
                "current_result": content,
                "current_step": "test_cases_review"  # Updated to next node
            })
            return {"test_cases": content}
        except Exception as e:
            self.logger.exception("Error in write_test_cases.")
            st.error(f"Failed to write test cases: {e}")
            return {"error": str(e)}

    def test_cases_review(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            prompt = f"""
                Please review the following test cases and provide your feedback.
                
                Test Cases:
                {state.get('test_cases', 'No test cases generated')}
                
                If the test cases are acceptable, type "approve". Otherwise, provide detailed feedback.
            """
            response = self.llm.invoke(prompt)
            content = getattr(response, 'content', None)
            if content is None:
                raise ValueError("LLM response does not contain content.")
            self._update_state({
                "test_feedback": content,
                "current_step": "fix_test_cases"  # Updated to next node
            })
            # st.session_state.user_decision = None
            return {"test_feedback": content}
        except Exception as e:
            self.logger.exception("Error in test_cases_review.")
            # st.error(f"Test cases review failed: {e}")
            return {"error": str(e)}
        
    def decision_test_cases_review(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            prompt = f"""
                Based on the following test cases and the review feedback, please decide whether the test cases are acceptable or if further modifications are required.
                
                Test Cases:
                {state.get('test_cases', 'No test cases available')}
                
                Review Feedback:
                {state.get('test_feedback', 'No feedback provided')}
                
                If the test cases are acceptable, output "approved". Otherwise, provide the modifications required.
            """
            response = self.llm.invoke(prompt)
            content = getattr(response, 'content', None)
            if content is None:
                raise ValueError("LLM response does not contain content.")
            self._update_state({
                "decision_test_cases": content,
                "current_result": content,
                "current_step": "fix_test_cases"  # or update to the next step in your flow if needed
            })
            return {"decision_test_cases": content}
        except Exception as e:
            self.logger.exception("Error in decision_test_cases_review.")
            st.error(f"Decision on test cases review failed: {e}")
            return {"error": str(e)}


    def fix_test_cases(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            prompt = f"""
                Improve the test cases based on the following feedback:
                
                Original Test Cases: {state.get('test_cases', 'No test cases available')}
                Feedback: {state.get('test_feedback', 'No feedback provided')}
                
                Ensure that all feedback points are addressed and that the Markdown table format is maintained.
            """
            response = self.llm.invoke(prompt)
            content = getattr(response, 'content', None)
            if content is None:
                raise ValueError("LLM response does not contain content.")
            self._update_state({
                "test_cases": content,
                "current_step": "completed"  # Final step
            })
            return {"test_cases": content}
        except Exception as e:
            self.logger.exception("Error in fix_test_cases.")
            # st.error(f"Failed to fix test cases: {e}")
            return {"error": str(e)}
