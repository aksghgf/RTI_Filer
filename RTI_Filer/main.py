from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv(encoding="utf-8-sig")

from core.validator import validate_rti_input
from core.classifier import classify_issue
from core.fallback import generate_rti_pipeline
from core.pdf_gen import create_rti_pdf
from core.db import get_db_connection, init_db_schema

OUTPUTS_DIR = os.getenv("OUTPUTS_DIR", "outputs")
os.makedirs(OUTPUTS_DIR, exist_ok=True)

DEFAULT_CORS = "http://localhost:4200,http://127.0.0.1:4200,http://localhost:8080"
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", DEFAULT_CORS).split(",")
    if origin.strip()
]
CORS_ORIGIN_REGEX = os.getenv("CORS_ORIGIN_REGEX", r"https://.*\.vercel\.app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    try:
        init_db_schema()
    except Exception as db_error:
        print(f"Database schema init skipped: {db_error}")
    yield


app = FastAPI(title="RTI Auto-Filer API", version="2.0", lifespan=lifespan)
app.mount("/outputs", StaticFiles(directory=OUTPUTS_DIR), name="outputs")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_origin_regex=CORS_ORIGIN_REGEX,
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
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            insert_query = """
            INSERT INTO rti_applications (
                user_name, user_location, problem_text, detected_ministry,
                rti_draft, pdf_path, language
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id;
            """
            cursor.execute(
                insert_query,
                (
                    request.user_name,
                    request.user_location,
                    input_check.sanitized_text,
                    current_ministry,
                    final_draft,
                    pdf_path,
                    input_check.language,
                ),
            )
            cursor.fetchone()
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as db_error:
            print(f"Database persist skipped: {db_error}")



        # Return cleanly parsed metadata structure back to frontend
        return {
            "status": "success",
            "detected_ministry": detected_dept['ministry'],
            "pdf_path": pdf_path,
            "draft_preview": final_draft
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Agentic Error: {str(e)}")