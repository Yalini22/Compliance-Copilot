import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
import plotly.express as px
import time

from backend.main import process_transactions  
from backend.kyc_extraction import kyc_extraction_agent
from backend.kyc_matching import kyc_matching_agent
from backend.aml_engine import aml_llm_agent, aml_batch_agent
from concurrent.futures import ThreadPoolExecutor

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="Compliance Copilot",
    page_icon="🛡️",
    layout="wide"
)

# ---------------------------------------------------
# PREMIUM CSS (FINAL CLEAN VERSION)
# ---------------------------------------------------
st.markdown("""
<style>

/* Remove extra top padding */
.block-container {
    padding-top: 2rem;
}

/* Background */
.stApp {
    background-color: #F9FAFB;
}

/* Hero Title */
.hero-title {
    font-size: 64px;
    font-weight: 800;
    text-align: center;
    color: #111827;
    margin-bottom: 10px;
}

/* Subtitle */
.hero-subtitle {
    font-size: 22px;
    text-align: center;
    color: #4B5563;
    margin-bottom: 50px;
}

/* Section Title */
.section-title {
    font-size: 28px;
    font-weight: 700;
    color: #111827;
    margin-bottom: 20px;
}

/* Feature cards */
.feature-card {
    background: white;
    padding: 30px;
    border-radius: 18px;
    text-align: center;
    box-shadow: 0px 10px 30px rgba(0,0,0,0.05);
}
            
/* Main action button */
.stButton > button {
    background: linear-gradient(90deg, #6366F1, #8B5CF6);
    color: white;
    font-size: 18px;
    font-weight: 600;
    padding: 12px 30px;
    border-radius: 12px;
    border: none;
    width: 100%;
}

.stButton > button:hover {
    opacity: 0.9;
}

/* Feature card text fix */
.feature-card h3 {
    color: #111827 !important;
    font-size: 20px;
    font-weight: 700;
}

.feature-card p {
    color: #4B5563 !important;
    font-size: 15px;
}
/* Remove dark dataframe styling */
[data-testid="stDataFrame"] {
    background-color: white !important;
    color: #111827 !important;
}

/* Table header */
[data-testid="stDataFrame"] th {
    background-color: #F3F4F6 !important;
    color: #111827 !important;
    font-weight: 600 !important;
}

/* Table cells */
[data-testid="stDataFrame"] td {
    background-color: white !important;
    color: #111827 !important;
}        
/* Hide Streamlit's default uploaded file preview */
[data-testid="stFileUploaderFile"] {
    display: none !important;
}
/* Make Streamlit header white */
header[data-testid="stHeader"] {
    background-color: white !important;
}

/* Make toolbar text black */
div[data-testid="stToolbar"] * {
    color: #111827 !important;
}

/* Make the top right buttons black */
button[kind="header"] {
    color: #111827 !important;
}

/* Remove blue top line */
div[data-testid="stDecoration"] {
    background: white !important;
}
/* Remove dark gradient background completely */
div[data-testid="stFileUploader"] div[role="button"] {
    background: white !important;
    background-image: none !important;
    border: 2px dashed #D1D5DB !important;
    border-radius: 14px !important;
}

/* Make drag text black */
div[data-testid="stFileUploader"] div[role="button"] * {
    color: #111827 !important;
}

/* Clean browse button */
div[data-testid="stFileUploader"] button {
    background: white !important;
    color: #111827 !important;
    border: 1px solid #D1D5DB !important;
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# HERO SECTION
# ---------------------------------------------------
st.markdown("<div class='hero-title'>What will you analyze today?</div>", unsafe_allow_html=True)
st.markdown("<div class='hero-subtitle'>AI‑powered KYC & AML Compliance Intelligence Platform</div>", unsafe_allow_html=True)

# ---------------------------------------------------
# FEATURES
# ---------------------------------------------------
st.markdown("<div class='section-title'>A powerful compliance suite</div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-card">
        <h3>🧾 KYC Verification</h3>
        <p>Automated identity validation using AI-powered document and risk analysis.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <h3>⚖ AML Detection</h3>
        <p>Hybrid rule-based and LLM risk classification for financial transactions.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <h3>📊 Risk Dashboard</h3>
        <p>Real-time compliance decisions with explainable AI-generated reports.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# ---------------------------------------------------
# UPLOAD SECTION
# ---------------------------------------------------
st.markdown("<div class='section-title'>Upload Compliance Dataset</div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1,2,1])
with col2:
    uploaded_file = st.file_uploader("", type=["csv"])

    

    if uploaded_file is not None:
        st.markdown(
        f"<p style='color:#111827; font-weight:600; margin-top:10px;'>📄 {uploaded_file.name}</p>",
        unsafe_allow_html=True
       )

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------
# START BUTTON BELOW UPLOAD (CENTERED)
# ---------------------------------------------------
col1, col2, col3 = st.columns([1,2,1])
with col2:
    run = st.button("Start Compliance Analysis")

# ---------------------------------------------------
# PROCESSING LOGIC
# ---------------------------------------------------
if run and uploaded_file:

    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()

    # CHANGE THIS NUMBER ANYTIME
    records_to_run = 500

    df = df.head(records_to_run)

    # Convert dataframe rows to list
    rows = [row for _, row in df.iterrows()]
    total_records = len(rows)

    progress_bar = st.progress(0)
    status_text = st.empty()
    start_time = time.time()

    from concurrent.futures import ThreadPoolExecutor

    batch_size = 20
    max_workers = 8

    batches = [rows[i:i + batch_size] for i in range(0, total_records, batch_size)]

    results = []
    processed = 0

    def process_batch(batch):
        return aml_batch_agent(batch)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:

        batch_outputs = executor.map(process_batch, batches)

        for batch, batch_results in zip(batches, batch_outputs):

            for i, row in enumerate(batch):

                if i < len(batch_results):
                    r = batch_results[i]
                else:
                    r = {
                        "aml_risk": "Unknown",
                        "decision": "Monitor",
                        "reason": "LLM response missing for this transaction"
                    }
                # -------------------------------
                # ✅ ADD THIS BLOCK (MongoDB Storage)
                # -------------------------------

                customer_type = str(row["customer_type"])

                if customer_type == "Individual":
                    name = str(row["customer_name"]) if pd.notna(row["customer_name"]) else "Unknown"
                else:
                    name = str(row["company_name"]) if pd.notna(row["company_name"]) else "Unknown"


                kyc_data = {
                    "customer_id": str(row["customer_id"]),
                    "customer_type": customer_type,
                    "name": str(row["customer_name"]) if pd.notna(row["customer_name"]) else "Unknown",
                    "company_name": str(row["company_name"]) if pd.notna(row["company_name"]) else "Unknown",
                    "country": str(row["sender_country"])   # from CSV
                }

                txn_data = {
                    "customer_id": str(row["customer_id"]),
                    "transaction_amount": float(row["transaction_amount"]),
                    "receiver_country": str(row["receiver_country"])   # from CSV
               }

                # 🔥 THIS LINE STORES DATA IN MONGODB
                process_transaction(kyc_data, txn_data)

                results.append({
                    "Customer Type": row["customer_type"],
                    "Customer Name": row["customer_name"],
                    "Company Name": row["company_name"],
                    "Transaction Amount": row["transaction_amount"],
                    "AML Risk": r.get("aml_risk", "Unknown"),
                    "Final Decision": r.get("decision", "Monitor"),
                    "Explanation": r.get("reason", "No explanation")
                })

                processed += 1
            progress_bar.progress(processed / total_records)

            elapsed = time.time() - start_time
            speed = processed / elapsed if elapsed > 0 else 0

            status_text.text(
                f"Processed {processed}/{total_records} | Speed: {speed:.2f} records/sec"
            )

    output_df = pd.DataFrame(results)
    output_df["AML Risk"] = output_df["AML Risk"].replace("Unknown", "Medium")
    # ----------------------------
    # DASHBOARD
    # ----------------------------

    st.markdown(
        "<div class='section-title'>Compliance Analytics Dashboard</div>",
        unsafe_allow_html=True
    )

    import plotly.express as px

    col1, col2 = st.columns(2)

    with col1:

        risk_counts = output_df["AML Risk"].value_counts().reset_index()
        risk_counts.columns = ["Risk Level", "Count"]

        fig = px.bar(
            risk_counts,
            x="Risk Level",
            y="Count",
            title="AML Risk Distribution",
            color="Risk Level"
        )

        fig.update_layout(
            paper_bgcolor="white",
            plot_bgcolor="white",
            font=dict(color="#111827", size=14)
        )

        st.plotly_chart(fig, use_container_width=True)

        pie_fig = px.pie(
            risk_counts,
            names="Risk Level",
            values="Count",
            color_discrete_sequence=["#6366F1", "#8B5CF6", "#EC4899"]
        )

        st.plotly_chart(pie_fig, use_container_width=True)

    with col2:

        decision_counts = output_df["Final Decision"].value_counts().reset_index()
        decision_counts.columns = ["Decision", "Count"]

        fig2 = px.bar(
            decision_counts,
            x="Decision",
            y="Count",
            color="Decision",
            color_discrete_sequence=["#6366F1", "#10B981", "#EF4444"]
        )

        fig2.update_layout(
            paper_bgcolor="white",
            plot_bgcolor="white",
            font=dict(color="#111827", size=14),
        )

        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        "<div class='section-title'>Detailed Compliance Results</div>",
        unsafe_allow_html=True
    )

    st.dataframe(output_df, use_container_width=True)

    st.download_button(
        "Download Compliance Report",
        output_df.to_csv(index=False).encode("utf-8"),
        "Compliance_Report.csv"
    )
    