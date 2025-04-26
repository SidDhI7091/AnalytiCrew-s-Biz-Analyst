from datetime import datetime
from uuid import uuid4

def format_combined_extraction(raw_output, source_files):
    return {
        "id": f"REQ-{str(uuid4())[:8]}",
        "requirement_text": "Combined extraction from multiple documents.",
        "functional": "\n".join(raw_output.get("functional", [])),
        "non_functional": "\n".join(raw_output.get("non_functional", [])),
        "regulatory": "\n".join(raw_output.get("regulatory", [])),
        "security": "\n".join(raw_output.get("security", [])),
        "ui": "\n".join(raw_output.get("ui", [])),
        "usability": "\n".join(raw_output.get("usability", [])),
        "other": "\n".join(raw_output.get("other", [])),
        "source": ", ".join(source_files),
        "confidence_score": 0.92,  # Heuristic or placeholder
        "priority": "High",
        "status": "Extracted",
        "extracted_keywords": [],  # Fill later via NER/spacy
        "stakeholders": [],
        "domain_entity": "",
        "related_requirements": [],
        "ambiguity_flag": False,
        "conflict_flag": False,
        "generated_questions": [],  # Optional: use LLM later
        "traceability_link": "",
        "timestamp": datetime.utcnow().isoformat()
    }