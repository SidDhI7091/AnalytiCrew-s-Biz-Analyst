async def parse_txt(file):
    content = await file.read()
    return content.decode("utf-8", errors="ignore")
