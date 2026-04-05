import json
import re
from .llm_client import llm_call

def kyc_matching_agent(extraction_result):

    prompt = f"""
You are a KYC decision agent.

Risk Flag: {extraction_result['risk_flag']}

Determine final KYC status:
Approved / Review / Rejected

Return ONLY JSON:
{{"kyc_status":"...","reason":"short reason"}}
"""

    raw_output = llm_call(prompt)

    json_match = re.search(r"\{.*\}", raw_output, re.DOTALL)

    if json_match:
        try:
            return json.loads(json_match.group())
        except:
            return {"kyc_status": "Unknown", "reason": "Invalid JSON"}
    else:
        return {"kyc_status": "Unknown", "reason": "No JSON returned"}


