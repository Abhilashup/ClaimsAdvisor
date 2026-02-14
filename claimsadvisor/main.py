import sys
import os
from src.parser import parse_document
from src.crew import ClaimsAuditor

def run(file_path: str):
    """
    1. Parse the document using OCR (LlamaParse)
    2. Pass the extracted text to the Crew
    """
    try:
        # Step 1: Extract text
        print(f"--- Starting OCR Process ---")
        extracted_text = parse_document(file_path)
        
        if not extracted_text:
            print("Error: No text extracted from the document.")
            return

        # Step 2: Kickoff Crew
        print(f"--- Starting Crew Negotiation ---")
        inputs = {
            "extracted_text": extracted_text
        }
        
        result = ClaimsAuditor().claimsresearchercrew().kickoff(inputs=inputs)
        
        print("\n--- Final Audit Result ---")
        print(result)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_document>")
    else:
        file_path = sys.argv[1]
        if os.path.exists(file_path):
            run(file_path)
        else:
            print(f"File not found: {file_path}")

