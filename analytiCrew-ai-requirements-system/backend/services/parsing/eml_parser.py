import email

async def parse_eml(file):
    contents = await file.read()
    msg = email.message_from_bytes(contents)
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                return part.get_payload(decode=True).decode("utf-8", errors="ignore")
    return msg.get_payload(decode=True).decode("utf-8", errors="ignore")

