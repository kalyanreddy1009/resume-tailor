export const API_URL = "http://localhost:8000/api";

export interface TailorResponse {
  analysis: {
    match_score: number;
    matching_skills: string[];
    missing_but_true: string[];
    missing_and_absent: string[];
    changes_summary: string[];
  };
  resume: string;
}

export async function checkHealth(): Promise<{ status: string; agy_installed: boolean }> {
  const res = await fetch(`${API_URL.replace("/api", "")}/api/health`);
  if (!res.ok) throw new Error("Health check failed");
  return res.json();
}

export async function getMasterResume(): Promise<string> {
  const res = await fetch(`${API_URL}/resume/`);
  if (!res.ok) throw new Error("Failed to fetch master resume");
  const data = await res.json();
  return data.content || "";
}

export async function updateMasterResume(content: string): Promise<void> {
  const res = await fetch(`${API_URL}/resume/`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content }),
  });
  if (!res.ok) throw new Error("Failed to update master resume");
}

export async function importResume(file: File): Promise<string> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_URL}/resume/import`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => null);
    if (errorData && errorData.detail) {
       throw { ...errorData.detail };
    }
    throw { error: "Import Failed", hint: `Server returned ${res.status} ${res.statusText}` };
  }
  const data = await res.json();
  return data.parsed_content;
}

export async function tailorResume(jobDescription: string, customInstructions: string = ""): Promise<TailorResponse> {
  const res = await fetch(`${API_URL}/tailor/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ job_description: jobDescription, custom_instructions: customInstructions }),
  });
  
  if (!res.ok) {
    const errorData = await res.json().catch(() => null);
    if (errorData && errorData.detail) {
       throw { ...errorData.detail };
    }
    throw { error: "Tailor Request Failed", hint: "Unknown error occurred" };
  }
  
  return res.json();
}

export async function exportDocument(content: string, format: "docx" | "pdf"): Promise<void> {
  const res = await fetch(`${API_URL}/export/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content, format }),
  });
  
  if (!res.ok) throw new Error("Failed to export document");
  
  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  const dateStr = new Date().toISOString().split("T")[0];
  a.download = `Resume_Tailored_${dateStr}.${format}`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
}
