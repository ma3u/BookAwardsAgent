"""
Configuration settings for the Book Awards Websearch Agent.
"""

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
AIRTABLE_API_KEY = ""  # To be set by user
AIRTABLE_BASE_ID = ""  # To be set by user
AIRTABLE_TABLE_NAME = "Book Awards"

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
