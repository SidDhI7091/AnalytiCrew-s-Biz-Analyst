# import requests
# from requests.auth import HTTPBasicAuth
# import json

# # Define ADF formatter first
# def format_adf_description(description_text):
#     lines = description_text.strip().split('\n')
#     content_blocks = []

#     for line in lines:
#         line = line.strip()

#         if line.lower().startswith("title:"):
#             content_blocks.append({
#                 "type": "heading",
#                 "attrs": {"level": 2},
#                 "content": [{"type": "text", "text": line[6:].strip()}]
#             })
#         elif line.startswith("-"):
#             content_blocks.append({
#                 "type": "bulletList",
#                 "content": [{
#                     "type": "listItem",
#                     "content": [{
#                         "type": "paragraph",
#                         "content": [{"type": "text", "text": line[1:].strip()}]
#                     }]
#                 }]
#             })
#         elif "http" in line:
#             text_part = line.split("http")[0].strip()
#             url_part = line[line.find("http"):].strip()
#             content_blocks.append({
#                 "type": "paragraph",
#                 "content": [
#                     {"type": "text", "text": text_part + " " if text_part else ""},
#                     {"type": "text", "text": url_part, "marks": [{"type": "link", "attrs": {"href": url_part}}]}
#                 ]
#             })
#         elif line:
#             content_blocks.append({
#                 "type": "paragraph",
#                 "content": [{"type": "text", "text": line}]
#             })

#     return {
#         "type": "doc",
#         "version": 1,
#         "content": content_blocks
#     }

# # Function to create story
# def create_jira_story(email, api_token, project_key, jira_domain, summary, raw_description):
#     url = f"https://{jira_domain}.atlassian.net/rest/api/3/issue"
#     headers = {
#         "Accept": "application/json",
#         "Content-Type": "application/json"
#     }

#     description_adf = format_adf_description(raw_description)

#     payload = json.dumps({
#         "fields": {
#             "project": {"key": project_key},
#             "summary": summary,
#             "description": description_adf,
#             "issuetype": {"name": "Story"}
#         }
#     })

#     response = requests.post(
#         url,
#         data=payload,
#         headers=headers,
#         auth=HTTPBasicAuth(email, api_token)
#     )

#     if response.status_code == 201:
#         print(f"Created story: {summary}")
#         return response.json()["key"]
#     else:
#         print(f"Failed to create story: {response.status_code}")
#         print(response.text)
#         return None

# # Now call the function with real values
# sample_description = """
# Title: KYC Verification
# The system must validate PAN and Aadhaar using NSDL API.
# - Integrate with UIDAI endpoint
# - Log verification status
# More: https://nsdl.co.in
# """

# create_jira_story(
#     email="analystbarclays@gmail.com",
#     api_token="ATATT3xFfGF0lTjqI9D5Ia97iEMEJdY3zNXaLxqJZKJZ6SsrRHC77v4WLKjLF3lFUuMhJghHoB9fHRmTH3eYegEE3aebS9rWAlyLzxkysD0GYkYtXobLPqYN7BmpRznt8GCo0Oqg5U3F4JhdJy9nX1vt2HNmMTPUSa8AUjvO-w4_v4H5Rd1Xn2Q=77CB1E06",
#     project_key="SCRUM",
#     jira_domain="analystbarclays",
#     summary="KYC API Integration Requirement",
#     raw_description=sample_description
# )

import requests
from requests.auth import HTTPBasicAuth
import json
from firebase_admin import firestore , credentials
import firebase_admin

# from firebase_admin import firestore
# from firebase.firebase_init import db
# # Initialize Firebase with your service account key
# cred = credentials.Certificate(r"..\firebase\firebase-admin-key.json")
# firebase_admin.initialize_app(cred)

# Firestore client
# db = firestore.client()

cred = credentials.Certificate("firebase/firebase-admin-key.json")  # Replace with the correct path
firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()

# Define ADF formatter first
def format_adf_description(description_text):
    print("Formatting description...")
    lines = description_text.strip().split('\n')
    content_blocks = []

    for line in lines:
        line = line.strip()
        print(f"Processing line: {line}")

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

# Function to create story in Jira
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

    try:
        response = requests.post(
            url,
            data=payload,
            headers=headers,
            auth=HTTPBasicAuth(email, api_token)
        )

        print(f"Jira response status code: {response.status_code}")
        print(f"Response content: {response.text}")

        if response.status_code == 201:
            print(f"Created story: {summary}")
            return response.json()["key"]
        else:
            print(f"Failed to create story: {response.status_code}")
            print(response.text)
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error while creating Jira story: {e}")
        return None


# Function to loop through all projects and their requirements
def export_requirements_to_jira(email, api_token, jira_domain):
    print("Exporting requirements to Jira...")
    
    # Get all projects in Firebase
    projects_ref = db.collection('projects')
    projects = projects_ref.stream()
    
    for project in projects:
        project_name = project  # The project name in Firebase
        project_id = project_name  # The project name in Jira

        print(f"Processing project: {project_name}")

        # Get the 'extracted_requirements' collection for this project
        requirements_ref = db.collection('projects').document(project_name).collection('extracted_requirements')
        requirements = requirements_ref.stream()

        # Loop through all requirements in the project
        for requirement_doc in requirements:
            requirement_data = requirement_doc.to_dict()
            print(f"Processing requirement: {requirement_data['id']}")

            # Map the Firebase document to the Jira issue fields
            requirement = {
                "id": requirement_data["id"],
                "category": requirement_data.get("category", "Uncategorized"),
                "priority": requirement_data["priority"],
                "requirement_text": requirement_data["requirement_text"],
                "source": requirement_data["source"],
                "status": requirement_data["status"],
                "timestamp": requirement_data["timestamp"]
            }

            # Create the Jira story for each requirement
            create_jira_story(
                email=email,
                api_token=api_token,
                project_key=project_id,  # The project key is the project name
                jira_domain=jira_domain,
                summary=requirement["requirement_text"],  # The requirement text as the summary
                raw_description=f"Category: {requirement['category']}\nSource: {requirement['source']}\nStatus: {requirement['status']}"
            )

# Run the export function with your credentials
export_requirements_to_jira(
    email="analystbarclays@gmail.com",
    api_token="ATATT3xFfGF0orRftrOthxYV5CkTS1-68CaIuPI7TqCashx1CP9ulKkZu9L3ohYUv3r2p-4EC2VGBfUcg1aElamlyMeLtvCg4u36AeKGF3yGTq44iJd2d52BY2OPQhVtLzF_iEXXyffvD-kF0aWXV5yO2UC-ULAHC3kft1UwZItswbJ62JFABxE=703851F4",
    jira_domain="analystbarclays"
)