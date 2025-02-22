from typing import Dict
from langchain_core.prompts import ChatPromptTemplate
from src.langgraphagenticai.state.state import State
from langchain_core.messages import HumanMessage, AIMessage
import json

class TravelPlannerNode:
    """
    Travel Planner logic implementation.
    """
    def __init__(self, model):
        self.llm = model
        self.itinerary_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a creative and detail-oriented travel assistant. Create a visually appealing and highly detailed travel itinerary from {source} to {city} for the user. "
               "The itinerary should be based on the user's interests: {interests} and their additional request: {user_message}. "
               "The trip will take place from {start_date} to {end_date}. "
               "**Follow these guidelines to create the itinerary:**\n"
               "1. **Structure:** Organize the itinerary into clear sections with subheadings for each day (e.g., 'Day 1: Arrival and Exploration').\n"
               "2. **Activities:** Include a mix of activities (e.g., sightseeing, dining, adventure, relaxation) tailored to the user's interests.\n"
               "3. **Flights and Accommodations:** Provide flight options (if applicable) and recommend accommodations with actual links to their location on Google Maps.\n"
               "4. **Cost Estimation:** Add approximate costs for activities, flights, and accommodations.\n"
               "5. **Emojis:** Use relevant emojis (e.g., ✈️ for flights, 🏨 for hotels, 🍽️ for dining) to make the itinerary visually engaging.\n"
               "6. **Markdown Formatting:** Use bullet points, bold text, and subheadings for clarity and readability.\n"
               "7. **Links:** Include clickable links for booking flights, accommodations, and activity reservations where applicable.\n"
               "8. **No Introductory Explanation:** Jump straight into the itinerary without unnecessary introductions.\n"
               "**Example Format:**\n"
               "### Day 1: Arrival in {city} ✈️\n"
               "- **Morning:** Arrive at {city} Airport. Transfer to your hotel 🏨. [Hotel Map Link](https://maps.google.com)\n"
               "- **Afternoon:** Explore landmark and enjoy lunch at restaurant 🍽️. (Cost: ~ 50)\n"
               "- **Evening:** Relax at location and enjoy dinner at restaurant 🍷. (Cost: ~ 70)\n"
               "### Day 2: Adventure and Sightseeing 🌄\n"
               "- **Morning:** Visit attraction and enjoy activity. (Cost: ~ 30)\n"
               "- **Afternoon:** Lunch at restaurant 🍽️. (Cost: ~ 40)\n"
               "- **Evening:** Explore location and enjoy a guided tour. (Cost: ~ 60)\n"
               "Ensure the itinerary is engaging, practical, and tailored to the user's preferences and cost should be in local currency"),
    ("human", "Create an itinerary for my trip"),
])
    def process(self, state: State) -> Dict:
        """
        Processes the input state and generates a travel itinerary.
        """
        # Validate required fields
        content_str = state.get("messages")[0].content.replace("'", '"')
        content = json.loads(content_str)

        # Validate required fields
        if not content.get("city") or not content.get("interests") or not content.get("start_date") or not content.get("end_date"):
            return {
                "messages": [AIMessage(content="Please provide a city, interests, start date, and end date to generate an itinerary.")],
                "itinerary": ""
            }

        # Generate the itinerary using the LLM
        response = self.llm.invoke(self.itinerary_prompt.format_messages(
            source=content["source"],
            user_message = content["user_message"],
            city=content["city"],
            interests=content["interests"],  # No need to join, as it's already a string
            start_date=content["start_date"],
            end_date=content["end_date"]
        ))

        # Update the state with the generated itinerary
        return {
            "messages": state.get("messages", []) + [AIMessage(content=response.content)],  # Safely access "messages"
            "itinerary": AIMessage(content=response.content),
            "city": content["city"],
            "interests": content["interests"],
            "start_date": content["start_date"],
            "end_date": content["end_date"]
        }