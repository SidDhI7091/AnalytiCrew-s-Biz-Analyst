from bs4 import BeautifulSoup

async def parse_html(file):
    content = await file.read()
    soup = BeautifulSoup(content, "html.parser")
    return soup.get_text()
