from pathlib import Path

# Base directory of backend (c:\Users\...\resume-tailor\backend)
BASE_DIR = Path(__file__).resolve().parent

# Workspace directory (c:\Users\...\resume-tailor\workspace)
WORKSPACE_DIR = BASE_DIR.parent / "workspace"
WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
