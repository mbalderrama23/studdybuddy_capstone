from typing import Dict, List, Optional
import uuid

from models.schemas import Material, MaterialSummary


class MaterialStorage:
    def __init__(self):
        self._materials: Dict[str, Material] = {}
    
    def generate_id(self) -> str:
        return str(uuid.uuid4())[:8]
    
    def store(self, material: Material) -> str:
        self._materials[material.id] = material
        return material.id
    
    def get(self, material_id: str) -> Optional[Material]:
        return self._materials.get(material_id)
    
    def get_all(self) -> List[Material]:
        return list(self._materials.values())
    
    def get_summaries(self) -> List[MaterialSummary]:
        summaries = []
        for material in self._materials.values():
            preview = material.content[:200] + "..." if len(material.content) > 200 else material.content
            summary = MaterialSummary(
                id=material.id,
                title=material.title,
                type=material.type,
                created_at=material.created_at,
                content_preview=preview,
                word_count=len(material.content.split())
            )
            summaries.append(summary)
        return summaries
    
    def delete(self, material_id: str) -> bool:
        if material_id in self._materials:
            del self._materials[material_id]
            return True
        return False
    
    def search(self, query: str, material_ids: Optional[List[str]] = None) -> List[Dict]:
        query_lower = query.lower()
        results = []
        
        materials_to_search = self._materials.values()
        if material_ids:
            materials_to_search = [m for m in materials_to_search if m.id in material_ids]
        
        for material in materials_to_search:
            content_lower = material.content.lower()
            if query_lower in content_lower:
                pos = content_lower.find(query_lower)
                start = max(0, pos - 100)
                end = min(len(material.content), pos + 100)
                snippet = material.content[start:end]
                
                results.append({
                    "material_id": material.id,
                    "title": material.title,
                    "snippet": snippet
                })
        
        return results
    
    def get_content_by_ids(self, material_ids: List[str]) -> str:
        contents = []
        for mid in material_ids:
            material = self.get(mid)
            if material:
                contents.append(f"=== {material.title} ===\n{material.content}")
        return "\n\n".join(contents)
    
    def clear(self):
        self._materials.clear()


material_storage = MaterialStorage()
