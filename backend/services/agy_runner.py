import asyncio
import os
import json
import subprocess
from pathlib import Path

from config import WORKSPACE_DIR

LOCK = asyncio.Lock()

async def run_tailor_pipeline(job_description: str, custom_instructions: str = ""):
    if LOCK.locked():
        raise Exception("CONFLICT: Another tailoring job is already in progress.")
    
    async with LOCK:
        jd_path = WORKSPACE_DIR / "job_description.md"
        output_resume_path = WORKSPACE_DIR / "tailored_resume.md"
        output_analysis_path = WORKSPACE_DIR / "analysis.json"
        status_path = WORKSPACE_DIR / "status.txt"

        # 1. Write JD
        jd_path.write_text(job_description, encoding="utf-8")
        status_path.write_text("Starting AI engine...", encoding="utf-8")
        
        # 2. Delete stale outputs
        if output_resume_path.exists():
            output_resume_path.unlink()
        if output_analysis_path.exists():
            output_analysis_path.unlink()

        # 3. Run agy
        formatting_rules = (
            "FORMATTING RULES: Format the resume neatly. DO NOT use asterisks (*) or long dashes (—) as they make the output look like an AI prompt. "
            "Use clean, standard markdown with hyphens (-) for bullet points. "
        )
        custom_rules = f"USER CUSTOM INSTRUCTIONS: {custom_instructions} " if custom_instructions else ""
        
        instruction = (
            f"READ RULES.md, master_resume.md, and job_description.md. {formatting_rules} {custom_rules}"
            f"Write your entire output to files. Do not rely on printing to the terminal. "
            f"Produce TWO output files in this run exactly to these paths: "
            f"1) {output_analysis_path} (strict JSON, no markdown fences) containing: match_score (0-100), matching_skills [str], "
            f"missing_but_true [str], missing_and_absent [str], changes_summary [str]. "
            f"2) {output_resume_path} containing the full tailored resume in clean markdown. "
            f"CRITICAL: Write them to the exact absolute paths provided above, DO NOT write them to your scratch directory."
        )
        
        import subprocess
        import threading
        
        cmd = [
            "cmd", "/c", "agy", "-p", instruction, "--mode=accept-edits", "--dangerously-skip-permissions", "--effort", "low"
        ]

        try:
            # 4. Use Popen and threading to stream output safely without asyncio subprocess issues
            process = subprocess.Popen(
                cmd,
                cwd=str(WORKSPACE_DIR),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            def stream_output():
                for line in process.stdout:
                    line_text = line.strip()
                    if line_text:
                        status_path.write_text(line_text, encoding="utf-8")
                        
            thread = threading.Thread(target=stream_output)
            thread.start()
            
            # Wait for process exit in a thread to avoid blocking the event loop
            returncode = await asyncio.to_thread(process.wait, timeout=300)
            thread.join()
            
            if returncode != 0:
                print(f"Warning: agy exited with code {returncode}")
                
        except subprocess.TimeoutExpired:
            process.kill()
            raise Exception("TIMEOUT: AI engine took too long.")
        except Exception as e:
            import traceback
            print(f"Exception in agy_runner:\n{traceback.format_exc()}")
            raise Exception(f"AI_ENGINE_ERROR: {repr(e)}")

        # Check if files exist
        if not output_resume_path.exists() or not output_analysis_path.exists():
            raise Exception("NO_OUTPUT: AI engine produced no output — check that `agy` is installed, authenticated, and has quota remaining.")

        resume_content = output_resume_path.read_text(encoding="utf-8")
        analysis_content = output_analysis_path.read_text(encoding="utf-8")

        # Strip code fences from analysis if any
        analysis_content = analysis_content.strip()
        if analysis_content.startswith("```json"):
            analysis_content = analysis_content[7:]
        if analysis_content.startswith("```"):
            analysis_content = analysis_content[3:]
        if analysis_content.endswith("```"):
            analysis_content = analysis_content[:-3]
        analysis_content = analysis_content.strip()

        try:
            analysis_data = json.loads(analysis_content)
        except json.JSONDecodeError:
            raise Exception("MALFORMED_JSON: AI engine produced invalid JSON analysis.")

        if not resume_content:
            raise Exception("NO_OUTPUT: AI engine produced empty resume.")

        return {
            "analysis": analysis_data,
            "resume": resume_content
        }
