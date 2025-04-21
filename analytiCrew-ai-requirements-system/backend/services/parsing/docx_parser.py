from docx import Document
from io import BytesIO

async def parse_docx(file):
    contents = await file.read()
    doc = Document(BytesIO(contents))
    return "\n".join([p.text for p in doc.paragraphs])

