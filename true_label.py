import pandas as pd

df = pd.read_csv("data/labeled_dataset.csv")

def generate_true_label(row):

    amount = row["transaction_amount"]
    freq = row["transaction_frequency"]
    country = row["receiver_country"]

    high_risk_countries = [
        "Nigeria","Iran","North Korea","Syria",
        "Afghanistan","Somalia","Yemen"
    ]

    if amount > 300000:
        return "High"

    if country in high_risk_countries and amount > 100000:
        return "High"

    if freq == "irregular" and amount > 150000:
        return "High"

    if amount > 100000:
        return "Medium"

    if freq == "irregular":
        return "Medium"

    return "Low"

df["true_label"] = df.apply(generate_true_label, axis=1)

df.to_csv("data/compliance_with_true_labels.csv", index=False)

print("True labels generated successfully.")