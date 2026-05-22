from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import os
from dotenv import load_dotenv

# Base path clear karke explicit encoding do
load_dotenv(encoding="utf-8-sig")

# Core agents and utility logic imports
from core.validator import validate_rti_input
from core.classifier import classify_issue  # Base JSON model function
from core.fallback import generate_rti_pipeline
from core.pdf_gen import create_rti_pdf
from core.db import get_db_connection
# 1. Initialize FastAPI App
app = FastAPI(title="RTI Auto-Filer API", version="2.0")
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")
# 2. CORS Middleware Configuration (Mandatory for Angular Frontend Integration)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # Angular Local Dev Port [cite: 381]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Request Data Transfer Object (DTO) using Pydantic
class RTIRequest(BaseModel):
    user_name: str
    user_location: str
    problem_text: str

# 4. Health Check Endpoint
@app.get("/")
def read_root():
    return {"status": "healthy", "service": "RTI Auto-Filer Backend Engine"}

# 5. Core RTI Generation Endpoint
@app.post("/api/v1/generate-rti")
async def generate_rti_endpoint(request: RTIRequest):
    """FastAPI wrapper that processes input, runs agent loops, and outputs a PDF."""
    
    # Stage 1: Input Validation & Language Detection
    input_check = validate_rti_input(request.problem_text)
    if not input_check.valid:
        raise HTTPException(status_code=400, detail=input_check.hint)
        
    try:
        # Stage 2: Target Ministry Classification (Using ministries.json)
        # Note: Ensure core/classifier.py exposes a function that handles keyword parsing
        detected_dept = classify_issue(input_check.sanitized_text)
        
        current_ministry = detected_dept['ministry']

        # Stage 3: Dynamic Multi-Lingual AI Drafting Pipeline (Groq / Gemini)
        final_draft = await generate_rti_pipeline(
            user_query=input_check.sanitized_text,
            user_name=request.user_name,
            user_location=request.user_location,
            #language=input_check.language
        )
        
        # Stage 4: Crisp PDF Generation with Noto Sans Devanagari support
        pdf_path = create_rti_pdf(
            rti_text=final_draft,
            ministry_name=detected_dept['ministry'],
            user_name=request.user_name,
            user_location=request.user_location
        )
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        insert_query = """
        INSERT INTO rti_applications (user_name, user_location, problem_text, detected_ministry, rti_draft, pdf_path, language)
        VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id;
        """
        
        cursor.execute(insert_query, (
            request.user_name,
            request.user_location,
            input_check.sanitized_text,
            current_ministry,
            final_draft,
            pdf_path,
            input_check.language  # ➕ Storing detected language inside database
        ))
        
        db_record_id = cursor.fetchone()[0]
        
        conn.commit()  
        cursor.close()
        conn.close()



        # Return cleanly parsed metadata structure back to frontend
        return {
            "status": "success",
            "detected_ministry": detected_dept['ministry'],
            "pdf_path": pdf_path,
            "draft_preview": final_draft
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Agentic Error: {str(e)}")