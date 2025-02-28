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
    
class SDLCState(TypedDict):
    current_step: Literal[
        "requirements",
        "generate_user_stories",
        "po_approval",
        "generate_code",
        "code_review",
        "completed"
    ]
    requirements: Optional[str]
    user_stories: Optional[str]
    po_feedback: Optional[str]
    generated_code: Optional[str]
    review_feedback: Optional[str]
    decision: Optional[Literal["approved", "feedback"]]