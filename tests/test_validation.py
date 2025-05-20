"""
Test script for validating the Book Awards Websearch Agent.
"""

import os
import sys
import json
import logging
from typing import Dict, Any, List

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from websearch import WebSearcher
from extractor import DataExtractor
from airtable_updater import AirtableUpdater
from config import AWARD_FIELDS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_websearch():
    """Test the websearch functionality."""
    logger.info("Testing websearch functionality...")
    
    searcher = WebSearcher()
    results = searcher.search_for_book_awards()
    
    if results:
        logger.info(f"Found {len(results)} potential book awards")
        logger.info(f"First result: {results[0]}")
        return True
    else:
        logger.error("No book awards found in search")
        return False

def test_extraction(url=None):
    """
    Test the data extraction functionality.
    
    Args:
        url: URL to test extraction on (optional)
    """
    logger.info("Testing data extraction functionality...")
    
    # Use a known book award URL if none provided
    if not url:
        url = "https://axiomawards.com/"
    
    extractor = DataExtractor()
    award_data = extractor.extract_award_data(url)
    
    # Check if essential fields were extracted
    essential_fields = ["Award Name", "Award Website"]
    missing_fields = [field for field in essential_fields if not award_data.get(field)]
    
    if missing_fields:
        logger.error(f"Missing essential fields: {missing_fields}")
        return False
    
    logger.info(f"Successfully extracted data for {award_data.get('Award Name')}")
    logger.info(f"Fields extracted: {[field for field in award_data.keys() if award_data.get(field)]}")
    
    # Save the extracted data for inspection
    with open("test_extraction_result.json", "w") as f:
        json.dump(award_data, f, indent=2)
    
    logger.info("Saved extraction result to test_extraction_result.json")
    return True

def test_airtable_integration(api_key=None, base_id=None, table_name=None):
    """
    Test the Airtable integration functionality.
    
    Args:
        api_key: Airtable API key
        base_id: Airtable base ID
        table_name: Airtable table name
    """
    if not api_key or not base_id or not table_name:
        logger.warning("Airtable credentials not provided, skipping integration test")
        return False
    
    logger.info("Testing Airtable integration...")
    
    # Create a test award record
    test_award = {
        "Award Name": "Test Book Award",
        "Category": "Non-fiction",
        "Entry Deadline": "12/31/2025",
        "Eligibility Criteria": "Books published in the last 2 years",
        "Application Procedures": "Submit online through the website",
        "Award Website": "https://example.com/test-award",
        "Prize Amount": "$1000",
        "Application Fee": "$75",
        "Award Status": "Open",
        "Awarding Organization": "Test Organization",
        "In-Person Celebration": "Yes",
        "ISBN Required": "Yes"
    }
    
    # Initialize the Airtable updater
    updater = AirtableUpdater(api_key, base_id, table_name)
    
    # Test updating Airtable
    success = updater.update_airtable(test_award)
    
    if success:
        logger.info("Successfully updated Airtable with test award")
        return True
    else:
        logger.error("Failed to update Airtable with test award")
        return False

def validate_sample_data():
    """Validate the agent with sample data."""
    logger.info("Validating agent with sample data...")
    
    # Test URLs for known book awards
    test_urls = [
        "https://axiomawards.com/",
        "https://www.indieexcellence.com/",
        "https://www.nonobviousbookawards.com/"
    ]
    
    extractor = DataExtractor()
    all_awards_data = []
    
    for url in test_urls:
        logger.info(f"Extracting data from {url}")
        award_data = extractor.extract_award_data(url)
        all_awards_data.append(award_data)
    
    # Save the extracted data
    with open("sample_awards_data.json", "w") as f:
        json.dump(all_awards_data, f, indent=2)
    
    logger.info("Saved sample awards data to sample_awards_data.json")
    
    # Analyze data completeness
    analyze_data_completeness(all_awards_data)
    
    return True

def analyze_data_completeness(awards_data):
    """
    Analyze the completeness of extracted data.
    
    Args:
        awards_data: List of award data dictionaries
    """
    logger.info("Analyzing data completeness...")
    
    # Count filled fields for each award
    for award in awards_data:
        award_name = award.get("Award Name", "Unknown")
        filled_fields = sum(1 for field in AWARD_FIELDS if award.get(field))
        completeness = filled_fields / len(AWARD_FIELDS) * 100
        
        logger.info(f"{award_name}: {filled_fields}/{len(AWARD_FIELDS)} fields filled ({completeness:.1f}%)")
        
        # List missing important fields
        important_fields = ["Award Name", "Category", "Entry Deadline", "Eligibility Criteria", 
                           "Application Procedures", "Award Website", "Prize Amount", "Application Fee"]
        missing_important = [field for field in important_fields if not award.get(field)]
        
        if missing_important:
            logger.warning(f"{award_name}: Missing important fields: {missing_important}")

def main():
    """Main entry point for testing."""
    # Test websearch
    websearch_success = test_websearch()
    
    # Test extraction
    extraction_success = test_extraction()
    
    # Validate with sample data
    validation_success = validate_sample_data()
    
    # Test Airtable integration if credentials are provided
    api_key = os.environ.get("AIRTABLE_API_KEY")
    base_id = os.environ.get("AIRTABLE_BASE_ID")
    table_name = os.environ.get("AIRTABLE_TABLE_NAME")
    
    if api_key and base_id and table_name:
        airtable_success = test_airtable_integration(api_key, base_id, table_name)
    else:
        logger.warning("Airtable credentials not found in environment variables")
        airtable_success = False
    
    # Print summary
    logger.info("\nTest Summary:")
    logger.info(f"Websearch: {'SUCCESS' if websearch_success else 'FAILURE'}")
    logger.info(f"Extraction: {'SUCCESS' if extraction_success else 'FAILURE'}")
    logger.info(f"Validation: {'SUCCESS' if validation_success else 'FAILURE'}")
    logger.info(f"Airtable: {'SUCCESS' if airtable_success else 'NOT TESTED'}")

if __name__ == "__main__":
    main()
