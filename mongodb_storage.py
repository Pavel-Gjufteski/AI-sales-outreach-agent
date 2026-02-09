from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime
from prompt import AgentOutput
from scrape import extract_visible_text, truncate_text

load_dotenv()


MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "ai_outreach_agent"
COLLECTION_NAME = "analysis"


def get_collection():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    return db[COLLECTION_NAME]


def save_analysis(
    company_url: str,
    user_input: str,
    html: str,
    output: AgentOutput,
    token_usage: dict,
    elapsed_seconds: float,
    linkedin_profiles: list,
    pdf_path: str = None
) -> str:
    """
    Save analysis results to MongoDB.
    Extracts website content from html automatically.

    Args:
        company_url: The normalized company website URL (with https://)
        user_input: The URL input from user (e.g., "datamaster.ai" or "https://datamaster.ai")
        html: The HTML content scraped from the website
        output: The AgentOutput from LLM analysis
        token_usage: Token usage statistics
        elapsed_seconds: Processing time
        linkedin_profiles: List of LinkedIn profiles found
        pdf_path: Path to generated PDF (optional)

    Returns:
        str: The inserted document ID
    """
    # Extract visible text from HTML
    visible_text = extract_visible_text(html)
    visible_text = truncate_text(visible_text)

    collection = get_collection()

    document = {
        "user_input": user_input,  
        "website_content": visible_text,  
        "linkedin_profiles": linkedin_profiles,  
        "analysis_output": output.model_dump(), 
        "metadata": {
            "created_at": datetime.utcnow(),
            "token_usage": token_usage,
            "elapsed_seconds": elapsed_seconds,
            "pdf_path": pdf_path,
        }
    }

    result = collection.insert_one(document)
    return str(result.inserted_id)