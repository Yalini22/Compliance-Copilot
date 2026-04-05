import json
import re
from .llm_client import llm_call

def kyc_extraction_agent(row):

    prompt = f"""
You are a KYC extraction agent.

Customer Name: {row['customer_name']}
Customer Type: {row['customer_type']}
Registration Status: {row['registration_status']}
PEP Status: {row['pep_status']}
Sender Country: {row['sender_country']}

Return ONLY JSON:
{{"risk_flag":"Yes/No","reason":"short reason"}}
"""

    raw_output = llm_call(prompt)

    json_match = re.search(r"\{.*\}", raw_output, re.DOTALL)

    if json_match:
        try:
            return json.loads(json_match.group())
        except:
            return {"risk_flag": "Unknown", "reason": "Invalid JSON"}
    else:
        return {"risk_flag": "Unknown", "reason": "No JSON returned"}



