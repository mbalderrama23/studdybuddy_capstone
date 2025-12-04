import sqlite3
from dataclasses import dataclass
from typing import List, Optional

DB_PATH = "materials.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS materials (
            id TEXT PRIMARY KEY,
            title TEXT,
            type TEXT,
            content TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

@dataclass
class MaterialRow:
    id: str
    title: str
    type: str
    content: str

class MaterialDB:
    def __init__(self):
        self.path = DB_PATH

    def save(self, material):
        conn = sqlite3.connect(self.path)
        conn.execute(
            "REPLACE INTO materials (id, title, type, content) VALUES (?, ?, ?, ?)",
            (material.id, material.title, 
             material.type.value if hasattr(material.type, "value") else material.type, 
             material.content)
        )
        conn.commit()
        conn.close()

    def get(self, material_id: str) -> Optional[MaterialRow]:
        conn = sqlite3.connect(self.path)
        cur = conn.execute(
            "SELECT id, title, type, content FROM materials WHERE id = ?",
            (material_id,)
        )
        row = cur.fetchone()
        conn.close()

        if not row:
            return None

        return MaterialRow(id=row[0], title=row[1], type=row[2], content=row[3])

    def list(self) -> List[MaterialRow]:
        conn = sqlite3.connect(self.path)
        cur = conn.execute(
            "SELECT id, title, type, content FROM materials ORDER BY ROWID DESC"
        )
        rows = [MaterialRow(id=r[0], title=r[1], type=r[2], content=r[3]) 
                for r in cur.fetchall()]
        conn.close()
        return rows

    # ⭐ NEW DELETE METHOD
    def delete(self, material_id: str) -> bool:
        conn = sqlite3.connect(self.path)
        cur = conn.execute("DELETE FROM materials WHERE id = ?", (material_id,))
        conn.commit()
        conn.close()
        return cur.rowcount > 0

    def clear(self):
        conn = sqlite3.connect(self.path)
        conn.execute("DELETE FROM materials")
        conn.commit()
        conn.close()


material_db = MaterialDB()
