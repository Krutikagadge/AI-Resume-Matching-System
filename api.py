from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware  # To prevent CORS issues
from pydantic import BaseModel
from typing import List
import os
import logging
from matching import match_candidates  # Ensure this file exists and is correctly implemented

# ✅ Initialize FastAPI
app = FastAPI()

# ✅ Enable CORS (Important for Frontend to access Backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (Adjust for security)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Logging Configuration
logging.basicConfig(level=logging.INFO)

# ✅ Root Endpoint (Fix for 404 Error)
@app.get("/")
def read_root():
    return {"message": "Resume Analyzer API is running!"}

# ✅ Define request model
class JobRequest(BaseModel):
    category: str
    job_description: str
    top_n: int = 5  # Default to top 5 candidates

# ✅ Define response model
class CandidateMatch(BaseModel):
    rank: int
    resume_file: str
    match_score: float

# ✅ Define API Endpoint for Matching Candidates
@app.post("/score_candidates", response_model=List[CandidateMatch])
def score_candidates(job: JobRequest):
    """
    API endpoint to get top matching candidates based on job description.
    """
    logging.info(f"Received job description for category: {job.category}")
    
    results = match_candidates(job.job_description, job.category, job.top_n)
    
    # Convert .txt filenames to corresponding .pdf filenames
    for result in results:
        txt_filename = result["resume_file"]
        pdf_filename = txt_filename.replace(".txt", ".pdf")
        result["resume_file"] = pdf_filename  # Updating response to return PDF names

    return results

# ✅ Serve Resumes as PDF
RESUME_DIR = "raw_resumes"  # Base directory containing category subfolders

@app.get("/resumes/{category}/{filename}")
async def get_resume(category: str, filename: str):
    """
    Endpoint to serve resumes as downloadable PDF files.
    """
    file_path = os.path.join(RESUME_DIR, category, filename)
    
    if os.path.exists(file_path):
        logging.info(f"Serving resume: {file_path}")
        return FileResponse(file_path, media_type="application/pdf")
    
    logging.error(f"File not found: {file_path}")
    return {"detail": "File Not Found"}

# ✅ Run FastAPI Server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
