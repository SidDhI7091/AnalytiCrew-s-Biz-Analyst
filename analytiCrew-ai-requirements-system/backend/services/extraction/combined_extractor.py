from firebase_admin import firestore
from services.extraction.mistral_extractor import extract_with_mistral
from services.extraction.formatter import format_combined_extraction

db = firestore.client()

def extract_from_all_documents():
    docs = db.collection("parsed_docs").get()

    combined_text = ""
    sources = []

    for doc in docs:
        data = doc.to_dict()
        if data.get("status") == "parsed" and "content" in data:
            combined_text += f"\n\nSource: {data['filename']}\n{data['content']}"
            sources.append(data["filename"])

    if not combined_text.strip():
        return {"error": "No parsed content found"}

    raw_result = extract_with_mistral(combined_text)

    # Format all categories (functional, non-functional, etc.) into a single JSON record
    formatted = format_combined_extraction(raw_result, sources)

    # Store in a new document
    output_doc = {
        "filename": "ALL_COMBINED",
        "content": combined_text,
        "status": "extracted",
        "timestamp": firestore.SERVER_TIMESTAMP,
        "extracted": {
            "requirements": [formatted]
        }
    }

    db.collection("extracted_combined").add(output_doc)
    return {"message": "Combined extraction complete"}
