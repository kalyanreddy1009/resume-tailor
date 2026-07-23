from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from pathlib import Path
from services.parser import parse_document

from config import WORKSPACE_DIR

router = APIRouter()
MASTER_RESUME_PATH = WORKSPACE_DIR / "master_resume.md"

class MasterResumeContent(BaseModel):
    content: str

@router.get("/")
def get_master_resume():
    if not MASTER_RESUME_PATH.exists():
        return {"content": ""}
    return {"content": MASTER_RESUME_PATH.read_text(encoding="utf-8")}

@router.put("/")
def update_master_resume(req: MasterResumeContent):
    MASTER_RESUME_PATH.write_text(req.content, encoding="utf-8")
    return {"status": "success"}

@router.post("/import")
async def import_resume(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".pdf", ".docx")):
        raise HTTPException(status_code=400, detail={"error": "Unsupported file", "hint": "Only PDF and DOCX files are supported for import."})
    
    content = await file.read()
    
    try:
        parsed_md = parse_document(content, file.filename)
        return {"parsed_content": parsed_md}
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": "Parse error", "hint": str(e)})
