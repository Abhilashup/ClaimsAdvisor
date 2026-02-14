import sys
import os
import logging
from src.parser import parse_document
from src.crew import ClaimsAuditor

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run(file_path: str):
    """
    1. Parse the document using OCR (LlamaParse)
    2. Pass the extracted text to the Crew
    3. Output structured results
    """
    try:
        # Step 1: Extract text
        logger.info(f"--- Starting OCR Process for {file_path} ---")
        extracted_text = parse_document(file_path)
        
        if not extracted_text:
            logger.error("No text could be extracted from the document.")
            return

        # Step 2: Kickoff Crew
        logger.info(f"--- Starting Crew Negotiation ---")
        inputs = {
            "extracted_text": extracted_text
        }
        
        # This will now return a Pydantic object if configured correctly in crew.py
        result = ClaimsAuditor().claimsresearchercrew().kickoff(inputs=inputs)
        
        # Access structured data from the result
        # CrewAI result.pydantic contains the actual model instance
        if hasattr(result, 'pydantic') and result.pydantic:
            report = result.pydantic
            logger.info("\n--- Final Audit Report ---")
            logger.info(f"Summary: {report.summary}")
            logger.info(f"Total Valid Amount: {report.total_valid_amount}")
            for claim in report.audited_claims:
                logger.info(f"Claim: {claim.description} | Status: {claim.category} | Section: {claim.section}")
        else:
            logger.info("\n--- Final Audit Result (Raw) ---")
            logger.info(result)

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
         logger.info("Usage: python main.py <path_to_document>")
    else:
        file_path = sys.argv[1]
        if os.path.exists(file_path):
            run(file_path)
        else:
            logger.error(f"File not found: {file_path}")


