from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models.schemas import (
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

# -------------------------
# CORS (REQUIRED)
# -------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # You can restrict this to your Lovable domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------
# ROOT
# -------------------------
@app.get("/")
async def root():
    return {"message": "StudyBuddy API", "status": "running"}


# -------------------------
# UPLOAD FILE
# -------------------------
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

    # *** FIXED response format for frontend ***
    return {
        "ok": True,
        "doc_id": material_id,
        "title": material.title,
        "chunks": len(material.content.split()),
        "message": f"Uploaded '{material.title}'"
    }


# -------------------------
# UPLOAD TEXT
# -------------------------
@app.post("/upload/text")
async def upload_text(
    text: str = Form(...),
    title: str = Form("Untitled")
):
    material_id, material = process_and_store_text(text=text, title=title)

    return {
        "ok": True,
        "doc_id": material_id,
        "title": material.title,
        "chunks": len(material.content.split()),
        "message": f"Uploaded '{material.title}'"
    }


# -------------------------
# LIST MATERIALS
# -------------------------
@app.get("/materials")
async def list_materials():
    summaries = material_storage.get_summaries()

    # Convert backend memory to frontend format
    frontend_list = [
        {
            "doc_id": m.id,
            "title": m.title,
            "type": m.type.value,
            "word_count": len(m.content.split())
        }
        for m in summaries
    ]

    return {
        "ok": True,
        "materials": frontend_list,
        "total_count": len(frontend_list)
    }


# -------------------------
# GET MATERIAL
# -------------------------
@app.get("/materials/{material_id}")
async def get_material(material_id: str):
    material = material_storage.get(material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Not found")

    return {
        "doc_id": material.id,
        "title": material.title,
        "type": material.type.value,
        "content": material.content
    }


# -------------------------
# CLEAR MATERIALS
# -------------------------
@app.delete("/materials")
async def clear_materials():
    material_storage.clear()
    reset_agent()
    return {"ok": True, "message": "Cleared"}


# -------------------------
# CHAT
# -------------------------
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
@app.post("/materials/upload")
async def alias_upload_file(file: UploadFile = File(...), title: str = Form(None)):
    return await upload_file(file=file, title=title)

@app.post("/materials/upload-text")
async def alias_upload_text(text: str = Form(...), title: str = Form("Untitled")):
    return await upload_text(text=text, title=title)

@app.get("/materials/list")
async def alias_list_materials():
    return await list_materials()


# -------------------------
# Local dev
# -------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


