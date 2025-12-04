from typing import Optional, Tuple
from datetime import datetime
import io
import os

from models.schemas import Material, MaterialType
from storage.memory import material_storage


def detect_material_type(filename: str, content_type: Optional[str] = None) -> MaterialType:
    filename_lower = filename.lower()
    if filename_lower.endswith('.pdf'):
        return MaterialType.PDF
    elif filename_lower.endswith('.docx'):
        return MaterialType.DOCX
    elif filename_lower.endswith('.pptx'):
        return MaterialType.PPTX
    elif filename_lower.endswith('.txt'):
        return MaterialType.TXT
    elif filename_lower.endswith('.md'):
        return MaterialType.MARKDOWN
    return MaterialType.UNKNOWN


def extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(io.BytesIO(file_bytes))
        text_parts = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
        return "\n\n".join(text_parts)
    except Exception as e:
        return f"[Error extracting PDF: {str(e)}]"


def extract_text_from_docx(file_bytes: bytes) -> str:
    try:
        from docx import Document
        doc = Document(io.BytesIO(file_bytes))
        paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
        return "\n\n".join(paragraphs)
    except Exception as e:
        return f"[Error extracting DOCX: {str(e)}]"


def extract_text_from_pptx(file_bytes: bytes) -> str:
    try:
        from pptx import Presentation
        prs = Presentation(io.BytesIO(file_bytes))
        text_parts = []
        for slide_num, slide in enumerate(prs.slides, 1):
            slide_text = [f"--- Slide {slide_num} ---"]
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    slide_text.append(shape.text)
            text_parts.append("\n".join(slide_text))
        return "\n\n".join(text_parts)
    except Exception as e:
        return f"[Error extracting PPTX: {str(e)}]"


def extract_text(file_bytes: bytes, material_type: MaterialType) -> str:
    if material_type == MaterialType.PDF:
        return extract_text_from_pdf(file_bytes)
    elif material_type == MaterialType.DOCX:
        return extract_text_from_docx(file_bytes)
    elif material_type == MaterialType.PPTX:
        return extract_text_from_pptx(file_bytes)
    elif material_type in (MaterialType.TXT, MaterialType.MARKDOWN):
        try:
            return file_bytes.decode('utf-8')
        except:
            return "[Error decoding text file]"
    return "[Unknown file format]"


def process_and_store_file(
    filename: str,
    file_bytes: bytes,
    content_type: Optional[str] = None,
    custom_title: Optional[str] = None
) -> Tuple[str, Material]:
    material_type = detect_material_type(filename, content_type)
    content = extract_text(file_bytes, material_type)
    material_id = material_storage.generate_id()
    title = custom_title or os.path.splitext(filename)[0]
    
    material = Material(
        id=material_id,
        title=title,
        type=material_type,
        content=content,
        created_at=datetime.now().isoformat(),
        metadata_info=f"filename:{filename},size:{len(file_bytes)}"
    )
    
    material_storage.store(material)
    return material_id, material


def process_and_store_text(text: str, title: str = "Untitled Notes") -> Tuple[str, Material]:
    material_id = material_storage.generate_id()
    
    material = Material(
        id=material_id,
        title=title,
        type=MaterialType.TXT,
        content=text,
        created_at=datetime.now().isoformat(),
        metadata_info="source:direct_text"
    )
    
    material_storage.store(material)
    return material_id, material


def get_material_content(material_id: str) -> Optional[str]:
    material = material_storage.get(material_id)
    if material:
        return material.content
    return None


def get_all_materials_content(material_ids: Optional[list] = None) -> str:
    if material_ids:
        return material_storage.get_content_by_ids(material_ids)
    materials = material_storage.get_all()
    if not materials:
        return "[No materials uploaded yet]"
    return material_storage.get_content_by_ids([m.id for m in materials])
