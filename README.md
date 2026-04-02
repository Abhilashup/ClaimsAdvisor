# ClaimsAdvisor AI ⚖️

**A Premium AI-Powered Tax Auditor for Salaried Individuals**

ClaimsAdvisor AI is a sophisticated multi-agent system designed to help employees audit their tax claims against the latest Indian Income Tax laws for **FY 2025-26 (AY 2026-27)**. It provides precise guidance on claim validity for both the **Old** and **New** Tax Regimes.

---

## 🚀 Key Features

-   **Multi-Agent Intelligence**: Powered by **CrewAI** with three specialized agents:
    -   **Financial Data Extractor**: Converts raw documents into structured financial data.
    -   **Tax Policy Researcher**: Verifies real-time tax limits and rules for FY 2025-26.
    -   **Senior Tax Auditor**: Validates claims and provides detailed, regime-specific justifications.
-   **Advanced Document Parsing**: Uses **LlamaParse** to accurately extract text and tables from PDFs, DOCX, Images, and HTML.
-   **Regime-Specific Auditing**: Explicitly handles the differences between Old and New regimes, including:
    -   HRA eligibility (with updated Metro city definitions like Bengaluru, Pune, etc.).
    -   Section 80C and 80D limits.
    -   Meal coupon exemptions (up to ₹200/meal).
    -   Standard Deduction (₹75k for New, ₹50k for Old).
-   **Privacy First**: Built-in **PII Masking** to automatically redact sensitive information like PAN, Aadhaar, Phone numbers, and Bank Accounts.
-   **Executive Summary & Visuals**: Provides a high-level executive summary and an interactive distribution chart for quick insights.

---

## 🛠️ Tech Stack

-   **Backend**: Python, CrewAI
-   **Frontend**: Streamlit
-   **LLM**: Llama-3.3-70b-versatile (via Groq)
-   **OCR/Parsing**: LlamaParse
-   **Search**: Serper (Brave Search)
-   **Package Manager**: UV

---

## 🏗️ Installation & Setup

1.  **Clone the Repository**:
    ```bash
    git clone <your-repo-url>
    cd claimsadvisor
    ```

2.  **Environment Setup**:
    Ensure you have [uv](https://github.com/astral-sh/uv) installed. Create a `.env` file in `claimsadvisor/src` with the following keys:
    ```env
    GROQ_API_KEY=your_groq_key
    LLAMA_CLOUD_API_KEY=your_llama_parse_key
    ```

3.  **Install Dependencies**:
    ```bash
    uv pip install -r pyproject.toml
    ```

4.  **Run the Application**:
    ```bash
    uv run streamlit run app.py
    ```

---

## 📋 Usage Guide

1.  **Set Your Profile**: Select your Tax Regime (Old/New) and provide optional income details for precise HRA auditing.
2.  **Upload Documents**: Drop your bills, rent receipts, or investment proofs.
3.  **Start Audit**: Click 'Process' and watch the AI agents work in real-time.
4.  **Review & Download**: Examine the detailed breakdown and download the final audit as a structured CSV.

---

## 🔐 Privacy Note

This application is designed for **awareness only**. All Personal Identifiable Information (PII) is masked or ignored during processing. We do not store your documents permanently.

---

## 📜 Disclaimer

This tool provides general guidance based on AI interpretation of tax laws. It does not constitute professional tax advice. Always consult a qualified Chartered Accountant before filing your tax returns.
