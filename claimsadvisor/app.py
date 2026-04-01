import streamlit as st
import re
import os
import tempfile
import pandas as pd
import numpy as np
# Compatibility patch for NumPy 2.0+
if not hasattr(np, "bool8"): np.bool8 = np.bool_
if not hasattr(np, "unicode_"): np.unicode_ = np.str_
if not hasattr(np, "int0"): np.int0 = np.int64
if not hasattr(np, "uint0"): np.uint0 = np.uint64
import plotly.express as px
from src.parser import parse_document
from src.crew import ClaimsAuditor
from src.models import FinalAuditReport, ExtractedData
import logging
import time


def mask_pii(text: str) -> str:
    """
    Masks common PII patterns in text:
    - PAN numbers (e.g., ABCDE1234F -> AB***234F)
    - Aadhaar numbers (e.g., 1234 5678 9012 -> XXXX XXXX 9012)
    - Phone numbers (10-digit Indian mobile)
    - Email addresses
    - Bank account numbers (long digit sequences)
    """
    # PAN number: 5 letters, 4 digits, 1 letter
    text = re.sub(
        r'\b([A-Z]{2})[A-Z]{3}(\d{3})(\d)([A-Z])\b',
        r'\1***\2*\4',
        text
    )

    # Aadhaar: 4 4 4 digit groups
    text = re.sub(
        r'\b\d{4}[\s-]\d{4}[\s-](\d{4})\b',
        r'XXXX XXXX \1',
        text
    )
    # Aadhaar: 12 consecutive digits
    text = re.sub(
        r'\b\d{8}(\d{4})\b',
        r'XXXXXXXX\1',
        text
    )

    # Indian mobile: +91 or 0 prefix optional, then 10 digits
    text = re.sub(
        r'(\+91[\s-]?|0)?([6-9]\d)(\d{4})(\d{4})\b',
        r'\1\2****\4',
        text
    )

    # Email addresses
    text = re.sub(
        r'([a-zA-Z0-9._%+-])[a-zA-Z0-9._%+-]*(@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
        r'\1****\2',
        text
    )

    # Bank account numbers (sequences of 9-18 digits)
    text = re.sub(
        r'\b(\d{4})\d{5,10}(\d{4})\b',
        r'\1*****\2',
        text
    )

    # Names following common prefixes (case-insensitive)
    # Matches "Name: John Doe", "Employee Name - Jane", "Mr. Smith", etc.
    prefixes = r'(?:Name:|Employee Name|Patient Name|Mr\.|Mrs\.|Ms\.|Shri|Smt\.|Landlord Name|Doctor Name|Payee)'
    def replace_name(m):
        prefix = m.group(1)
        sep = m.group(2)
        name = m.group(3).strip()
        if not name:
            return m.group(0)
        
        parts = name.split()
        if len(parts) > 1:
            masked = f"{parts[0][0]}*** {parts[-1]}"
        else:
            masked = f"{name[0]}***"
        
        return f"{prefix}{sep}{masked}"

    # Refined regex to stop at common delimiters like comma or double space or newline
    text = re.sub(
        rf'\b({prefixes})(\s*[:\-\s]\s*)([a-zA-Z\.\-\s]{{2,}}?)(?=\n|\r|  |,|\t|$)',
        replace_name,
        text,
        flags=re.IGNORECASE
    )

    return text


