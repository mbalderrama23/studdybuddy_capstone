import json
from typing import Any, List
from datetime import datetime, timedelta

from agent.tools import Tool
from storage.memory import material_storage


class ListMaterialsTool(Tool):
    @property
    def action_type(self) -> str:
        return "list_materials"
    
    def get_tool_description(self) -> str:
        return """### list_materials
Lists all uploaded study materials.
Input: "list" or empty string
Output: List of materials with id, title, preview"""
    
    def run(self, input_data: Any) -> str:
        summaries = material_storage.get_summaries()
        if not summaries:
            return "No materials uploaded yet."
        result = []
        for s in summaries:
            result.append(f"- ID: {s.id}, Title: {s.title}, Words: {s.word_count}")
        return "\n".join(result)


class RetrieveMaterialTool(Tool):
    @property
    def action_type(self) -> str:
        return "retrieve_material"
    
    def get_tool_description(self) -> str:
        return """### retrieve_material
Gets the full content of materials.
Input: material_id OR "all" for all materials
Output: Full text content"""
    
    def run(self, input_data: Any) -> str:
        input_str = str(input_data).strip().lower()
        
        if input_str == "all" or input_str == "" or input_str == "none":
            materials = material_storage.get_all()
            if not materials:
                return "No materials uploaded yet."
            contents = []
            for m in materials:
                contents.append(f"=== {m.title} ===\n{m.content}")
            return "\n\n".join(contents)
        else:
            material = material_storage.get(input_str)
            if material:
                return f"=== {material.title} ===\n{material.content}"
            return f"Material '{input_str}' not found."


class SearchMaterialTool(Tool):
    @property
    def action_type(self) -> str:
        return "search_material"
    
    def get_tool_description(self) -> str:
        return """### search_material
Searches for keywords in materials.
Input: search query string
Output: Matching snippets"""
    
    def run(self, input_data: Any) -> str:
        query = str(input_data).strip()
        if not query:
            return "No search query provided."
        
        results = material_storage.search(query)
        if not results:
            return f"No results for '{query}'."
        
        output = []
        for r in results:
            output.append(f"From '{r['title']}':\n...{r['snippet']}...")
        return "\n\n".join(output)


class GenerateQuizTool(Tool):
    @property
    def action_type(self) -> str:
        return "generate_quiz"
    
    def get_tool_description(self) -> str:
        return """### generate_quiz
Generates quiz questions from materials.
Input: number of questions (e.g., "5") or "default"
Output: Instructions to create quiz from the material content"""
    
    def run(self, input_data: Any) -> str:
        num = 5
        try:
            num = int(str(input_data).strip())
        except:
            pass
        
        materials = material_storage.get_all()
        if not materials:
            return "No materials to create quiz from."
        
        content = "\n".join([m.content[:2000] for m in materials])
        return f"Create {num} multiple choice questions based on this content:\n{content}\n\nFormat each question with A,B,C,D options and indicate correct answer."


class GenerateStudyPlanTool(Tool):
    @property
    def action_type(self) -> str:
        return "generate_study_plan"
    
    def get_tool_description(self) -> str:
        return """### generate_study_plan
Creates a study plan.
Input: exam date (e.g., "2025-01-15") or "1 week"
Output: Structured study plan"""
    
    def run(self, input_data: Any) -> str:
        materials = material_storage.get_all()
        if not materials:
            return "No materials to create study plan from."
        
        topics = [m.title for m in materials]
        input_str = str(input_data).strip()
        
        return f"Create a study plan for these topics: {', '.join(topics)}. Target date: {input_str}. Include daily tasks and time estimates."


class GenerateCheatsheetTool(Tool):
    @property
    def action_type(self) -> str:
        return "generate_cheatsheet"
    
    def get_tool_description(self) -> str:
        return """### generate_cheatsheet
Creates a condensed cheat sheet.
Input: "summary" or specific topic
Output: Key points from materials"""
    
    def run(self, input_data: Any) -> str:
        materials = material_storage.get_all()
        if not materials:
            return "No materials to summarize."
        
        content = "\n".join([m.content[:2000] for m in materials])
        return f"Create a cheat sheet with key concepts, formulas, and important points from:\n{content}"


def get_studybuddy_tools() -> List[Tool]:
    return [
        ListMaterialsTool(),
        RetrieveMaterialTool(),
        SearchMaterialTool(),
        GenerateQuizTool(),
        GenerateStudyPlanTool(),
        GenerateCheatsheetTool(),
    ]
