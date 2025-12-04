from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # ⭐ REQUIRED for Lovable Frontend

from models.schemas import (
    UploadResponse,
    MaterialsListResponse,
    ChatRequest,
    ChatResponse,
    ResponseType,
)
from storage.memory import material_storage
from services.material_service import process_and_store_file, process_and_store_text
from agent.studybuddy_agent import get_agent, reset_agent


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("=" * 40)
    print("StudyBuddy is ready!")
    print("=" * 40)
    yield
    print("Shutting down...")


app = FastAPI(title="StudyBuddy API", version="1.0.0", lifespan=lifespan)

# ⭐ CORS — REQUIRED for frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # you can restrict this later to your lovable domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------------------------------------
# ROOT CHECK
# ----------------------------------------------------
@app.get("/")
async def root():
    return {"message": "StudyBuddy API", "status": "running"}


# ----------------------------------------------------
# UPLOAD FILE
# ----------------------------------------------------
@app.post("/upload/file", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    title: str = Form(None)
):
    """Upload a file (PDF, DOCX, PPTX, TXT)"""
    file_bytes = await file.read()

    material_id, material = process_and_store_file(
        filename=file.filename,
        file_bytes=file_bytes,
        content_type=file.content_type,
        custom_title=title
    )

    return UploadResponse(
        material_id=material_id,
        title=material.title,
        type=material.type,
        word_count=len(material.content.split()),
        message=f"Uploaded '{material.title}'"
    )


# ----------------------------------------------------
# UPLOAD TEXT
# ----------------------------------------------------
@app.post("/upload/text", response_model=UploadResponse)
async def upload_text(
    text: str = Form(...),
    title: str = Form("Untitled")
):
    """Upload text directly"""
    material_id, material = process_and_store_text(text=text, title=title)

    return UploadResponse(
        material_id=material_id,
        title=material.title,
        type=material.type,
        word_count=len(material.content.split()),
        message=f"Uploaded '{material.title}'"
    )


# ----------------------------------------------------
# LIST MATERIALS
# ----------------------------------------------------
@app.get("/materials", response_model=MaterialsListResponse)
async def list_materials():
    summaries = material_storage.get_summaries()
    return MaterialsListResponse(materials=summaries, total_count=len(summaries))


# ----------------------------------------------------
# GET SINGLE MATERIAL
# ----------------------------------------------------
@app.get("/materials/{material_id}")
async def get_material(material_id: str):
    material = material_storage.get(material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Not found")

    return {
        "id": material.id,
        "title": material.title,
        "type": material.type.value,
        "content": material.content
    }


# ----------------------------------------------------
# CLEAR MATERIALS (Reset storage + agent)
# ----------------------------------------------------
@app.delete("/materials")
async def clear_materials():
    material_storage.clear()
    reset_agent()
    return {"message": "Cleared"}


# ----------------------------------------------------
# CHAT WITH AGENT
# ----------------------------------------------------
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        agent = get_agent()
        result = agent.run(message=request.message, material_ids=request.material_ids)

        return ChatResponse(
            type=ResponseType(result["type"]),
            final_answer=result["final_answer"],
            payload=result.get("payload", "")
        )

    except Exception as e:
        return ChatResponse(
            type=ResponseType.ERROR,
            final_answer=f"Error: {str(e)}",
            payload=""
        )


# ----------------------------------------------------
# ALIAS ROUTES FOR LOVABLE FRONTEND
# ----------------------------------------------------

# Lovable frontend: POST /materials/upload → our /upload/file
@app.post("/materials/upload")
async def alias_upload_file(file: UploadFile = File(...), title: str = Form(None)):
    return await upload_file(file=file, title=title)


# Lovable frontend: POST /materials/upload-text → our /upload/text
@app.post("/materials/upload-text")
async def alias_upload_text(text: str = Form(...), title: str = Form("Untitled")):
    return await upload_text(text=text, title=title)


# Lovable frontend: GET /materials/list → our /materials
@app.get("/materials/list")
async def alias_list_materials():
    return await list_materials()


# ----------------------------------------------------
# UVICORN ENTRYPOINT (for local use)
# ----------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

