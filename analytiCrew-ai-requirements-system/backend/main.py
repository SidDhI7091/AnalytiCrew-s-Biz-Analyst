from fastapi import FastAPI, UploadFile, File, HTTPException
from firebase.firebase_init import store_parsed_content
from starlette.datastructures import UploadFile as StarletteUploadFile
from services.parsing import (
    pdf_parser, docx_parser, excel_parser, eml_parser,
    txt_parser, html_parser,tesseract_service
)


app = FastAPI()

SUPPORTED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/jpg"]
SUPPORTED_PDF_TYPES = ["application/pdf"]



@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
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

    store_parsed_content(filename, file.content_type, content)

    return {"message": "File parsed successfully", "filename": filename}
