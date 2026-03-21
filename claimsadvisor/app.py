import streamlit as st
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
        height: 3.5em;
        background: linear-gradient(90deg, #ff4b4b 0%, #ff7676 100%);
        color: white;
        font-weight: 700;
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
        padding: 25px;
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
    
    /* Audit Summary Box */
    .audit-summary {
        font-size: 1.1em;
        line-height: 1.7;
        color: #d1d5db;
        background: rgba(38, 39, 48, 0.6);
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #464b5d;
        border-left: 6px solid #ff4b4b;
        margin: 20px 0;
    }
    
    /* Heading Colors */
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 800 !important;
    }
    
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>⚖️</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; margin-top: -20px;'>ClaimsAdvisor</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("### 📤 Upload Center")
    uploaded_file = st.file_uploader("Drop your documents here", type=["pdf", "html", "png", "jpg", "jpeg", "docx"])
    
    st.markdown("---")
    st.markdown("### 🧪 Quick Test")
    if st.button("Use Sample Document"):
        # Check if sample exists
        sample_path = "claimsadvisor/dummy_claim.html"
        if os.path.exists(sample_path):
            with open(sample_path, "rb") as f:
                st.session_state.sample_content = f.read()
                st.session_state.sample_name = "dummy_claim.html"
                st.info("Sample loaded. Click 'Process' to start.")
        else:
            st.error("Sample file not found.")

    st.markdown("---")
    if st.button("🔄 Clear & Restart"):
        st.session_state.clear()
        st.rerun()

# --- Main Logic ---
st.markdown("# AI-Driven Tax Claim Auditor")
st.markdown("### `Precision` • `Speed` • `Privacy`")
st.write("")

# Determine content to process
content_to_process = None
file_name = None

if uploaded_file:
    content_to_process = uploaded_file.getvalue()
    file_name = uploaded_file.name
elif "sample_content" in st.session_state:
    content_to_process = st.session_state.sample_content
    file_name = st.session_state.sample_name

if not content_to_process:
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
    if "audit_report" not in st.session_state or ("last_file" in st.session_state and st.session_state.last_file != file_name):
        with st.status("🚀 Processing Claims...", expanded=True) as status:
            try:
                # 1. Save content to temp path
                suffix = f".{file_name.split('.')[-1]}"
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                    tmp_file.write(content_to_process)
                    tmp_path = tmp_file.name

                st.session_state.last_file = file_name
                
                # 2. OCR Extraction
                st.write("🔍 **Phase 1: OCR Extraction**...")
                extracted_text = parse_document(tmp_path)
                
                if not extracted_text:
                    st.error("Text extraction failed.")
                    st.stop()
                
                # 3. Kickoff Crew
                st.write("🤖 **Phase 2: Multi-Agent Audit** (Researching & Validating)...")
                inputs = {"extracted_text": extracted_text}
                
                auditor = ClaimsAuditor()
                result = auditor.claimsresearchercrew().kickoff(inputs=inputs)
                
                # 4. Store result
                st.session_state.audit_report = result
                st.session_state.extracted_text = extracted_text
                
                # Cleanup
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                
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
            
            # --- Metrics ---
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f'<div class="metric-card"><h3>Total Valid</h3><h2 style="color:#00ff88;">₹ {data.total_valid_amount:,.2f}</h2></div>', unsafe_allow_html=True)
            with col2:
                valid_count = len([c for c in data.audited_claims if c.category == 'Valid'])
                st.markdown(f'<div class="metric-card"><h3>Valid Claims</h3><h2>{valid_count}</h2></div>', unsafe_allow_html=True)
            with col3:
                review_count = len([c for c in data.audited_claims if c.category == 'Review Needed'])
                st.markdown(f'<div class="metric-card"><h3>Needs Review</h3><h2 style="color:#ffcc00;">{review_count}</h2></div>', unsafe_allow_html=True)

            # --- Chart and Summary ---
            st.write("")
            mid_left, mid_right = st.columns([1, 2])
            
            with mid_left:
                st.subheader("Audit Distribution")
                # Prepare data for pie chart
                counts = pd.Series([c.category for c in data.audited_claims]).value_counts().reset_index()
                counts.columns = ['Category', 'Count']
                fig = px.pie(counts, values='Count', names='Category', 
                             color='Category',
                             color_discrete_map={'Valid': '#00ff88', 'Rejected': '#ff4b4b', 'Review Needed': '#ffcc00'},
                             hole=0.6)
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig, use_container_width=True)

            with mid_right:
                st.subheader("Executive Summary")
                st.markdown(f'<div class="audit-summary">{data.summary}</div>', unsafe_allow_html=True)

            # --- Audited Claims Table ---
            st.subheader("📋 Detailed Audit Breakdown")
            claims_df = pd.DataFrame([
                {
                    "Description": c.description,
                    "Amount": f"₹ {c.amount:,.2f}",
                    "Section": c.section,
                    "Status": c.category,
                    "Reasoning": c.reasoning
                } for c in data.audited_claims
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

        # Tabs for details
        tab1, tab2 = st.tabs(["📄 OCR Extracted Text", "🤖 Multi-Agent Logs"])
        with tab1:
            st.text_area("Markdown text extracted from document:", st.session_state.extracted_text, height=400)
        with tab2:
            st.info("Log visualization under development. Check terminal for real-time progress.")

