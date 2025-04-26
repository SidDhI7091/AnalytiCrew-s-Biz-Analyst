from fastapi import FastAPI, UploadFile, File, HTTPException , Depends
from firebase.firebase_init import store_parsed_content
from firebase.firebase_init import db
from starlette.datastructures import UploadFile as StarletteUploadFile
from datetime import datetime
import uuid
from services.parsing import (
    pdf_parser, docx_parser, excel_parser, eml_parser,
    txt_parser, html_parser,tesseract_service
)
from services.extraction.mistral_extractor import extract_with_mistral
from services.extraction.formatter import format_combined_extraction
from services.extraction.combined_extractor import extract_from_all_documents
from firebase_admin import firestore
from firebase_admin import auth
from services.parsing import web_scraper
from fastapi import Body
from fastapi.middleware.cors import CORSMiddleware
from api.routes import auth

import random
import string
from api.routes import gap_analysis

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React app origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPPORTED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/jpg"]
SUPPORTED_PDF_TYPES = ["application/pdf"]


# --------------------------------------------
# Dummy user auth - replace with Firebase Auth
# --------------------------------------------
app.include_router(auth.router, prefix="/auth")
app.include_router(gap_analysis.router)

def get_current_user():
    return {"user_id": "user123", "email": "sid@example.com"}  # hardcoded for now

# --------------------------------------------
# Generate a random project ID
# --------------------------------------------
def generate_project_id(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# --------------------------------------------
# Create a new project with generated ID
# --------------------------------------------
@app.post("/projects/create")
def create_project(name: str, description: str, user=Depends(get_current_user)):
    project_id = generate_project_id()
    project_data = {
        "name": name,
        "description": description,
        "owner_id": user["user_id"],
        "allowed_users": [user["user_id"]],
        "created_at": datetime.utcnow().isoformat()
    }
    db.collection("projects").document(project_id).set(project_data)
    return {"project_id": project_id, "message": "Project created successfully."}

# --------------------------------------------
# Extract all requirements from a project's documents
# --------------------------------------------

@app.post("/projects/{project_id}/extract")
def extract_all(project_id: str, user=Depends(get_current_user)):
    parsed_docs_ref = db.collection("projects").document(project_id).collection("parsed_docs")
    docs = parsed_docs_ref.stream()

    combined_text = ""
    sources = []

    for doc in docs:
        data = doc.to_dict()
        combined_text += f"\n\nSource: {data['filename']}\n{data['content']}"
        sources.append(data["filename"])

    raw_result = extract_with_mistral(combined_text)
    formatted = format_combined_extraction(raw_result, sources)

    requirements_ref = db.collection("projects").document(project_id).collection("extracted_requirements")
    for category in ["functional", "non_functional", "security", "regulatory", "ui", "usability", "other"]:
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
    print("Text Sent to Mistral is:", combined_text[:500])  # Print first 500 chars
        

    return {"message": "Extraction complete."}
# --------------------------------------------
# Upload parsed file to a specific project
# --------------------------------------------

@app.post("/projects/{project_id}/upload")
async def upload_file(project_id: str, file: UploadFile = File(...), user=Depends(get_current_user)):
    filename = file.filename.lower()
    content = None

    if filename.endswith(".pdf"):
        content = await pdf_parser.parse_pdf(file)
    elif filename.endswith(".docx"):
        content = await docx_parser.parse_docx(file)
    elif filename.endswith(".xlsx"):
        content = await excel_parser.parse_excel(file)
    elif filename.endswith(".eml"):
        content = await eml_parser.parse_eml(file)
    elif filename.endswith(".txt"):
        content = await txt_parser.parse_txt(file)
    elif filename.endswith(".html") or filename.endswith(".htm"):
        content = await html_parser.parse_html(file)
    elif file.content_type in SUPPORTED_IMAGE_TYPES:
        content = await tesseract_service.extract_text_from_image(file)  
        
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    parsed_doc = {
        "filename": filename,
        "content": content,
        "status": "parsed",
        "timestamp": datetime.utcnow().isoformat()
    }
    

    # store_parsed_content(filename, file.content_type, content)
    db.collection("projects").document(project_id).collection("parsed_docs").add(parsed_doc)

    return {"message": "File parsed successfully", "filename": filename}

# --------------------------------------------
# Get list of projects user has access to
# --------------------------------------------
@app.get("/projects")
def get_user_projects(user=Depends(get_current_user)):
    user_projects = db.collection("projects").where("allowed_users", "array_contains", user["user_id"]).stream()
    return [{"id": p.id, **p.to_dict()} for p in user_projects]

@app.post("/projects/{project_id}/share")
def share_project(project_id: str, new_user_email: str, user=Depends(get_current_user)):
    # Step 1: Get UID of the invited user by email
    try:
        invited_user = auth.get_user_by_email(new_user_email)
        invited_uid = invited_user.uid
    except:
        raise HTTPException(status_code=404, detail="User not found")

    # Step 2: Update project's allowed_users array
    project_ref = db.collection("projects").document(project_id)
    project = project_ref.get()

    if not project.exists:
        raise HTTPException(status_code=404, detail="Project not found")

    project_data = project.to_dict()
    if user["user_id"] != project_data.get("owner_id"):
        raise HTTPException(status_code=403, detail="Only the owner can share the project")

    project_ref.update({
        "allowed_users": firestore.ArrayUnion([invited_uid])
    })

    return {"message": f"User {new_user_email} added to project."}

@app.post("/projects/{project_id}/remove")
def remove_user_from_project(project_id: str, remove_user_email: str, user=Depends(get_current_user)):
    # Step 1: Get UID of the user to be removed
    try:
        user_to_remove = auth.get_user_by_email(remove_user_email)
        remove_uid = user_to_remove.uid
    except:
        raise HTTPException(status_code=404, detail="User not found")

    # Step 2: Validate ownership
    project_ref = db.collection("projects").document(project_id)
    project = project_ref.get()

    if not project.exists:
        raise HTTPException(status_code=404, detail="Project not found")

    project_data = project.to_dict()
    if user["user_id"] != project_data.get("owner_id"):
        raise HTTPException(status_code=403, detail="Only the owner can remove users")

    # Step 3: Remove the user UID
    project_ref.update({
        "allowed_users": firestore.ArrayRemove([remove_uid])
    })

    return {"message": f"User {remove_user_email} removed from project."}

@app.get("/projects/{project_id}/members")
def list_project_members(project_id: str, user=Depends(get_current_user)):
    project_ref = db.collection("projects").document(project_id)
    project = project_ref.get()

    if not project.exists:
        raise HTTPException(status_code=404, detail="Project not found")

    project_data = project.to_dict()

    # Only allowed users can view the list
    if user["user_id"] not in project_data.get("allowed_users", []):
        raise HTTPException(status_code=403, detail="Access denied")

    member_uids = project_data.get("allowed_users", [])

    members = []
    for uid in member_uids:
        try:
            user_record = auth.get_user(uid)
            members.append({
                "uid": uid,
                "email": user_record.email,
                "display_name": user_record.display_name
            })
        except:
            continue

    return {"members": members}

