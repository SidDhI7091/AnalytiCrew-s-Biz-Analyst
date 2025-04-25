import requests
from requests.auth import HTTPBasicAuth
import json

# Define ADF formatter first
def format_adf_description(description_text):
    lines = description_text.strip().split('\n')
    content_blocks = []

    for line in lines:
        line = line.strip()

        if line.lower().startswith("title:"):
            content_blocks.append({
                "type": "heading",
                "attrs": {"level": 2},
                "content": [{"type": "text", "text": line[6:].strip()}]
            })
        elif line.startswith("-"):
            content_blocks.append({
                "type": "bulletList",
                "content": [{
                    "type": "listItem",
                    "content": [{
                        "type": "paragraph",
                        "content": [{"type": "text", "text": line[1:].strip()}]
                    }]
                }]
            })
        elif "http" in line:
            text_part = line.split("http")[0].strip()
            url_part = line[line.find("http"):].strip()
            content_blocks.append({
                "type": "paragraph",
                "content": [
                    {"type": "text", "text": text_part + " " if text_part else ""},
                    {"type": "text", "text": url_part, "marks": [{"type": "link", "attrs": {"href": url_part}}]}
                ]
            })
        elif line:
            content_blocks.append({
                "type": "paragraph",
                "content": [{"type": "text", "text": line}]
            })

    return {
        "type": "doc",
        "version": 1,
        "content": content_blocks
    }

# Function to create story
def create_jira_story(email, api_token, project_key, jira_domain, summary, raw_description):
    url = f"https://{jira_domain}.atlassian.net/rest/api/3/issue"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    description_adf = format_adf_description(raw_description)

    payload = json.dumps({
        "fields": {
            "project": {"key": project_key},
            "summary": summary,
            "description": description_adf,
            "issuetype": {"name": "Story"}
        }
    })

    response = requests.post(
        url,
        data=payload,
        headers=headers,
        auth=HTTPBasicAuth(email, api_token)
    )

    if response.status_code == 201:
        print(f"Created story: {summary}")
        return response.json()["key"]
    else:
        print(f"Failed to create story: {response.status_code}")
        print(response.text)
        return None

# Now call the function with real values
sample_description = """
Title: KYC Verification
The system must validate PAN and Aadhaar using NSDL API.
- Integrate with UIDAI endpoint
- Log verification status
More: https://nsdl.co.in
"""

create_jira_story(
    email="analystbarclays@gmail.com",
    api_token="ATATT3xFfGF0xz1wWfGzWt-nDbTIzcYfaIgSbgQqLlAYMrTMO1x8wxWgwWzsAzM1PIUbYMh7bydIIimz4MjfiSCy8v4ZBwWJn3zU1rsAjr6lnCsF2faapfKUYRe510GzEC_iScei6g6vAel4aHpOcMLOjfpabL106zta7GpWsgANhNjly4KTGf0=9361EC46",
    project_key="SCRUM",
    jira_domain="analystbarclays",
    summary="KYC API Integration Requirement",
    raw_description=sample_description
)
