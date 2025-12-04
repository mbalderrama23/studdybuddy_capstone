from typing import Any, List
from datetime import datetime, timedelta

from agent.tools import Tool

# ⭐ USE SQLITE INSTEAD OF MEMORY
from storage.db import material_db
from services.material_service import (
    get_material_content,
    get_all_materials_content,
)


class ListMaterialsTool(Tool):
    @property
    def action_type(self) -> str:
        return "list_materials"
    
    def get_tool_description(self) -> str:
        return """### list_materials
Lists all uploaded study materials.
Input: empty string
Output: List of materials with id, title, word_count
"""
    
    def run(self, input_data: Any) -> str:
        rows = material_db.list()
        if not rows:
            return "No materials uploaded yet."

        result = []
        for r in rows:
            result.append(f"- ID: {r.id}, Title: {r.title}, Words: {len(r.content.split())}")

        return "\n".join(result)


class RetrieveMaterialTool(Tool):
    @property
    def action_type(self) -> str:
        return "retrieve_material"
    
    def get_tool_description(self) -> str:
        return """### retrieve_material
Gets the full content of materials.
Input: material_id OR "all"
Output: Full text content
"""
    
    def run(self, input_data: Any) -> str:
        input_str = str(input_data).strip()

        if input_str.lower() in ("all", "", "none"):
            return get_all_materials_content()

        content = get_material_content(input_str)
        if content:
            return content
        
        return f"Material '{input_str}' not found."


class SearchMaterialTool(Tool):
    @property
    def action_type(self) -> str:
        return "search_material"
    
    def get_tool_description(self) -> str:
        return """### search_material
Searches for keywords in uploaded materials.
Input: search query
Output: matching text snippets
"""
    
    def run(self, input_data: Any) -> str:
        query = str(input_data).strip().lower()
        if not query:
            return "Search query is empty."

        rows = material_db.list()
        if not rows:
            return "No materials uploaded yet."

        results = []
        for r in rows:
            text = r.content.lower()
            idx = text.find(query)
            if idx != -1:
                start = max(0, idx - 80)
                end = min(len(r.content), idx + 80)
                snippet = r.content[start:end].replace("\n", " ")
                results.append(f"From {r.title}:\n...{snippet}...")

        if not results:
            return f"No results for '{query}'."

        return "\n\n".join(results)


class GenerateQuizTool(Tool):
    @property
    def action_type(self) -> str:
        return "generate_quiz"
    
    def get_tool_description(self) -> str:
        return """### generate_quiz
Generates quiz questions from the materials.
Input: number of questions or empty
"""
    
    def run(self, input_data: Any) -> str:
        try:
            num = int(str(input_data).strip())
        except:
            num = 5

        content = get_all_materials_content()
        return f"Create {num} multiple choice questions from this material:\n\n{content}"


class GenerateStudyPlanTool(Tool):
    @property
    def action_type(self) -> str:
        return "generate_study_plan"
    
    def get_tool_description(self) -> str:
        return """### generate_study_plan
Creates a study plan based on all uploaded materials.
Input: exam date or duration (e.g., '1 week')
"""
    
    def run(self, input_data: Any) -> str:
        rows = material_db.list()
        if not rows:
            return "No materials uploaded yet."

        topics = [r.title for r in rows]
        target = str(input_data).strip()

        return (
            f"Create a detailed study plan for: {', '.join(topics)}.\n"
            f"Exam date or timeframe: {target}.\n"
            "Break it down into daily tasks with time estimates."
        )


class GenerateCheatsheetTool(Tool):
    @property
    def action_type(self) -> str:
        return "generate_cheatsheet"
    
    def get_tool_description(self) -> str:
        return """### generate_cheatsheet
Creates a condensed cheat sheet from all materials.
"""
    
    def run(self, input_data: Any) -> str:
        content = get_all_materials_content()
        return f"Create a condensed cheat sheet summarizing key points from:\n\n{content}"


def get_studybuddy_tools() -> List[Tool]:
    return [
        ListMaterialsTool(),
        RetrieveMaterialTool(),
        SearchMaterialTool(),
        GenerateQuizTool(),
        GenerateStudyPlanTool(),
        GenerateCheatsheetTool(),
    ]

