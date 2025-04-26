from firebase_admin import firestore
from services.extraction.mistral_extractor import extract_with_mistral
from services.extraction.formatter import format_combined_extraction
from datetime import datetime
import uuid

db = firestore.client()

def extract_from_all_documents(project_id):
    parsed_docs_ref = db.collection("projects").document(project_id).collection("parsed_docs")
    docs = parsed_docs_ref.stream()

    combined_text = ""
    sources = []

    for doc in docs:
        data = doc.to_dict()
        if data.get("status") == "parsed":
            combined_text += f"\n\nSource: {data['filename']}\n{data['content']}"
            sources.append(data["filename"])

    if not combined_text.strip():
        return {"error": "No parsed content found"}

    raw_result = extract_with_mistral(combined_text)

    requirements_ref = db.collection("projects").document(project_id).collection("extracted_requirements")
    total_saved = 0    

    for category in ["functional", "non_functional", "regulatory", "security", "ui", "usability", "other"]:
        for req_text in raw_result.get(category, []):
            req_id = f"REQ-{str(uuid.uuid4())[:8]}"
            requirement = {
                "id": req_id,
                "requirement_text": req_text,
                "category": category.capitalize(),
                "source": ", ".join(sources),
                "priority": "High",
                "status": "Extracted",
                "timestamp": datetime.utcnow().isoformat()
            }
            requirements_ref.document(req_id).set(requirement)
            total_saved += 1

    return {"message": "Combined extraction complete"}