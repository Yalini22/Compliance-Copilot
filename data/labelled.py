import sys
import os
import pandas as pd

# allow importing backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.aml_engine import aml_batch_agent

# load dataset
df = pd.read_csv("data/transactiondata.csv")

rows = [row for _, row in df.iterrows()]

batch_size = 20
batches = [rows[i:i + batch_size] for i in range(0, len(rows), batch_size)]

results = []

for i, batch in enumerate(batches):

    batch_results = aml_batch_agent(batch)

    for j, row in enumerate(batch):

        if j < len(batch_results):
            r = batch_results[j]
        else:
            r = {
                "aml_risk": "Medium",
                "decision": "Monitor",
                "reason": "Automatic fallback due to incomplete response."
            }

        results.append(r["aml_risk"])

    print(f"Processed batch {i+1}/{len(batches)}")

# add labels to dataframe
df["aml_risk"] = results

# save labeled dataset
df.to_csv("data/labeled_dataset.csv", index=False)

print("Dataset labeled successfully.")