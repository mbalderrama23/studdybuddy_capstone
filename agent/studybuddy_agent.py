from typing import Optional, List, Dict
import json
import re

from agent.react_agent import ReactAgent
from tools.studybuddy_tools import get_studybuddy_tools
from models.schemas import AgentResponse, ResponseType


STUDYBUDDY_SYSTEM_PROMPT = """You are StudyBuddy, an intelligent AI study assistant.

Your capabilities:
1. Q&A: Answer questions based on uploaded study materials
2. Study Plans: Create structured study schedules
3. Cheat Sheets: Summarize key concepts
4. Quizzes: Generate practice questions

Guidelines:
- Use list_materials to see available content
- Use search_material or retrieve_material to get content
- Use generate_study_plan, generate_cheatsheet, or generate_quiz as needed
- Always base answers on the uploaded materials
- Be helpful and encouraging"""


class StudyBuddyAgent:
    def __init__(self, debug: bool = False):
        self.debug = debug
        tools = get_studybuddy_tools()
        self.agent = ReactAgent(
            tools=tools,
            custom_system_prompt=STUDYBUDDY_SYSTEM_PROMPT,
            max_iterations=15
        )
    
    def run(self, message: str, material_ids: Optional[List[str]] = None) -> Dict:
        augmented_message = message
        if material_ids:
            augmented_message = f"{message}\n\n[Focus on materials: {', '.join(material_ids)}]"
        
        response: AgentResponse = self.agent.run(augmented_message, debug=self.debug)
        
        response_type = self._detect_type(message)
        
        return {
            "type": response_type.value,
            "final_answer": response.final_answer,
            "payload": ""
        }
    
    def _detect_type(self, message: str) -> ResponseType:
        message_lower = message.lower()
        if any(word in message_lower for word in ["quiz", "test me", "question"]):
            return ResponseType.QUIZ
        elif any(word in message_lower for word in ["study plan", "schedule", "exam"]):
            return ResponseType.STUDY_PLAN
        elif any(word in message_lower for word in ["cheat sheet", "summary", "key points"]):
            return ResponseType.CHEATSHEET
        return ResponseType.ANSWER


_agent_instance: Optional[StudyBuddyAgent] = None


def get_agent(debug: bool = False) -> StudyBuddyAgent:
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = StudyBuddyAgent(debug=debug)
    return _agent_instance


def reset_agent():
    global _agent_instance
    _agent_instance = None
