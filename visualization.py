import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix

# load dataset
df = pd.read_csv("data/compliance_with_true_labels.csv")

y_true = df["true_label"]
y_pred = df["aml_risk"]

# -------------------------
# Confusion Matrix
# -------------------------
cm = confusion_matrix(y_true, y_pred)

plt.figure(figsize=(6,5))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=["Low","Medium","High"],
            yticklabels=["Low","Medium","High"])

plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("AML Risk Confusion Matrix")

plt.savefig("confusion_matrix.png")
plt.show()

# -------------------------
# Precision / Recall / F1
# -------------------------
report = classification_report(y_true, y_pred, output_dict=True)

metrics_df = pd.DataFrame(report).transpose().iloc[:3]

metrics_df[["precision","recall","f1-score"]].plot(
    kind="bar",
    figsize=(8,5)
)

plt.title("AML Classification Performance Metrics")
plt.ylabel("Score")
plt.xticks(rotation=0)

plt.savefig("metrics_bar_chart.png")
plt.show()

# -------------------------
# Class Distribution
# -------------------------
plt.figure(figsize=(6,4))
sns.countplot(x=y_true)

plt.title("True Label Distribution")
plt.xlabel("AML Risk Level")
plt.ylabel("Count")

plt.savefig("class_distribution.png")
plt.show()

print("Metric images generated successfully.")