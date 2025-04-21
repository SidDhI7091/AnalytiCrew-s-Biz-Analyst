import fitz  # pymupdf
from io import BytesIO

async def parse_pdf(file):
    contents = await file.read()
    doc = fitz.open(stream=BytesIO(contents), filetype="pdf")
    return "\n".join([page.get_text() for page in doc])