# --- Page Configuration ---
st.set_page_config(
    page_title="ClaimsAdvisor AI | Premium Tax Auditor",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom Styling ---
st.markdown("""
<style>
    /* Global Font Scaling */
    html {
        font-size: 0.95rem;
    }

    /* Gradient Background */
    .stApp {
        background: linear-gradient(135deg, #0e1117 0%, #1a1c23 100%);
        color: #e0e0e0;
    }
    
    /* Premium Sidebar */
    [data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    
    /* Custom Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3.2em;
        background: linear-gradient(90deg, #ff4b4b 0%, #ff7676 100%);
        color: white;
        font-weight: 700;
        font-size: 0.9rem;
        border: none;
        transition: all 0.4s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(255, 75, 75, 0.4);
        background: linear-gradient(90deg, #ff3333 0%, #ff5c5c 100%);
    }
    
    /* Metric Cards */
    .metric-container {
        display: flex;
        justify-content: space-between;
        gap: 15px;
    }
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        flex: 1;
        text-align: center;
        transition: 0.3s;
    }
    .metric-card:hover {
        border-color: #ff4b4b;
        background: rgba(255, 255, 255, 0.08);
    }
    .metric-card h3 {
        font-size: 0.9rem !important;
        margin-bottom: 5px;
    }
    .metric-card h2 {
        font-size: 1.4rem !important;
    }
    
    /* Audit Summary Box */
    .audit-summary {
        font-size: 0.95em;
        line-height: 1.6;
        color: #d1d5db;
        background: rgba(38, 39, 48, 0.6);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #464b5d;
        border-left: 6px solid #ff4b4b;
        margin: 15px 0;
    }
    
    /* Heading Colors & Scaling */
    h1 { font-size: 1.8rem !important; color: #ffffff !important; font-weight: 800 !important; }
    h2 { font-size: 1.4rem !important; color: #ffffff !important; font-weight: 700 !important; }
    h3 { font-size: 1.1rem !important; color: #ffffff !important; font-weight: 700 !important; }
    h4 { font-size: 1.0rem !important; color: #ffffff !important; font-weight: 600 !important; }
    h5 { font-size: 0.9rem !important; color: #ffffff !important; font-weight: 600 !important; }
    
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        font-size: 0.85rem;
    }

    /* Small Adjustments for Streamlit Defaults */
    p, li {
        font-size: 0.9rem;
    }
    
    .stMarkdown div p {
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>⚖️</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; margin-top: -20px;'>ClaimsAdvisor</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 0.75em; color: #888;'>For Salaried Individuals</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("### 🏛️ Tax Settings")
    tax_regime = st.sidebar.radio("Select Tax Regime", ["Old Tax Regime", "New Tax Regime"])
    
    st.markdown("---")
    st.markdown("### 📊 Income Profile (Optional)")
    
    # Initialize defaults
    basic_salary = 0
    monthly_hra = 0
    city_type = "Non-Metro"
    is_renting = False

    with st.expander("Provide Details for HRA Audit"):
        st.write("Enter your monthly income details for precise HRA/eligibility auditing.")
        basic_salary = st.number_input("Monthly Basic Salary (₹)", min_value=0, value=0, step=1000)
        monthly_hra = st.number_input("Monthly HRA Received (₹)", min_value=0, value=0, step=1000)
        city_type = st.selectbox("City Type", ["Metro (Bengaluru, Mumbai, Delhi, Kolkata, Chennai)", "Non-Metro"])
        is_renting = st.checkbox("I live in a rented house", value=True)
    
    # Defaults if expander is not interacted with or values are 0
    # (Streamlit keeps the variables in session state/scope)
    
    st.markdown("---")
    st.markdown("### 📤 Upload Center")
    uploaded_files = st.file_uploader("Drop your documents here", type=["pdf", "html", "png", "jpg", "jpeg", "docx"], accept_multiple_files=True)
    


    st.markdown("---")
    if st.button("🔄 Restart Process"):
        st.session_state.clear()
        st.rerun()

# --- Main Logic ---
st.markdown("# AI-Driven Claims Advisor")
st.markdown("### `Salaried Employees Only` • `Privacy First` • `Awareness`")
st.markdown("##### We give basic tax awareness to improve claim decisions, not full tax filing.")
st.write("")

st.info("🛡️ **Privacy Guard:** This tool is designed to mask or ignore Personal Identifiable Information (PII) like PAN, Aadhaar, and Names during processing.")

st.warning("⚠️ **Note:** Claim eligibility depends on your exact income (e.g., HRA). This tool provides general guidance on whether an expense type is valid for a claim.")
st.write("")

# Determine content to process
has_content = False

if uploaded_files:
    has_content = True
elif "sample_content" in st.session_state:
    has_content = True

if not has_content:
    st.markdown("""
    <div style="background: rgba(255,255,255,0.03); padding: 40px; border-radius: 20px; border: 1px dashed rgba(255,255,255,0.2); text-align: center;">
        <h2 style="color: #666 !important;">Start Your Audit</h2>
        <p style="color: #999;">Upload a file or use the sample in the sidebar to begin the AI-powered verification process.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("#### 🧠 Llama-3.1 Powered\nDeep reasoning for complex tax policy interpretation.")
    with c2:
        st.markdown("#### 🔍 Real-time Search\nAgents verify current FY 2025-26 rules dynamically.")
    with c3:
        st.markdown("#### 📄 Multi-Format\nSupports PDFs, HTML, Images, and Word docs.")

else:
    # Process the file
    current_identifier = ""
    if uploaded_files:
        current_identifier = ", ".join([f.name for f in uploaded_files]) + f" | {tax_regime}"
    elif "sample_content" in st.session_state:
        current_identifier = st.session_state.sample_name + f" | {tax_regime}"

    if "audit_report" not in st.session_state or ("last_identifier" in st.session_state and st.session_state.last_identifier != current_identifier):
        with st.status("🚀 Processing Claims...", expanded=True) as status:
            try:
                st.session_state.last_identifier = current_identifier
                st.write("🔍 **Phase 1: OCR Extraction**...")
                
                combined_text = ""
                
                if uploaded_files:
                    for uf in uploaded_files:
                        suffix = f".{uf.name.split('.')[-1]}"
                        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                            tmp_file.write(uf.getvalue())
                            tmp_path = tmp_file.name
                        
                        text = parse_document(tmp_path)
                        if text:
                            combined_text += f"\n\n---\n## 📄 Document: `{uf.name}`\n\n" + text
                            
                        if os.path.exists(tmp_path):
                            os.unlink(tmp_path)
                            
                elif "sample_content" in st.session_state:
                    suffix = f".{st.session_state.sample_name.split('.')[-1]}"
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                        tmp_file.write(st.session_state.sample_content)
                        tmp_path = tmp_file.name
                        
                    combined_text = parse_document(tmp_path)
                    
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
                
                if not combined_text:
                    st.error("Text extraction failed or no text found.")
                    st.stop()
                
                # 3. Kickoff Crew
                st.write("🤖 **Phase 2: Multi-Agent Audit** (Researching & Validating)...")
                
                # Check for basic financial keywords as a simple guardrail before processing
                financial_keywords = ["bill", "invoice", "claim", "tax", "gst", "amount", "rupees", "payment", "received", "dated", "vendor"]
                if not any(kw in combined_text.lower() for kw in financial_keywords):
                    st.error("⚠️ The uploaded document doesn't seem to be a financial claim or bill. Please upload valid documents.")
                    st.stop()

                inputs = {
                    "extracted_text": combined_text,
                    "tax_regime": tax_regime,
                    "monthly_basic": basic_salary if basic_salary > 0 else "Not Provided",
                    "monthly_hra": monthly_hra if monthly_hra > 0 else "Not Provided",
                    "city_type": city_type,
                    "is_renting": is_renting
                }
                
                auditor = ClaimsAuditor()
                result = auditor.claimsresearchercrew().kickoff(inputs=inputs)
                
                # 4. Store result
                st.session_state.audit_report = result
                st.session_state.extracted_text = combined_text
                
                status.update(label="✅ Audit Complete!", state="complete", expanded=False)

            except Exception as e:
                status.update(label="❌ Error during processing", state="error")
                st.error(f"Error: {e}")
                st.stop()

    # --- Display Results ---
    if "audit_report" in st.session_state:
        report = st.session_state.audit_report
        
        if hasattr(report, 'pydantic') and report.pydantic:
            data = report.pydantic
            
            # --- Filter Claims ---
            # Filter out and exclude claims where section is "None" or category is "Review Needed"
            filtered_claims = [
                c for c in data.audited_claims 
                if c.section and str(c.section).lower() not in ["none", "n/a", "not provided"] 
                and c.category in ["Valid", "Rejected"]
            ]
            
            # --- Metrics ---
            col1, col2 = st.columns(2)
            
            # Recalculate total valid amount based on filtered claims
            current_total_valid = sum([c.amount for c in filtered_claims if c.category == 'Valid'])
            valid_count = len([c for c in filtered_claims if c.category == 'Valid'])
            rejected_count = len([c for c in filtered_claims if c.category == 'Rejected'])

            with col1:
                st.markdown(f'<div class="metric-card"><h3>Total Valid</h3><h2 style="color:#00ff88;">₹ {current_total_valid:,.2f}</h2></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="metric-card"><h3>Valid Claims</h3><h2>{valid_count}</h2></div>', unsafe_allow_html=True)

            # --- Chart and Summary ---
            st.write("")
            mid_left, mid_right = st.columns([1, 2])
            
            with mid_left:
                st.subheader("Audit Distribution")
                # Prepare data for pie chart based on filtered claims
                if filtered_claims:
                    counts = pd.Series([c.category for c in filtered_claims]).value_counts().reset_index()
                    counts.columns = ['Category', 'Count']
                    fig = px.pie(counts, values='Count', names='Category', 
                                 color='Category',
                                 color_discrete_map={'Valid': '#00ff88', 'Rejected': '#ff4b4b'},
                                 hole=0.6)
                    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No valid or rejected claims found with a specified section.")

            with mid_right:
                st.subheader("Executive Summary")
                # Mask PII in summary
                masked_summary = mask_pii(data.summary)
                st.markdown(f'<div class="audit-summary">{masked_summary}</div>', unsafe_allow_html=True)

            # --- Audited Claims Table ---
            st.subheader("📋 Detailed Audit Breakdown")
            # Filtered list, removing Date and Vendor
            claims_df = pd.DataFrame([
                {
                    "Description": mask_pii(c.description),
                    "Amount": f"₹ {c.amount:,.2f}",
                    "Section": c.section,
                    "Status": c.category,
                    "Reasoning": mask_pii(c.reasoning)
                } for c in filtered_claims
            ])
            
            st.dataframe(claims_df, use_container_width=True, hide_index=True)

            # --- Download ---
            st.write("")
            csv = claims_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Structured Report (CSV)",
                data=csv,
                file_name=f"audit_report_{time.strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
            )
        else:
            st.subheader("Audit Result (Raw Agent Output)")
            st.markdown(report.raw)

        # Final Footer or simplified log view can be added here if needed in the future
        pass

