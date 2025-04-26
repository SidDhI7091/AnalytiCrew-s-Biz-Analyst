from services.gap_analysis.ideal_loader import load_ideal_requirements
from firebase.firebase_init import db

def fetch_extracted_texts(project_id):
    extracted_texts = []
    docs_ref = db.collection("projects").document(project_id).collection("extracted_requirements").stream()
    for doc in docs_ref:
        data = doc.to_dict()
        if "requirement_text" in data:
            extracted_texts.append(data["requirement_text"].lower())
    return extracted_texts

def find_missing_requirements(project_id):
    ideal_requirements = load_ideal_requirements()
    extracted_texts = fetch_extracted_texts(project_id)

    missing = []
    for ideal in ideal_requirements:
        keyword = ideal["word_to_match"].lower()
        keyword_found = False
        for text in extracted_texts:
            if keyword in text:
                keyword_found = True
                break
        
        if not keyword_found:
            missing.append(ideal)
    
    return missing
