from flask import Flask, request, jsonify, send_from_directory
import anthropic
import json
import os
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()

# Create the Flask web app
app = Flask(__name__)

# Create Claude AI connection
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


# This route serves your index.html when someone visits http://localhost:5000
@app.route("/")
def home():
    return send_from_directory(".", "index.html")


# This route handles the "Generate Report" button click from your web UI
@app.route("/generate", methods=["POST"])
def generate():
    # Get the vulnerability data sent from the browser
    data = request.get_json()

    # Build the prompt for Claude AI
    prompt = f"""You are a senior penetration tester with 10 years of experience.
Generate a professional VAPT finding report for the vulnerability below.
Return ONLY valid JSON — no markdown, no backticks, nothing else.

VULNERABILITY DETAILS:
Name: {data.get('name', '')}
Type: {data.get('type', '')}
URL: {data.get('url', '')}
Method: {data.get('method', '')}
HTTP Request: {data.get('request', '')}
Server Response: {data.get('response', '')}
Steps to Reproduce: {data.get('steps', '')}
Additional Context: {data.get('context', '')}

Return JSON with EXACTLY these fields:
{{
  "title": "Professional finding title",
  "severity": "Critical or High or Medium or Low or Informational",
  "cvss_score": "e.g. 9.8",
  "cvss_vector": "Full CVSS:3.1 vector then explain each metric on new line",
  "owasp_category": "e.g. A03:2021 - Injection",
  "cwe_id": "e.g. CWE-89",
  "affected_component": "Specific component name",
  "executive_summary": "2-3 non-technical sentences for management",
  "description": "Technical root cause explanation",
  "business_impact": "Specific business risks",
  "proof_of_concept": "Step-by-step reproduction steps",
  "remediation_immediate": "Quick immediate fix",
  "remediation_longterm": "Proper long-term code-level fix",
  "references": "3 references with URLs"
}}"""

    try:
        # Call Claude AI
        message = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )

        # Get and clean the response
        raw = message.content[0].text
        clean = raw.replace("```json", "").replace("```", "").strip()
        report = json.loads(clean)

        # Send the report back to the browser
        return jsonify({"success": True, "report": report})

    except json.JSONDecodeError as e:
        return jsonify({"success": False, "error": "AI returned unexpected format. Try again."}), 500
    except anthropic.AuthenticationError:
        return jsonify({"success": False, "error": "Invalid API key. Check your .env file."}), 401
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# Start the web server when you run this file
if __name__ == "__main__":
    print("\n VulnReportAI Web UI is starting...")
    print(" Open your browser and go to: http://localhost:5000")
    print(" Press Ctrl+C to stop the server\n")
    app.run(debug=True, port=5000)