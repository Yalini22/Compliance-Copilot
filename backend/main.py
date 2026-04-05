from backend.mongodb import kyc_collection, transaction_collection, results_collection

# -----------------------------
# AML LOGIC
# -----------------------------
def aml_prediction(transaction):
    amount = transaction["transaction_amount"]
    country = transaction["receiver_country"]

    high_risk_countries = ["Nigeria", "Iran", "North Korea"]

    if amount > 300000:
        return "High"

    if country in high_risk_countries and amount > 100000:
        return "High"

    if amount > 100000:
        return "Medium"

    return "Low"


def generate_explanation(risk):
    if risk == "High":
        return "High transaction risk due to amount or high-risk country."
    elif risk == "Medium":
        return "Moderate transaction value detected."
    return "Normal behavior."


def regulation_decision(risk):
    if risk == "High":
        return "Flag"
    elif risk == "Medium":
        return "Monitor"
    return "Approve"


# -----------------------------
# CORE PROCESS FUNCTION
# -----------------------------
def process_transactions(all_kyc_data, all_txn_data):
    
    # 🔥 CLEAR OLD DATA (IMPORTANT)
    transaction_collection.delete_many({})
    results_collection.delete_many({})

    # BATCH STORAGE
    transaction_batch = []
    results_batch = []

    for kyc_data, txn_data in zip(all_kyc_data, all_txn_data):

        customer_id = kyc_data["customer_id"]

        # STORE KYC (only once)
        if kyc_collection.count_documents({"customer_id": customer_id}) == 0:
            kyc_collection.insert_one(kyc_data)

        # AML LOGIC
        risk = aml_prediction(txn_data)
        explanation = generate_explanation(risk)
        decision = regulation_decision(risk)

        # ADD TO BATCH (instead of inserting one-by-one)
        transaction_batch.append(txn_data)

        results_batch.append({
            "customer_id": customer_id,
            "customer_name": kyc_data.get("name", "N/A"),
            "company_name": kyc_data.get("company_name", "N/A"),
            "aml_risk": risk,
            "explanation": explanation,
            "decision": decision
        })

    # 🔥 BULK INSERT (VERY FAST)
    if transaction_batch:
        transaction_collection.insert_many(transaction_batch)

    if results_batch:
        results_collection.insert_many(results_batch)

    return {
        "status": "success",
        "processed_records": len(results_batch)
    }


# -----------------------------
# INDEXING (RUN ONCE)
# -----------------------------
def setup_indexes():
    transaction_collection.create_index("customer_id")
    results_collection.create_index("customer_id")