# Resume Tailor

A local, privacy-first web application that perfectly tailors your master resume to job descriptions without inventing any false information or sending your data to third-party cloud APIs.

## Prerequisites

Before running the application, ensure your system has the following installed:
- **Node.js 18+**
- **Python 3.11+**
- **Antigravity CLI (`agy`)**: The local AI engine.
- **Git** & **GitHub CLI (`gh`)**: (Optional) To manage version control and pushes.

**Important Setup Step**: You must be authenticated with the `agy` CLI for the AI generation to work. Ensure you have quota remaining.

## Setup & Run

1. Clone or download this repository.
2. Run `start.bat` (Windows) or `start.sh` (Mac/Linux).
3. The script will automatically check for prerequisites, launch the FastAPI backend (`http://localhost:8000`), launch the Next.js frontend (`http://localhost:3000`), and open the app in your default browser.

## First-Run Setup: Master Resume Import

The **Master Resume** is the single source of truth for the application. The AI will *never* invent skills or dates that are not present in this document.

1. Open the application and navigate to the **Master Resume** tab (`/editor`).
2. Click **Import PDF/DOCX** and upload your current resume.
3. The application will parse your resume into structured Markdown.
4. **MANDATORY**: Review the generated Markdown carefully. Parsing multi-column PDFs can sometimes be unreliable. Fix any formatting issues and make sure all your experience is comprehensive, as the AI can only work with what is written here. The document auto-saves as you type.

## Daily Usage Flow

1. Find a job you want to apply for and copy its full Job Description.
2. Open the **Home** page of Resume Tailor.
3. Paste the Job Description into the first text box.
4. (Optional) Provide custom instructions in the second text box (e.g., *"Focus heavily on React, ignore backend skills, keep it under 1 page"*).
5. Click **Tailor My Resume**.
6. The app will generate a highly optimized resume in real-time. Once finished, you will see a Match Score, a breakdown of matching/missing skills, and a summary of what the AI changed.
7. Click **Download PDF** or **Download DOCX** to get your ATS-friendly, single-column tailored resume.

## Technical Details: The AI Engine File-Handoff Pattern

There is a known limitation where the `agy -p` CLI silently prints nothing to standard output when invoked from a subprocess without a real terminal. 

To guarantee reliability, Resume Tailor avoids capturing `stdout` entirely. Instead, it utilizes a strict **file-handoff pattern**:
1. The backend writes the sanitized job description to `workspace/job_description.md`.
2. The backend deletes any stale output files.
3. The backend invokes `agy` and explicitly instructs it to write its final output to `workspace/analysis.json` and `workspace/tailored_resume.md`.
4. The backend waits for the process to exit, then reads the files from disk and returns them to the frontend.

This pattern ensures that long generations don't crash, timeout, or block the FastAPI event loop, providing a smooth and stable experience.
