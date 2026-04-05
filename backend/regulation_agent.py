import json
import re
from .llm_client import llm_call

def regulation_agent(kyc_result, aml_result):

    prompt = f"""
You are a compliance regulation decision agent.

KYC Status: {kyc_result['kyc_status']}
AML Risk: {aml_result['aml_risk']}

Make final decision:
Approve / Escalate / Reject

Return ONLY JSON:
{{"decision":"...","reason":"short reason"}}
"""

    raw_output = llm_call(prompt)

    json_match = re.search(r"\{.*\}", raw_output, re.DOTALL)

    if json_match:
        try:
            return json.loads(json_match.group())
        except:
            return {"decision": "Unknown", "reason": "Invalid JSON"}
    else:
        return {"decision": "Unknown", "reason": "No JSON returned"}


