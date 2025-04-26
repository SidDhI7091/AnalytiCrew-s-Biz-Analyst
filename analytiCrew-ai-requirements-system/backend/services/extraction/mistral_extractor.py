import requests

def extract_with_mistral(text: str):
    """
    Sends parsed document content to the locally running Mistral model via Ollama
    and expects structured requirement extraction in categories like:
    functional, non_functional, security, regulatory, UI, etc.
    """

    prompt = f"""
You are a smart AI assistant for business analysts.

From the following document content, extract and categorize all types of requirements:
- Functional Requirements
- Non-Functional Requirements
- Regulatory Requirements
- Security Requirements
- UI Requirements
- Usability Requirements
- Any other types (if applicable)

Return the output in the following JSON format:
{{
  "functional": ["..."],
  "non_functional": ["..."],
  "regulatory": ["..."],
  "security": ["..."],
  "ui": ["..."],
  "usability": ["..."],
  "other": ["..."]
}}

Document content:
{text}
"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "mistral",
                "prompt": prompt,
                "stream": False
            },
            timeout = 90
        )
        print("Mistral Response Status:", response.status_code)
        print("Mistral Raw Response:", response.text)

        result = response.json().get("response", "")
        # WARNING: This assumes response is a JSON-formatted string
        try:
            parsed_result = eval(result.strip())  # Or use json.loads() if model returns valid JSON
        except Exception as e:
            print("Parsing error:", str(e))
            parsed_result = {"error": "Could not parse model response", "raw_output": result}

        return parsed_result

    except Exception as e:
        print("Exception in Mistral call:", str(e))
        return {"error": str(e)}