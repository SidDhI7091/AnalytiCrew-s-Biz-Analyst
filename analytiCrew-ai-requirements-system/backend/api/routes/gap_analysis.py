from fastapi import APIRouter
from services.gap_analysis.chatbot_gap_filler import chatbot_gap_analysis,add_requirement_to_firestore

router = APIRouter()

@router.post("/gap-analysis/confirm-add/{project_id}")
def confirm_add_requirements(project_id: str, req_body: dict):
    requirements = req_body.get("requirements", [])
    for req_text in requirements:
        add_requirement_to_firestore(project_id, req_text)
    return {"message": "Selected requirements added."}

@router.post("/gap-analysis/{project_id}")
def trigger_gap_analysis(project_id: str):
    result = chatbot_gap_analysis(project_id)
    return result

