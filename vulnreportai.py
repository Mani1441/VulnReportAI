from groq import Groq
import json
import os
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()

# Connect to Groq AI using your API key
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_vapt_report(vuln_name, vuln_type, url, method,
                          request_data, response_data, steps, context=""):
    """Send vulnerability details to AI and get professional VAPT report"""

    prompt = f"""You are a senior penetration tester with 10 years experience.
Generate a professional VAPT finding report for the vulnerability below.
Return ONLY valid JSON. No markdown. No backticks. No explanation. Just JSON.

VULNERABILITY DETAILS:
Name: {vuln_name}
Type: {vuln_type}
Affected URL: {url}
HTTP Method: {method}
HTTP Request: {request_data}
Server Response: {response_data}
Steps to Reproduce: {steps}
Additional Context: {context}

Return a JSON object with EXACTLY these fields:
{{
  "title": "Professional finding title",
  "severity": "Critical or High or Medium or Low or Informational",
  "cvss_score": "Numeric score like 9.8 or 7.5",
  "cvss_vector": "Full CVSS:3.1/AV:... vector, then explain each part on new line",
  "owasp_category": "e.g. A03:2021 - Injection",
  "cwe_id": "e.g. CWE-89",
  "affected_component": "Specific component or endpoint name",
  "executive_summary": "2-3 non-technical sentences for management",
  "description": "Technical explanation of root cause",
  "business_impact": "Specific business risks: data loss, compliance, financial",
  "proof_of_concept": "Exact reproduction steps based on evidence provided",
  "remediation_immediate": "Quick fix that can be done right now",
  "remediation_longterm": "Proper code-level fix with example",
  "references": "3 references with full URLs: OWASP, CWE, one more"
}}"""

    # Send to Groq AI and get response
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1500
    )

    raw = response.choices[0].message.content
    clean = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(clean)


def display_report(report):
    """Print the report nicely in terminal"""
    print("\n" + "=" * 65)
    print("          VAPT FINDING REPORT — VulnReportAI")
    print("=" * 65)
    print(f"  TITLE     : {report.get('title','N/A')}")
    print(f"  SEVERITY  : {report.get('severity','N/A')}")
    print(f"  CVSS SCORE: {report.get('cvss_score','N/A')}")
    print(f"  OWASP     : {report.get('owasp_category','N/A')}")
    print(f"  CWE       : {report.get('cwe_id','N/A')}")
    print(f"  COMPONENT : {report.get('affected_component','N/A')}")
    print("-" * 65)
    print(f"\n[EXECUTIVE SUMMARY]\n{report.get('executive_summary','N/A')}")
    print(f"\n[DESCRIPTION]\n{report.get('description','N/A')}")
    print(f"\n[BUSINESS IMPACT]\n{report.get('business_impact','N/A')}")
    print(f"\n[CVSS VECTOR]\n{report.get('cvss_vector','N/A')}")
    print(f"\n[PROOF OF CONCEPT]\n{report.get('proof_of_concept','N/A')}")
    print(f"\n[REMEDIATION — IMMEDIATE]\n{report.get('remediation_immediate','N/A')}")
    print(f"\n[REMEDIATION — LONG TERM]\n{report.get('remediation_longterm','N/A')}")
    print(f"\n[REFERENCES]\n{report.get('references','N/A')}")
    print("=" * 65)


def save_report(report, filename):
    """Save report as JSON file in reports folder"""
    os.makedirs("reports", exist_ok=True)
    filepath = f"reports/{filename}.json"
    with open(filepath, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n  Saved to: {filepath}")


if __name__ == "__main__":
    print("\n" + "=" * 65)
    print("   VulnReportAI — AI-Powered VAPT Report Generator")
    print("   Powered by Groq AI | github.com/Mani1441")
    print("=" * 65)
    print("\nAnswer these questions (press Enter after each):\n")

    vuln_name    = input("1. Vulnerability name: ")
    vuln_type    = input("2. Type (SQLi / XSS / IDOR etc): ")
    url          = input("3. Affected URL: ")
    method       = input("4. HTTP Method (GET/POST/PUT/DELETE): ")
    request_data = input("5. Paste HTTP request (one line): ")
    response_data= input("6. Key part of server response: ")
    steps        = input("7. Steps to reproduce: ")
    context      = input("8. Extra context (press Enter to skip): ")

    print("\n  Generating your report... (5-10 seconds)\n")

    try:
        report = generate_vapt_report(
            vuln_name, vuln_type, url, method,
            request_data, response_data, steps, context
        )
        display_report(report)

        save = input("\nSave this report? (y/n): ")
        if save.lower() == "y":
            fname = vuln_name.lower().replace(" ","_")[:30]
            save_report(report, fname)

    except json.JSONDecodeError:
        print("  Error: AI returned unexpected format. Try again.")
    except Exception as e:
        print(f"  Error: {e}")