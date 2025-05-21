"""
Main module for the Book Awards Websearch Agent.
Coordinates the websearch, data extraction, and Airtable update processes.
"""

import os
import sys
import time
import logging
import argparse
from typing import List, Dict, Any

from .websearch import WebSearcher
from .extractor import DataExtractor
from .airtable_updater import AirtableUpdater
from .config import AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("book_awards_agent.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BookAwardsAgent:
    """Main class for the Book Awards Websearch Agent."""
    
    def __init__(self, airtable_api_key=None, airtable_base_id=None, airtable_table_name=None):
        """
        Initialize the Book Awards Agent.
        
        Args:
            airtable_api_key: Airtable API key (defaults to config value)
            airtable_base_id: Airtable base ID (defaults to config value)
            airtable_table_name: Airtable table name (defaults to config value)
        """
        self.websearcher = WebSearcher()
        self.extractor = DataExtractor()
        self.airtable_updater = AirtableUpdater(
            api_key=airtable_api_key or AIRTABLE_API_KEY,
            base_id=airtable_base_id or AIRTABLE_BASE_ID,
            table_name=airtable_table_name or AIRTABLE_TABLE_NAME
        )
        
    def run(self, search_only=False, update_only=False, input_file=None):
        """
        Run the Book Awards Agent.
        
        Args:
            search_only: Only search for awards without updating Airtable
            update_only: Only update Airtable from existing data file
            input_file: Path to input file with award URLs (one per line)
        """
        if update_only and input_file:
            # Update Airtable from existing data file
            self._update_from_file(input_file)
        elif input_file:
            # Process specific URLs from file
            self._process_from_file(input_file, search_only)
        else:
            # Search for new awards
            self._search_and_process(search_only)
    
    def _search_and_process(self, search_only=False):
        """
        Search for book awards and process the results.
        
        Args:
            search_only: Only search for awards without updating Airtable
        """
        logger.info("Starting book awards search")
        
        # Search for book awards
        search_results = self.websearcher.search_for_book_awards()
        
        if not search_results:
            logger.warning("No book awards found in search")
            return
            
        logger.info(f"Found {len(search_results)} potential book awards")
        
        # Process each result
        all_awards_data = []
        
        for result in search_results:
            url = result['url']
            title = result['title']
            
            logger.info(f"Processing {title} at {url}")
            
            # Extract data from the award website
            award_data = self.extractor.extract_award_data(url, title)
            
            # Save the data
            all_awards_data.append(award_data)
            
            # Save progress to file
            self._save_progress(all_awards_data)
            
            # Update Airtable if not in search-only mode
            if not search_only:
                self.airtable_updater.update_airtable(award_data)
                
            # Avoid rate limiting
            time.sleep(2)
            
        # Final update to Airtable in batch if not in search-only mode
        if not search_only and all_awards_data:
            results = self.airtable_updater.update_multiple_awards(all_awards_data)
            logger.info(f"Airtable update results: {results}")
            
        logger.info("Book awards search and processing complete")
    
    def _process_from_file(self, input_file, search_only=False):
        """
        Process specific URLs from a file.
        
        Args:
            input_file: Path to input file with award URLs (one per line)
            search_only: Only search for awards without updating Airtable
        """
        if not os.path.exists(input_file):
            logger.error(f"Input file not found: {input_file}")
            return
            
        logger.info(f"Processing URLs from {input_file}")
        
        # Read URLs from file
        with open(input_file, 'r') as f:
            raw_lines = f.readlines()
        # Only process lines that are not comments or blank
        urls = []
        for line in raw_lines:
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue
            # Remove any trailing status comment
            url = stripped.split('#')[0].strip()
            if url:
                urls.append(url)
        if not urls:
            logger.warning("No URLs found in input file")
            return
        logger.info(f"Found {len(urls)} URLs to process")
        # Process each URL
        all_awards_data = []
        for idx, url in enumerate(urls):
            logger.info(f"Processing {url}")
            fail_reason = None
            try:
                # Extract data from the award website, capturing reason if failed
                award_data, fail_reason = self.extractor.extract_award_data_with_reason(url)
                if award_data is None:
                    reason_str = f"failed: {fail_reason}" if fail_reason else "failed"
                    logger.error(f"Extraction failed for {url}. Marking as {reason_str} in template.")
                    self._update_url_status_in_file(input_file, url, reason_str)
                    continue
                # Save the data
                all_awards_data.append(award_data)
                # Save progress to file
                self._save_progress(all_awards_data)
                # Set status to json-complete
                self._update_url_status_in_file(input_file, url, 'json-complete')
                # Update Airtable if not in search-only mode
                if not search_only:
                    airtable_success = self.airtable_updater.update_airtable(award_data)
                    if airtable_success:
                        # Set status to both
                        self._update_url_status_in_file(input_file, url, 'json-complete, airtable-complete')
            except Exception as e:
                fail_reason = f"{type(e).__name__}: {e}"
                logger.error(f"Unexpected error processing {url}: {fail_reason}")
                self._update_url_status_in_file(input_file, url, f"failed: {fail_reason}")
            # Avoid rate limiting
            time.sleep(2)
        # Log summary
        num_total = len(urls)
        num_success = sum(1 for line in open(input_file) if '# json-complete' in line)
        num_failed = sum(1 for line in open(input_file) if '# failed' in line)
        logger.info(f"SUMMARY: Processed {num_total} URLs | Success: {num_success} | Failed: {num_failed}")

    def _update_url_status_in_file(self, input_file, url, status):
        """
        Update the status comment for a URL in the input file.
        If upgrading from json-complete to json-complete, airtable-complete, do not downgrade.
        """
        try:
            with open(input_file, 'r') as f:
                lines = f.readlines()
            updated_lines = []
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('#') or not stripped:
                    updated_lines.append(line)
                    continue
                # Remove any trailing status comment for comparison
                line_url = stripped.split('#')[0].strip()
                if line_url == url:
                    # Check existing status
                    current_status = None
                    if '#' in stripped:
                        current_status = stripped.split('#', 1)[1].strip()
                    # If setting to both, always update
                    if status == 'json-complete, airtable-complete':
                        base = line_url
                        updated_lines.append(f"{base}  # json-complete, airtable-complete\n")
                    # If setting to json-complete, only update if not already both
                    elif status == 'json-complete':
                        if current_status == 'json-complete, airtable-complete':
                            updated_lines.append(line)
                        else:
                            base = line_url
                            updated_lines.append(f"{base}  # json-complete\n")
                    else:
                        base = line_url
                        updated_lines.append(f"{base}  # {status}\n")
                else:
                    updated_lines.append(line)
            with open(input_file, 'w') as f:
                f.writelines(updated_lines)
        except Exception as e:
            logger.error(f"Error updating status for {url} in {input_file}: {e}")

    
    def _update_from_file(self, input_file):
        """
        Update Airtable from an existing data file.
        
        Args:
            input_file: Path to input file with award data (JSON format)
        """
        import json
        
        if not os.path.exists(input_file):
            logger.error(f"Input file not found: {input_file}")
            return
            
        logger.info(f"Updating Airtable from {input_file}")
        
        # Read data from file
        try:
            logger.info(f"Trying to open file at: {input_file}")
            with open(input_file, 'r') as f:
                awards_data = json.load(f)
                
            if not awards_data:
                logger.warning("No award data found in input file")
                return
                
            logger.info(f"Found {len(awards_data)} awards to update")
            
            # Update Airtable
            results = self.airtable_updater.update_multiple_awards(awards_data)
            logger.info(f"Airtable update results: {results}")
            
        except Exception as e:
            logger.error(f"Error updating from file: {e}")
            
        logger.info("Airtable update complete")
    
    def _save_progress(self, awards_data):
        """
        Save progress to a file.
        
        Args:
            awards_data: List of award data dictionaries
        """
        import json
        
        try:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            data_file = os.path.join(project_root, 'book_awards_data.json')
            with open(data_file, 'w') as f:
                json.dump(awards_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving progress: {e}")

def main():
    """Main entry point for the Book Awards Agent."""
    parser = argparse.ArgumentParser(description="Book Awards Websearch Agent")
    
    parser.add_argument("--search-only", action="store_true", help="Only search for awards without updating Airtable")
    parser.add_argument("--update-only", action="store_true", help="Only update Airtable from existing data file")
    parser.add_argument("--input-file", help="Path to input file with award URLs or data")
    parser.add_argument("--airtable-api-key", help="Airtable API key")
    parser.add_argument("--airtable-base-id", help="Airtable base ID")
    parser.add_argument("--airtable-table-name", help="Airtable table name")
    
    args = parser.parse_args()
    
    # Set input_template.txt as default input file if not provided and not update-only
    input_file = args.input_file
    if not input_file and not args.update_only:
        # Path relative to backend/python/src
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        input_file = os.path.join(project_root, "input_template.txt")
    
    # Initialize the agent
    agent = BookAwardsAgent(
        airtable_api_key=args.airtable_api_key,
        airtable_base_id=args.airtable_base_id,
        airtable_table_name=args.airtable_table_name
    )
    
    # Run the agent
    agent.run(
        search_only=args.search_only,
        update_only=args.update_only,
        input_file=input_file
    )

if __name__ == "__main__":
    main()
