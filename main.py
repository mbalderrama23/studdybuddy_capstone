from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models.schemas import (
    ChatRequest,
    ChatResponse,
    ResponseType,
)
from services.material_service import process_and_store_file, process_and_store_text
from agent.studybuddy_agent import get_agent, reset_agent

# ⭐ NEW: SQLite repository instead of in-memory storage
from storage.db import material_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("=" * 40)
    print("StudyBuddy is ready (SQLite Enabled)!")
    print("=" * 40)
    yield
    print("Shutting down...")


app = FastAPI(title="StudyBuddy API", version="2.0.0", lifespan=lifespan)


# ----------------------------------------------------
# CORS
# ----------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "StudyBuddy API", "status": "running"}


# ----------------------------------------------------
# UPLOAD FILE
# ----------------------------------------------------
@app.post("/upload/file")
async def upload_file(
    file: UploadFile = File(...),
    title: str = Form(None)
):
    file_bytes = await file.read()

    material_id, material = process_and_store_file(
        filename=file.filename,
        file_bytes=file_bytes,
        content_type=file.content_type,
        custom_title=title
    )

    # ⭐ Save to DATABASE (not memory)
    material_db.save(material)

    return {
        "ok": True,
        "id": material_id,
        "title": material.title,
        "chunks": len(material.content.split()),
        "message": f"Uploaded '{material.title}'"
    }


# ----------------------------------------------------
# UPLOAD TEXT
# ----------------------------------------------------
@app.post("/upload/text")
async def upload_text(
    text: str = Form(...),
    title: str = Form("Untitled")
):
    material_id, material = process_and_store_text(text=text, title=title)

    # ⭐ Save to DATABASE
    material_db.save(material)

    return {
        "ok": True,
        "id": material_id,
        "title": material.title,
        "chunks": len(material.content.split()),
        "message": f"Uploaded '{material.title}'"
    }


# ----------------------------------------------------
# LIST MATERIALS (SQLite)
# ----------------------------------------------------
@app.get("/materials")
async def list_materials():
    rows = material_db.list()

    frontend_list = [
        {
            "id": r.id,
            "title": r.title,
            "type": r.type,
            "word_count": len(r.content.split()),
            "content_preview": r.content[:200]
        }
        for r in rows
    ]

    return {
        "ok": True,
        "materials": frontend_list,
        "total_count": len(frontend_list)
    }


# ----------------------------------------------------
# GET ONE MATERIAL
# ----------------------------------------------------
@app.get("/materials/{material_id}")
async def get_material(material_id: str):
    material = material_db.get(material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Not found")

    return {
        "id": material.id,
        "title": material.title,
        "type": material.type,
        "content": material.content,
    }


# ----------------------------------------------------
# CLEAR MATERIALS (DATABASE)
# ----------------------------------------------------
@app.delete("/materials")
async def clear_materials():
    material_db.clear()
    reset_agent()
    return {"ok": True, "message": "Cleared"}


# ----------------------------------------------------
# CHAT
# ----------------------------------------------------
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        agent = get_agent()
        result = agent.run(
            message=request.message,
            material_ids=request.material_ids
        )

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
# LOVABLE COMPATIBILITY ROUTES
# ----------------------------------------------------
@app.post("/materials/upload")
async def alias_upload_file(file: UploadFile = File(...), title: str = Form(None)):
    return await upload_file(file=file, title=title)


@app.post("/materials/upload-text")
async def alias_upload_text(text: str = Form(...), title: str = Form("Untitled")):
    return await upload_text(text=text, title=title)


@app.get("/materials/list")
async def alias_list_materials():
    return await list_materials()


# ----------------------------------------------------
# LOCAL DEV
# ----------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
