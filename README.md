# ⚖️ ClaimsAdvisor AI | Premium Tax Auditor

**ClaimsAdvisor AI** is an advanced, AI-driven tax auditing platform designed specifically for salaried individuals in India. It leverages a multi-agent orchestration framework to parse, research, and audit tax claims with high precision, ensuring compliance with the latest Financial Year tax regulations.

---

## 🌟 Key Features

- **🧠 Multi-Agent Orchestration**: Powered by **CrewAI**, the system employs specialized agents for information extraction, tax policy research, and final auditing.
- **📄 High-Precision OCR**: Utilizes **LlamaParse** to convert complex financial documents (PDFs, Images, HTML) into structured Markdown while preserving tables and layouts.
- **🛡️ Privacy-First Design**: Built-in logic to identify and mask Personal Identifiable Information (PII) like PAN, Aadhaar, and names before processing.
- **🏛️ Indian Tax Expertise**: Supports both **Old and New Tax Regimes** and performs real-time research on current HRA, LTA, and Section 80C/80D policies.
- **📊 Interactive Analytics**: Real-time dashboard featuring:
  - **Audit Distribution Pie Charts**
  - **Executive Summaries**
  - **Detailed Status Tracking** (Valid, Rejected, or Review Needed)
- **📥 Exportable Reports**: Download structured CSV audit reports for your records.

---

## 🛠️ Tech Stack

- **Core Framework**: [CrewAI](https://www.crewai.com/) (Multi-Agent Workflows)
- **Frontend**: [Streamlit](https://streamlit.io/)
- **Document Parsing**: [LlamaParse](https://cloud.llamaindex.ai/)
- **Large Language Model**: [Groq](https://groq.com/) (Llama-3.3-70b-versatile)
- **Real-time Search**: [Serper.dev](https://serper.dev/) (Brave Search)
- **Package Management**: [uv](https://github.com/astral-sh/uv)

---

## 🚀 Getting Started

### Prerequisites

- [Python 3.12+](https://www.python.org/)
- [uv](https://github.com/astral-sh/uv) installed on your system.
- API Keys for:
  - **Groq** (LLM)
  - **LlamaCloud** (OCR)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-repo/ClaimsAdvisor.git
   cd ClaimsAdvisor/claimsadvisor
   ```

2. **Configure Environment Variables**:
   Create a `.env` file in the `claimsadvisor/src` directory (or use the one in root if configured) and add your keys:
   ```env
   GROQ_API_KEY=your_groq_key
   LLAMA_CLOUD_API_KEY=your_llamaparse_key
   ```

3. **Run the Application**:
   ```bash
   uv run streamlit run app.py
   ```

---

## 📁 Project Structure

```text
claimsadvisor/
├── app.py              # Main Streamlit Application
├── src/
│   ├── crew.py         # CrewAI Agent & Task Definitions
│   ├── parser.py       # LlamaParse OCR Logic
│   ├── models.py       # Pydantic Data Models
│   └── config/         # YAML configurations for Agents & Tasks
├── .env                # API Keys (Git ignored)
└── pyproject.toml      # Dependency Management
```

---

## 📝 Usage

1. **Set Profile**: Input your Monthly Basic Salary and City Type in the sidebar to calibrate HRA eligibility logic.
2. **Choose Regime**: Select between Old and New Tax Regimes.
3. **Upload Documents**: Drop your tax receipts, bills, or investment proofs.
4. **Audit**: The AI will extract data, verify it against FY 2025-26 rules, and provide a detailed verdict.

---

## ⚠️ Disclaimer

*This tool provides basic tax awareness and preliminary audit guidance. It is not a substitute for professional tax advice or official tax filing services. Always consult with a certified tax professional before making final tax decisions.*

---
