import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


# -----------------------------
# LOAD DATASET
# -----------------------------
df = pd.read_csv("data/compliance_with_true_labels.csv")


# -----------------------------
# ENCODE CATEGORICAL FEATURES
# -----------------------------
le_freq = LabelEncoder()
le_country = LabelEncoder()

df["transaction_frequency"] = le_freq.fit_transform(df["transaction_frequency"])
df["receiver_country"] = le_country.fit_transform(df["receiver_country"])


# -----------------------------
# FEATURES AND TARGET
# -----------------------------
X = df[
[
    "transaction_amount",
    "transaction_frequency",
    "receiver_country"
]
]

y = df["true_label"]


# -----------------------------
# TRAIN TEST SPLIT
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)


# -----------------------------
# TRAIN MODEL
# -----------------------------
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    random_state=42
)

model.fit(X_train, y_train)


# -----------------------------
# PREDICTIONS
# -----------------------------
pred = model.predict(X_test)


# -----------------------------
# MODEL METRICS
# -----------------------------
print("\nAccuracy:", accuracy_score(y_test, pred))

print("\nClassification Report:\n")
print(classification_report(y_test, pred))


# -----------------------------
# CONFUSION MATRIX
# -----------------------------
cm = confusion_matrix(y_test, pred)

plt.figure(figsize=(6,5))

sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="Blues",
    xticklabels=model.classes_,
    yticklabels=model.classes_
)

plt.title("Confusion Matrix")
plt.xlabel("Predicted Label")
plt.ylabel("True Label")

plt.tight_layout()
plt.savefig("confusion_matrix.png")
plt.show()


# -----------------------------
# METRICS BAR CHART
# -----------------------------
report = classification_report(y_test, pred, output_dict=True)

report_df = pd.DataFrame(report).transpose()

metrics = report_df.loc[
["High","Medium","Low"],
["precision","recall","f1-score"]
]

metrics.plot(kind="bar", figsize=(8,5))

plt.title("Precision, Recall, F1-score by Class")
plt.ylabel("Score")
plt.xlabel("Risk Level")

plt.xticks(rotation=0)

plt.tight_layout()
plt.savefig("metrics_bar_chart.png")
plt.show()


# -----------------------------
# CLASS DISTRIBUTION
# -----------------------------
plt.figure(figsize=(6,4))

sns.countplot(x=df["true_label"], order=["Low","Medium","High"])

plt.title("Class Distribution")
plt.xlabel("AML Risk Level")
plt.ylabel("Count")

plt.tight_layout()
plt.savefig("class_distribution.png")
plt.show()


# -----------------------------
# FEATURE IMPORTANCE
# -----------------------------
importance = model.feature_importances_

importance_df = pd.DataFrame({
    "Feature": X.columns,
    "Importance": importance
}).sort_values(by="Importance", ascending=False)

plt.figure(figsize=(7,5))

sns.barplot(
    x="Importance",
    y="Feature",
    data=importance_df
)

plt.title("Feature Importance - RandomForestClassifier Model")

plt.tight_layout()
plt.savefig("feature_importance.png")
plt.show()


print("\nAll evaluation plots generated successfully.")