from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import JSONResponse
from firebase_admin import firestore
from services.extraction.mistral_extractor import extract_with_mistral
from services.extraction.formatter import format_combined_extraction
from typing import List
import uuid
from datetime import datetime

router = APIRouter()

@router.post("/gap-analysis/{project_id}")
async def trigger_gap_analysis(project_id: str):
    # Step 1: Fetch all extracted and ideal requirements from Firestore
    db = firestore.client()
    project_ref = db.collection("projects").document(project_id)
    
    # Get extracted requirements
    extracted_ref = project_ref.collection("extracted_requirements")
    extracted_docs = extracted_ref.stream()
    extracted_requirements = []
    for doc in extracted_docs:
        data = doc.to_dict()
        extracted_requirements.append(data["requirement_text"])

    # Get ideal requirements from a local JSON or Firestore
    # Here we assume you have a JSON file for ideal requirements
    ideal_requirements = get_ideal_requirements()

    # Step 2: Send requirements to Mistral for gap analysis
    combined_requirements = extracted_requirements 
    gap_analysis_result = extract_with_mistral("\n".join(combined_requirements))

    # Step 3: Check if the analysis returned any missing requirements
    missing_requirements = gap_analysis_result.get("missing", [])

    # Step 4: Return missing requirements to the chatbot
    if missing_requirements:
        formatted_requirements = [{"id": str(idx + 1), "requirement_text": req} for idx, req in enumerate(missing_requirements)]
        return {"missing": formatted_requirements}
    else:
        return {"message": "No missing requirements found."}

def get_ideal_requirements():
    # Ideally, you would fetch these from Firestore or a local JSON file
    # Example structure
    return [
        "The system must allow users to reset their password easily.",
        "Users must be able to log in using multi-factor authentication.",
        "The system should provide an audit trail for all sensitive actions.",
        # Add more requirements
    ]
