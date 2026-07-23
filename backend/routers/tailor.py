from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from services.agy_runner import run_tailor_pipeline
from pathlib import Path

from config import WORKSPACE_DIR

router = APIRouter()
STATUS_FILE = WORKSPACE_DIR / "status.txt"

class TailorRequest(BaseModel):
    job_description: str
    custom_instructions: str = ""

@router.get("/status")
def get_status():
    if not STATUS_FILE.exists():
        return {"status": "Starting AI engine..."}
    return {"status": STATUS_FILE.read_text(encoding="utf-8").strip() or "Processing..."}

@router.post("/")
async def tailor_resume(req: TailorRequest):
    if not req.job_description or len(req.job_description.strip()) == 0:
        raise HTTPException(status_code=400, detail={"error": "Empty job description", "hint": "Please paste a job description."})
    
    if len(req.job_description) > 15000:
        raise HTTPException(status_code=400, detail={"error": "Job description too large", "hint": "Maximum allowed size is ~15000 characters."})
    
    try:
        result = await run_tailor_pipeline(req.job_description, req.custom_instructions)
        return result
    except Exception as e:
        msg = str(e)
        if "CONFLICT" in msg:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={"error": "Busy", "hint": "Another tailoring job is already in progress. Please wait."})
        elif "NO_OUTPUT" in msg:
            raise HTTPException(status_code=500, detail={"error": "AI Engine Error", "hint": "AI engine produced no output — check that `agy` is installed, authenticated, and has quota remaining."})
        elif "TIMEOUT" in msg:
            raise HTTPException(status_code=504, detail={"error": "Timeout", "hint": "The AI engine took too long to respond. Please try again."})
        else:
            raise HTTPException(status_code=500, detail={"error": "Internal Error", "hint": msg})
