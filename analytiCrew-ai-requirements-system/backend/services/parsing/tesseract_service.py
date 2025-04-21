from fastapi import UploadFile
from PIL import Image
import pytesseract
from io import BytesIO

async def extract_text_from_image(file: UploadFile) -> str:
    contents = await file.read()
    try:
        
        image = Image.open(BytesIO(contents))
        text = pytesseract.image_to_string(image,lang='eng+hin')
        return text.strip()
    except Exception as e:
        return f"Error processing image: {str(e)}"

