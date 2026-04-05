from .llm_client import llm_call

def report_agent(row, decision):

    prompt = f"""
Generate a short compliance explanation.

Customer Name: {row['customer_name']}
Final Decision: {decision['decision']}

Provide a concise explanation (2–3 lines).
"""

    return llm_call(prompt)



