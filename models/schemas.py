from typing import List, Optional
from pydantic import BaseModel
from enum import Enum
from datetime import datetime


class MaterialType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    PPTX = "pptx"
    TXT = "txt"
    MARKDOWN = "md"
    UNKNOWN = "unknown"


class ResponseType(str, Enum):
    ANSWER = "answer"
    QUIZ = "quiz"
    STUDY_PLAN = "study_plan"
    CHEATSHEET = "cheatsheet"
    ERROR = "error"


class Action(BaseModel):
    action_type: str
    input: str = ""


class Observation(BaseModel):
    result: str


class ThoughtStep(BaseModel):
    thought: str = ""
    action_type: str = ""
    observation: str = ""


class AgentResponse(BaseModel):
    thought_process: List[ThoughtStep] = []
    final_answer: str


class Material(BaseModel):
    id: str
    title: str
    type: MaterialType
    content: str
    created_at: str = ""
    metadata_info: str = ""


class MaterialSummary(BaseModel):
    id: str
    title: str
    type: MaterialType
    created_at: str
    content_preview: str
    word_count: int


class UploadResponse(BaseModel):
    material_id: str
    title: str
    type: MaterialType
    word_count: int
    message: str


class MaterialsListResponse(BaseModel):
    materials: List[MaterialSummary]
    total_count: int


class ChatRequest(BaseModel):
    message: str
    material_ids: List[str] = []


class ChatResponse(BaseModel):
    type: ResponseType
    final_answer: str
    payload: str = ""
