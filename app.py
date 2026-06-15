from flask import Flask, request, jsonify, send_from_directory
from groq import Groq
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()

    prompt = f"""You are a senior penetration tester with 10 years experience.
Generate a professional VAPT finding report for the vulnerability below.
Return ONLY valid JSON. No markdown. No backticks. No explanation. Just JSON.

Name: {data.get('name','')}
Type: {data.get('type','')}
URL: {data.get('url','')}
Method: {data.get('method','')}
HTTP Request: {data.get('request','')}
Server Response: {data.get('response','')}
Steps: {data.get('steps','')}
Context: {data.get('context','')}

Return JSON with these fields:
{{
  "title": "Professional finding title",
  "severity": "Critical or High or Medium or Low or Informational",
  "cvss_score": "e.g. 9.8",
  "cvss_vector": "Full CVSS:3.1 vector then explain each metric on new line",
  "owasp_category": "e.g. A03:2021 - Injection",
  "cwe_id": "e.g. CWE-89",
  "affected_component": "Specific component",
  "executive_summary": "2-3 non-technical sentences",
  "description": "Technical root cause explanation",
  "business_impact": "Specific business risks",
  "proof_of_concept": "Step by step reproduction",
  "remediation_immediate": "Quick fix",
  "remediation_longterm": "Code-level proper fix",
  "references": "3 references with full URLs"
}}"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1500
        )
        raw = response.choices[0].message.content
        clean = raw.replace("```json","").replace("```","").strip()
        report = json.loads(clean)
        return jsonify({"success": True, "report": report})

    except json.JSONDecodeError:
        return jsonify({"success": False,
                        "error": "AI returned unexpected format. Try again."}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    print("\n VulnReportAI Web UI starting...")
    print(" Open your browser: http://localhost:5000")
    print(" Press Ctrl+C to stop\n")
    app.run(debug=True, port=5000)