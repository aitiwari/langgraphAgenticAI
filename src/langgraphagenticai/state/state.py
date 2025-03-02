from typing import Annotated, Literal, Optional
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from typing import TypedDict, Annotated, List
from langchain_core.messages import HumanMessage, AIMessage

class State(TypedDict):
    """
    Represents the structure of the state used in the graph.
    """
    messages: Annotated[list, add_messages]
    
    
class PlannerState(TypedDict):
    messages: Annotated[List[HumanMessage | AIMessage], "Conversation history"]
    city: str
    interests: List[str]
    itinerary: str
    start_date: str 
    end_date: str    
    
# class SDLCState(TypedDict):
#     current_step: Literal[
#         "requirements",
#         "generate_user_stories",
#         "po_approval",
#         "generate_code",
#         "code_review",
#         "completed"
#     ]
#     requirements: Optional[str]
#     user_stories: Optional[str]
#     po_feedback: Optional[str]
#     generated_code: Optional[str]
#     review_feedback: Optional[str]
#     decision: Optional[Literal["approved", "feedback"]]
    
# from typing import TypedDict, Optional, Literal

class SDLCState(TypedDict):
    current_step: Literal[
        "requirements",
        "generate_user_stories",
        "product_owner_review",
        "create_design_docs",
        "design_review",
        "generate_code",
        "code_review",
        "fix_code_after_code_review",
        "security_review",
        "fix_code_after_security",
        "write_test_cases",
        "test_cases_review",
        "fix_test_cases",
        "end"
    ]
    decision: Optional[Literal["approved", "feedback"]]
    # Content fields
    requirements: Optional[str]
    user_stories: Optional[str]
    design_docs: Optional[str]
    generated_code: Optional[str]
    test_cases: Optional[str]
    # Feedback fields
    po_feedback: Optional[str]          # Product Owner feedback
    design_feedback: Optional[str]      # Design Review feedback
    code_feedback: Optional[str]        # Code Review feedback
    security_feedback: Optional[str]    # Security Review feedback
    test_case_feedback: Optional[str]   # Test Case Review feedback
    # For human input during interrupts.
    human_decision: Optional[str]