from openai import OpenAI
from kyc_matching import verify_kyc_kyb
import json
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def kyc_llm_agent(row):
    rule_passed, rule_reason = verify_kyc_kyb(row)

    prompt = f"""
You are a bank KYC/KYB verification agent.

Customer data:
{row.to_dict()}

Rule-based validation:
Passed: {rule_passed}
Reason: {rule_reason}

Decide final KYC status (Verified or Failed)
and explain briefly.

Return ONLY valid JSON:
{{"kyc_status": "...", "reason": "..."}}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return json.loads(response.choices[0].message.content)
