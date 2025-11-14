"""
Data Cleaning Bot - FastAPI Backend
Main application entry point with API endpoints for:
- POST /clean: Upload CSV and get cleaned data + script + AI report
- GET /health: Health check
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from utils_serialization import to_serializable

import os
import tempfile
import base64
from io import StringIO, BytesIO
import traceback

from cleaning_logic import DataCleaningPipeline, generate_python_script
from ai_report import generate_ai_report
from pydantic import BaseModel


# Initialize FastAPI app
app = FastAPI(
    title="Data Cleaning Bot",
    description="Automatic data cleaning with AI-powered reports",
    version="1.0.0"
)

# Add CORS middleware for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CleaningResponse(BaseModel):
    """Response model for cleaning operation."""
    success: bool
    message: str
    cleaned_csv_base64: str = None
    cleaning_script_base64: str = None
    ai_report: str = None
    summary: dict = None


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    Returns: {"status": "ok"}
    """
    return {"status": "ok"}


@app.post("/clean")
async def clean_data(file: UploadFile = File(...)):
    """
    Main cleaning endpoint.
    
    Accepts: CSV file upload
    Returns:
        - cleaned_csv_base64: Base64 encoded cleaned CSV
        - cleaning_script_base64: Base64 encoded Python script
        - ai_report: Human-readable cleaning report
        - summary: Cleaning statistics
    """
    
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=400,
                detail="Only CSV files are supported"
            )
        
        # Read uploaded file
        contents = await file.read()
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='wb') as tmp:
            tmp.write(contents)
            tmp_path = tmp.name
        
        try:
            # Run cleaning pipeline
            pipeline = DataCleaningPipeline()
            cleaned_df, cleaning_steps, summary = pipeline.run_pipeline(tmp_path)
            
            summary = {k: to_serializable(v) for k, v in summary.items()}

            cleaning_steps = [
                {k: to_serializable(v) for k, v in step.items()}
                for step in cleaning_steps
            ]
            # Get original columns for script generation
            original_columns = list(pipeline.original_df.columns)
            
            # Generate Python cleaning script
            cleaning_script = generate_python_script(cleaning_steps, original_columns)
            
            # Generate AI report
            ai_provider = os.getenv("AI_PROVIDER", "openai").lower()
            ai_report = generate_ai_report(
                pipeline.original_df,
                cleaned_df,
                cleaning_steps,
                summary,
                ai_provider=ai_provider
            )
            
            # Convert DataFrames to CSV strings
            cleaned_csv_buffer = StringIO()
            cleaned_df.to_csv(cleaned_csv_buffer, index=False)
            cleaned_csv_str = cleaned_csv_buffer.getvalue()
            
            # Encode to base64 for transmission
            cleaned_csv_base64 = base64.b64encode(
                cleaned_csv_str.encode('utf-8')
            ).decode('utf-8')
            
            cleaning_script_base64 = base64.b64encode(
                cleaning_script.encode('utf-8')
            ).decode('utf-8')
            
            # Prepare response
            response = CleaningResponse(
                success=True,
                message="Data cleaned successfully",
                cleaned_csv_base64=cleaned_csv_base64,
                cleaning_script_base64=cleaning_script_base64,
                ai_report=ai_report,
                summary=summary
            )
            
            return response.model_dump()
        
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    except HTTPException:
        raise
    except Exception as e:
        # Log error details
        error_traceback = traceback.format_exc()
        print(f"Error in /clean endpoint: {error_traceback}")
        
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Data Cleaning Bot API",
        "version": "1.0.0",
        "description": "Automatic CSV data cleaning with AI reports",
        "endpoints": {
            "GET /health": "Health check",
            "POST /clean": "Upload CSV and get cleaned data, script, and AI report"
        },
        "environment": {
            "ai_provider": os.getenv("AI_PROVIDER", "openai"),
            "has_openai_key": bool(os.getenv("OPENAI_API_KEY")),
            "has_groq_key": bool(os.getenv("GROQ_API_KEY"))
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    # Run server on localhost:8000
    # In production, use Vercel serverless functions
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )
