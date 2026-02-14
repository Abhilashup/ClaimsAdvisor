import os
from dotenv import load_dotenv
from llama_parse import LlamaParse

load_dotenv()

def parse_document(file_path: str) -> str:
    """
    Parses a document (PDF, Image, etc.) into markdown text using LlamaParse.
    """
    if not os.getenv("LLAMA_CLOUD_API_KEY"):
        raise ValueError("LLAMA_CLOUD_API_KEY not found in environment variables.")

    # Initialize LlamaParse
    parser = LlamaParse(
        result_type="markdown",  # "markdown" is usually best for LLMs
        verbose=True,
        language="en",
        num_workers=4
    )

    print(f"Parsing document: {file_path}...")
    
    # Load and parse the document
    documents = parser.load_data(file_path)
    
    # Combine all parsed pages/sections into one string
    extracted_text = "\n\n".join([doc.text for doc in documents])
    
    return extracted_text

if __name__ == "__main__":
    # Quick test if run directly
    test_file = "path/to/your/test_invoice.pdf"
    if os.path.exists(test_file):
        text = parse_document(test_file)
        print("--- Extracted Text Preview ---")
        print(text[:500])
    else:
        print(f"Test file not found at {test_file}. Please update the path in src/parser.py for testing.")
