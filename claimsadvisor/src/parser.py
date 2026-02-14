import os
import logging
from dotenv import load_dotenv
from llama_parse import LlamaParse

# Configure Logging
logger = logging.getLogger(__name__)

load_dotenv()

SUPPORTED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png', '.docx', '.html'}

def parse_document(file_path: str) -> str:
    """
    Parses a document into markdown text using LlamaParse with validation and logging.
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        raise FileNotFoundError(f"File not found: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        logger.warning(f"File extension {ext} may not be fully supported by LlamaParse.")

    if not os.getenv("LLAMA_CLOUD_API_KEY"):
        logger.error("LLAMA_CLOUD_API_KEY not found in environment variables.")
        raise ValueError("LLAMA_CLOUD_API_KEY not found in environment variables.")

    # Initialize LlamaParse
    parser = LlamaParse(
        result_type="markdown",
        verbose=False, # Set to False for cleaner production logs
        language="en",
        num_workers=4
    )

    logger.info(f"Starting LlamaParse for: {file_path}")
    
    try:
        # Load and parse the document
        documents = parser.load_data(file_path)
        
        # Combine all parsed pages/sections into one string
        extracted_text = "\n\n".join([doc.text for doc in documents])
        
        if not extracted_text:
            logger.warning(f"No text extracted from {file_path}")
            
        return extracted_text
        
    except Exception as e:
        logger.error(f"Failed to parse document: {file_path}. Error: {e}")
        raise


if __name__ == "__main__":
    # Quick test if run directly
    test_file = "path/to/your/test_invoice.pdf"
    if os.path.exists(test_file):
        text = parse_document(test_file)
        print("--- Extracted Text Preview ---")
        print(text[:500])
    else:
        print(f"Test file not found at {test_file}. Please update the path in src/parser.py for testing.")
