from bs4 import BeautifulSoup

async def parse_html(file):
    content = await file.read()
    decoded_content = content.decode("utf-8", errors="ignore")
    soup = BeautifulSoup(decoded_content, "html.parser")
    return soup.get_text()
