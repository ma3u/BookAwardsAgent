"""
Configuration settings for the Book Awards Websearch Agent.
Loads and validates environment variables.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
import pathlib

# Explicitly specify the .env path
ENV_PATH = pathlib.Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# Debug print to confirm loading
print(f"[DEBUG] AIRTABLE_API_KEY loaded: {os.getenv('AIRTABLE_API_KEY')}")

# Required environment variables
REQUIRED_ENV_VARS = [
    'AIRTABLE_API_KEY',
    'AIRTABLE_BASE_ID',
    'AIRTABLE_TABLE_NAME'
]

# Validate required environment variables
missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
if missing_vars:
    raise EnvironmentError(
        f"Missing required environment variables: {', '.join(missing_vars)}"
    )

# Airtable configuration
class AirtableConfig:
    API_KEY = os.getenv('AIRTABLE_API_KEY')
    BASE_ID = os.getenv('AIRTABLE_BASE_ID')
    TABLE_NAME = os.getenv('AIRTABLE_TABLE_NAME')

# Fields to extract from book award websites
AWARD_FIELDS = [
    "Award Name",
    "Category",
    "Entry Deadline",
    "Eligibility Criteria",
    "Application Procedures",
    "Award Website",
    "Prize Amount",
    "Application Fee",
    "Award Status",
    "Award Logo",
    "Awarding Organization",
    "Contact Person",
    "Contact Email",
    "Contact Phone",
    "Physical Address",
    "Past Winners URL",
    "Extra Benefits",
    "In-Person Celebration",
    "Number of Categories",
    "Geographic Restrictions",
    "Alli Rating",
    "Accepted Formats",
    "ISBN Required",
    "Accepts Series",
    "Accepts Anthologies",
    "Accepts Debut Authors",
    "Evaluates Covers",
    "Evaluates Illustrations",
    "Evaluates Interior Design",
    "Secondary Website",
    "Judging Criteria",
    "Listed in Lead Magnet",
    "Described in Drip Campaign"
]

# Airtable configuration
AIRTABLE_API_KEY = os.getenv('AIRTABLE_API_KEY')
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
AIRTABLE_TABLE_NAME = os.getenv('AIRTABLE_TABLE_NAME')

# Search configuration
SEARCH_QUERIES = [
    "book awards submission deadline",
    "literary prize application",
    "book contest entry requirements",
    "publishing awards eligibility",
    "author awards application process"
]

# User agent for web requests
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# Maximum number of search results to process per query
MAX_SEARCH_RESULTS = 10

# Delay between requests (in seconds) to avoid rate limiting
REQUEST_DELAY = 2
