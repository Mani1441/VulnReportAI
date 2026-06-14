import anthropic
import json
import os
from dotenv import load_dotenv

# This loads your API key from the .env file
load_dotenv()

# This creates a connection to the Claude AI using your API key
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def generate_vapt_report(vuln_name, vuln_type, url, method,
                          request_data, response_data, steps, context=""):
    """
    This function sends vulnerability details to Claude AI
    and gets back a professional VAPT finding report
    """

    # This is the instruction we send to Claude
    prompt = f"""You are a senior penetration tester with 10 years of experience.
Generate a professional VAPT finding report for the vulnerability below.
Return ONLY valid JSON — no markdown, no explanation, no backticks, nothing else.

VULNERABILITY DETAILS:
Name: {vuln_name}
Type: {vuln_type}
Affected URL: {url}
HTTP Method: {method}
HTTP Request: {request_data}
Server Response: {response_data}
Steps to Reproduce: {steps}
Additional Context: {context}

Return JSON with EXACTLY these fields (all required):
{{
  "title": "Clear professional finding title",
  "severity": "Critical or High or Medium or Low or Informational",
  "cvss_score": "Numeric score like 9.8 or 7.5",
  "cvss_vector": "Full CVSS:3.1 vector string, then explain each metric on a new line",
  "owasp_category": "e.g. A03:2021 - Injection",
  "cwe_id": "e.g. CWE-89",
  "affected_component": "Name the specific component or endpoint",
  "executive_summary": "2-3 sentences in non-technical language for management",
  "description": "Technical explanation of the vulnerability and its root cause",
  "business_impact": "Specific risks: data breach, financial loss, compliance violations",
  "proof_of_concept": "Exact steps to reproduce with the evidence provided",
  "remediation_immediate": "Quick fix that can be done right now",
  "remediation_longterm": "Proper code-level fix with example if possible",
  "references": "3 references: OWASP link, CWE link, one more relevant resource"
}}"""

    # Send the prompt to Claude AI and get the response
    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )

    # Get the text response from Claude
    raw_response = message.content[0].text

    # Clean up any accidental markdown formatting
    clean_response = raw_response.replace("```json", "").replace("```", "").strip()

    # Convert the JSON text into a Python dictionary
    report = json.loads(clean_response)
    return report


def display_report(report):
    """This function prints the report nicely in the terminal"""
    print("\n")
    print("=" * 65)
    print("           VAPT FINDING REPORT — VulnReportAI")
    print("=" * 65)
    print(f"  TITLE     : {report.get('title', 'N/A')}")
    print(f"  SEVERITY  : {report.get('severity', 'N/A')}")
    print(f"  CVSS SCORE: {report.get('cvss_score', 'N/A')}")
    print(f"  OWASP     : {report.get('owasp_category', 'N/A')}")
    print(f"  CWE       : {report.get('cwe_id', 'N/A')}")
    print(f"  COMPONENT : {report.get('affected_component', 'N/A')}")
    print("-" * 65)
    print(f"\n[EXECUTIVE SUMMARY — For Management]\n{report.get('executive_summary', 'N/A')}")
    print(f"\n[TECHNICAL DESCRIPTION]\n{report.get('description', 'N/A')}")
    print(f"\n[BUSINESS IMPACT]\n{report.get('business_impact', 'N/A')}")
    print(f"\n[CVSS VECTOR BREAKDOWN]\n{report.get('cvss_vector', 'N/A')}")
    print(f"\n[PROOF OF CONCEPT]\n{report.get('proof_of_concept', 'N/A')}")
    print(f"\n[REMEDIATION — IMMEDIATE FIX]\n{report.get('remediation_immediate', 'N/A')}")
    print(f"\n[REMEDIATION — LONG TERM FIX]\n{report.get('remediation_longterm', 'N/A')}")
    print(f"\n[REFERENCES]\n{report.get('references', 'N/A')}")
    print("=" * 65)


def save_report_to_file(report, filename):
    """This function saves the report as a JSON file"""
    filepath = f"reports/{filename}.json"
    with open(filepath, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n  Report saved to: {filepath}")


# This is the main program that runs when you execute the file
if __name__ == "__main__":
    print("\n" + "=" * 65)
    print("   VulnReportAI — AI-Powered VAPT Report Generator")
    print("   Built by Manikanth Pattar | github.com/Mani1441")
    print("=" * 65)
    print("\nEnter the vulnerability details below:")
    print("(Press Enter after each answer)\n")

    # Collect vulnerability information from user
    vuln_name = input("1. Vulnerability name: ")
    vuln_type = input("2. Type (e.g. SQL Injection, XSS, IDOR): ")
    url = input("3. Affected URL: ")
    method = input("4. HTTP Method (GET/POST/PUT/DELETE): ")
    request_data = input("5. Paste the HTTP request (one line): ")
    response_data = input("6. Key part of server response: ")
    steps = input("7. Steps to reproduce (brief): ")
    context = input("8. Additional context (press Enter to skip): ")

    print("\n  Sending to Claude AI... generating your report...")
    print("  (This takes 10-15 seconds)\n")

    try:
        # Call the AI and get the report
        report = generate_vapt_report(
            vuln_name, vuln_type, url, method,
            request_data, response_data, steps, context
        )

        # Display the report in terminal
        display_report(report)

        # Ask if user wants to save the report
        save = input("\nSave this report to file? (y/n): ")
        if save.lower() == "y":
            filename = vuln_name.lower().replace(" ", "_")[:30]
            save_report_to_file(report, filename)
            print("  Done! Check the reports/ folder.")

    except json.JSONDecodeError:
        print("  Error: AI returned unexpected format. Try again.")
    except anthropic.AuthenticationError:
        print("  Error: Invalid API key. Check your .env file.")
    except Exception as e:
        print(f"  Error: {e}")

    print("\n  Thank you for using VulnReportAI!")