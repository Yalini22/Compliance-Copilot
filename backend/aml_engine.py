import json
import re
from .llm_client import llm_call


# ---------------------------------------------------
# Single Transaction AML Agent
# ---------------------------------------------------
def aml_llm_agent(row):

    prompt = f"""
You are an AML compliance analyst.

Analyze the following transaction.

Transaction details:
Amount: {row['transaction_amount']}
Frequency: {row['transaction_frequency']}
Receiver Country: {row['receiver_country']}

Classify AML risk and explain clearly.

Return ONLY JSON in this format:

{{
"aml_risk": "Low/Medium/High",
"decision": "Approve/Monitor/Flag",
"reason": "1–2 sentence explanation of why the transaction has this risk level"
}}
"""

    try:
        raw_output = llm_call(prompt)

    except Exception as e:
        print("LLM call failed:", e)
        return {
            "aml_risk": "Unknown",
            "decision": "Monitor",
            "reason": "LLM request failed"
        }

    json_match = re.search(r"\{.*?\}", raw_output, re.DOTALL)

    if json_match:
        try:
            result = json.loads(json_match.group())

            result.setdefault("aml_risk", "Unknown")
            result.setdefault("decision", "Monitor")
            result.setdefault("reason", "No explanation provided")

            return result

        except Exception:
            pass

    return {
        "aml_risk": "Unknown",
        "decision": "Monitor",
        "reason": "Could not parse LLM response"
    }


# ---------------------------------------------------
# Batch AML Agent
# ---------------------------------------------------
def aml_batch_agent(batch_rows):

    transactions_text = ""

    for row in batch_rows:
        transactions_text += f"""
Customer Type: {row['customer_type']}
Customer Name: {row['customer_name']}
Transaction Amount: {row['transaction_amount']}
Transaction Frequency: {row['transaction_frequency']}
Receiver Country: {row['receiver_country']}
"""

    prompt = f"""
You are a senior Anti‑Money Laundering (AML) compliance analyst.

For each transaction, evaluate the following risk factors and assign a score:

1. Transaction Amount Risk
   - Low (<100k)
   - Medium (100k–300k)
   - High (>300k)

2. Transaction Frequency Risk
   - Regular → Low
   - Occasional → Medium
   - Irregular → High

3. Country Risk
   High‑risk jurisdictions include:
   Nigeria, Iran, North Korea, Syria, Afghanistan, Somalia, Yemen.

Risk scoring rules:

High Risk
- Very large transaction
- High‑risk country with large amount
- Irregular transaction behaviour with large amount

Medium Risk
- Moderately large transaction
- Irregular frequency
- Moderate risk patterns

Low Risk
- Normal transaction amount
- Regular behaviour
- Low‑risk country

Evaluate the transaction logically and then assign:

AML Risk → Low / Medium / High  
Decision → Approve / Monitor / Flag  

Provide a clear explanation.

Transactions:
{transactions_text}

Return ONLY JSON list in this format:

[
{{"aml_risk":"Low","decision":"Approve","reason":"Detailed explanation"}},
{{"aml_risk":"Medium","decision":"Monitor","reason":"Detailed explanation"}},
{{"aml_risk":"High","decision":"Flag","reason":"Detailed explanation"}}
]
"""

    MAX_RETRIES = 3

    for attempt in range(MAX_RETRIES):

        try:
            raw_output = llm_call(prompt)

            json_match = re.search(r"\[.*\]", raw_output, re.DOTALL)

            if not json_match:
                raise ValueError("JSON list not found")

            parsed_results = json.loads(json_match.group())

            # Ensure every row gets a result
            cleaned_results = []

            for i in range(len(batch_rows)):

                if i < len(parsed_results):
                    r = parsed_results[i]
                else:
                    r = {
                        "aml_risk": "Medium",
                        "decision": "Monitor",
                        "reason": "The transaction requires manual review due to incomplete automated risk analysis."
                    }

                reason = r.get("reason", "Transaction requires manual compliance review.")

                # remove "Transaction 1:", "Transaction 2:" etc if the model outputs it
                reason = re.sub(r"Transaction\s*\d+\s*:?\s*", "", reason, flags=re.IGNORECASE)

                cleaned_results.append({
                    "aml_risk": r.get("aml_risk", "Medium"),
                    "decision": r.get("decision", "Monitor"),
                    "reason": reason
                })
            return cleaned_results

        except Exception as e:
            print(f"Retry {attempt+1} failed:", e)

    # Final fallback
    fallback = []
    for _ in batch_rows:
        fallback.append({
            "aml_risk": "Medium",
            "decision": "Monitor",
            "reason": "Automated AML analysis could not complete successfully, therefore this transaction requires compliance review."
        })

    return fallback