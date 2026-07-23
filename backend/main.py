import os
import subprocess
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from routers import resume, tailor, export

app = FastAPI(title="Resume Tailor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resume.router, prefix="/api/resume", tags=["resume"])
app.include_router(tailor.router, prefix="/api/tailor", tags=["tailor"])
app.include_router(export.router, prefix="/api/export", tags=["export"])

agy_installed = False

@app.on_event("startup")
async def startup_event():
    global agy_installed
    # Check if agy is installed
    try:
        subprocess.run(["cmd", "/c", "agy --version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        agy_installed = True
    except Exception:
        print("WARNING: agy CLI not found or failed to run. Ensure agy is installed and in PATH.")

@app.get("/api/health")
def health():
    return {"status": "ok", "agy_installed": agy_installed}
