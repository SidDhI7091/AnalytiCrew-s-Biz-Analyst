import pandas as pd
from io import BytesIO

async def parse_excel(file):
    contents = await file.read()
    df = pd.read_excel(BytesIO(contents), engine="openpyxl")
    return df.to_string(index=False)

