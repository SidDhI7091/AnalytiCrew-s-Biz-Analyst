from firebase.firebase_init import db
from services.gap_analysis.gap_analyzer import find_missing_requirements
from firebase_admin import firestore
from datetime import datetime

def chatbot_gap_analysis(project_id):
    missing_reqs = find_missing_requirements(project_id)

    if not missing_reqs:
        return {"message": "No missing requirements found!"}

    print("\n🔎 Missing Requirements Detected:\n")
    for idx, req in enumerate(missing_reqs, 1):
        print(f"{idx}. {req['id']} - {req['requirement_text']}")

    selection = input("\nEnter numbers of requirements you want to add (comma-separated), or 'no' to skip: ")

    if selection.lower() == "no":
        return {"message": "No missing requirements added."}

    selected_indices = [int(x.strip()) for x in selection.split(",") if x.strip().isdigit()]
    for idx in selected_indices:
        if 1 <= idx <= len(missing_reqs):
            req = missing_reqs[idx - 1]
            add_requirement_to_firestore(project_id, req)

    return {"message": "Selected missing requirements added successfully."}

def add_requirement_to_firestore(project_id, requirement):
    req_doc = {
        "id": requirement["id"],
        "requirement_text": requirement["requirement_text"],
        "category": "Gap_Filled",
        "source": "Ideal Standard",
        "priority": "Medium",
        "status": "Extracted",
        "timestamp": firestore.SERVER_TIMESTAMP
    }

    db.collection("projects").document(project_id).collection("extracted_requirements").add(req_doc)