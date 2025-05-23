"""
Airtable integration module for the Book Awards Websearch Agent.
Handles updating the Airtable base with book award data.
"""

import os
import time
import requests
import logging
from typing import Dict, Any, List, Optional
import json
import urllib.parse
from .config import AIRTABLE_API_KEY, AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AirtableUpdater:
    """Class to handle Airtable updates for book award data."""

    # Fields that are single/multi-select in Airtable (update as needed)
    SELECT_FIELDS = [
        "Category",
        "Award Status"
    ]
    # Fields that should be numeric (float)
    NUMERIC_FIELDS = [
        "Prize Amount",
        "Application Fee"
    ]

    def __init__(self, api_key: str = None, base_id: str = None, table_name: str = None):
        """
        Initialize the AirtableUpdater with API credentials.
        
        Args:
            api_key: Airtable API key (defaults to config value)
            base_id: Airtable base ID (defaults to config value)
            table_name: Airtable table name (defaults to config value)
        """
        self.api_key = api_key or AIRTABLE_API_KEY
        self.base_id = base_id or AIRTABLE_BASE_ID
        self.table_name = table_name or AIRTABLE_TABLE_NAME
        
        # Validate credentials
        if not self.api_key or not self.base_id or not self.table_name:
            logger.warning("Airtable credentials not fully configured")
            
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        self.base_url = f'https://api.airtable.com/v0/{self.base_id}/{self.table_name}'
        self.existing_records = {}  # Cache for existing records
        # Always initialize select_options_cache, even if super().__init__ is called
        self.select_options_cache = getattr(self, 'select_options_cache', {})


    def _fetch_select_options(self):
        """
        Fetch and cache select options for relevant fields from Airtable.
        """
        url = f"https://api.airtable.com/v0/meta/bases/{self.base_id}/tables"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            tables = response.json().get('tables', [])
            for table in tables:
                if table['name'] == self.table_name:
                    for field in table['fields']:
                        if field['name'] in self.SELECT_FIELDS and field['type'] == 'singleSelect':
                            self.select_options_cache[field['name']] = [opt['name'] for opt in field['options']['choices']]
        except Exception as e:
            logger.error(f"Failed to fetch select options: {e}")

    def _get_select_options(self, field_name):
        if field_name not in self.select_options_cache:
            self._fetch_select_options()
        return self.select_options_cache.get(field_name, [])

    def __init__(self, api_key: str = None, base_id: str = None, table_name: str = None):
        """
        Initialize the AirtableUpdater with API credentials.
        
        Args:
            api_key: Airtable API key (defaults to config value)
            base_id: Airtable base ID (defaults to config value)
            table_name: Airtable table name (defaults to config value)
        """
        self.api_key = api_key or AIRTABLE_API_KEY
        self.base_id = base_id or AIRTABLE_BASE_ID
        self.table_name = table_name or AIRTABLE_TABLE_NAME
        
        # Validate credentials
        if not self.api_key or not self.base_id or not self.table_name:
            logger.warning("Airtable credentials not fully configured")
            
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        self.base_url = f'https://api.airtable.com/v0/{self.base_id}/{self.table_name}'
        self.existing_records = {}  # Cache for existing records
        self.select_options_cache = {}  # Ensure select_options_cache is always available

    def _prepare_fields(self, award_data: Dict[str, Any]) -> Dict[str, Any]:
        # Only include fields that exist in Airtable schema (AWARD_FIELDS)
        from .config import AWARD_FIELDS
        boolean_fields = [
            "ISBN Required", "Accepts Series", "Accepts Anthologies",
            "Accepts Debut Authors", "Evaluates Covers", "Evaluates Illustrations",
            "Evaluates Interior Design", "In-Person Celebration"
        ]
        max_text_length = 10000  # Defensive limit for text fields
        fields = {}
        for key, value in award_data.items():
            if key not in AWARD_FIELDS:
                continue
            # Skip empty values
            if value is None or (isinstance(value, str) and value.strip() == ""):
                continue
            # Convert boolean fields
            if key in boolean_fields:
                # Special handling for In-Person Celebration: always "Yes"/"No" string
                if key == "In-Person Celebration":
                    if isinstance(value, bool):
                        fields[key] = "Yes" if value else "No"
                    elif isinstance(value, str):
                        fields[key] = "Yes" if value.strip().lower() in ["yes", "true", "1"] else "No"
                    else:
                        fields[key] = "No"
                else:
                    fields[key] = str(value).strip().lower() in ["yes", "true", "1"]
            # Validate select fields
            elif key in self.SELECT_FIELDS:
                allowed_options = self._get_select_options(key)
                if value in allowed_options:
                    fields[key] = value
                elif allowed_options:
                    fields[key] = allowed_options[0]
                else:
                    continue
            # Format numeric fields
            elif key in self.NUMERIC_FIELDS:
                import re
                try:
                    numeric = float(re.sub(r'[^\d.]', '', str(value)))
                    fields[key] = numeric
                except Exception:
                    continue
            # Special handling for Number of Categories: try to cast to int, else skip
            elif key == "Number of Categories":
                import re
                try:
                    # Remove non-digit characters, allow numbers like "80", "2025", etc.
                    num_str = re.sub(r'[^\d]', '', str(value))
                    if num_str:
                        fields[key] = int(num_str)
                except Exception:
                    continue
            # Truncate long text fields
            elif isinstance(value, str) and len(value) > max_text_length:
                fields[key] = value[:max_text_length]
            else:
                fields[key] = value
        return fields

    def update_airtable(self, award_data: Dict[str, Any]) -> bool:
        """
        Update Airtable with the provided award data.
        
        Args:
            award_data: Dictionary containing award data
            
        Returns:
            Boolean indicating success
        """
        if not self.api_key or not self.base_id or not self.table_name:
            logger.error("Airtable credentials not configured")
            return False
            
        try:
            # Check if this award already exists in Airtable
            existing_record_id = self._find_existing_record(award_data["Award Name"], award_data["Award Website"])
            
            if existing_record_id:
                # Update existing record
                return self._update_record(existing_record_id, award_data)
            else:
                # Create new record
                return self._create_record(award_data)
                
        except Exception as e:
            logger.error(f"Error updating Airtable: {e}")
            return False
    
    def update_multiple_awards(self, awards_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Update multiple awards in Airtable.
        
        Args:
            awards_data: List of dictionaries containing award data
            
        Returns:
            Dictionary with counts of created, updated, and failed records
        """
        results = {
            "created": 0,
            "updated": 0,
            "failed": 0
        }
        
        # Load existing records first to minimize API calls
        self._load_existing_records()
        
        for award_data in awards_data:
            try:
                # Check if this award already exists in Airtable
                existing_record_id = self._find_existing_record(award_data["Award Name"], award_data["Award Website"])
                
                if existing_record_id:
                    # Update existing record
                    success = self._update_record(existing_record_id, award_data)
                    if success:
                        results["updated"] += 1
                    else:
                        results["failed"] += 1
                else:
                    # Create new record
                    success = self._create_record(award_data)
                    if success:
                        results["created"] += 1
                    else:
                        results["failed"] += 1
                        
                # Avoid rate limiting
                time.sleep(0.2)
                
            except Exception as e:
                logger.error(f"Error updating award {award_data.get('Award Name', 'Unknown')}: {e}")
                results["failed"] += 1
                
        return results
    
    def _load_existing_records(self) -> None:
        """
        Load existing records from Airtable to minimize API calls.
        """
        try:
            url = f"{self.base_url}?fields%5B%5D=Award+Name&fields%5B%5D=Award+Website"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            records = response.json().get('records', [])
            
            # Cache records by name and website for quick lookup
            for record in records:
                record_id = record.get('id')
                fields = record.get('fields', {})
                name = fields.get('Award Name', '')
                website = fields.get('Award Website', '')
                
                if name:
                    self.existing_records[name.lower()] = record_id
                if website:
                    self.existing_records[website.lower()] = record_id
                    
            logger.info(f"Loaded {len(records)} existing records from Airtable")
            
        except Exception as e:
            logger.error(f"Error loading existing records: {e}")
    
    def _create_record(self, award_data: Dict[str, Any]) -> bool:
        fields = self._prepare_fields(award_data)
        try:
            url = self.base_url
            response = requests.post(url, headers=self.headers, json={'fields': fields})
            response.raise_for_status()
            return True
        except requests.exceptions.HTTPError as e:
            error_detail = None
            try:
                error_detail = response.json()
            except Exception:
                pass
            logger.error(f"Error creating record: {e}, data sent: {fields}, airtable_response: {error_detail}")
            return False
        except Exception as e:
            logger.error(f"Error creating record: {e}, data sent: {fields}")
            return False

    def _update_record(self, record_id: str, award_data: Dict[str, Any]) -> bool:
        """
        Update an existing Airtable record by ID.
        Args:
            record_id: The Airtable record ID to update
            award_data: Dictionary of award data to update
        Returns:
            True if update succeeded, False otherwise
        """
        fields = self._prepare_fields(award_data)
        try:
            url = f"{self.base_url}/{record_id}"
            response = requests.patch(url, headers=self.headers, json={'fields': fields})
            response.raise_for_status()
            return True
        except requests.exceptions.HTTPError as e:
            error_detail = None
            try:
                error_detail = response.json()
            except Exception:
                pass
            logger.error(f"Error updating record: {e}, record_id: {record_id}, data sent: {fields}, airtable_response: {error_detail}")
            return False
        except Exception as e:
            logger.error(f"Error updating record: {e}, record_id: {record_id}, data sent: {fields}")
            return False

    def _escape_formula_value(self, value: str) -> str:
        # Airtable formulas use double quotes for string literals, and double quotes inside must be doubled
        # Also escape ampersands and other special characters if needed
        if not isinstance(value, str):
            value = str(value)
        return '"' + value.replace('"', '""') + '"'

    def _find_existing_record(self, award_name: str, award_website: str) -> Optional[str]:
        """
        Find an existing record by award name or website.
        
        Args:
            award_name: Name of the award
            award_website: Website of the award
        
        Returns:
            Record ID if found, None otherwise
        """
        # Check cache first
        if self.existing_records:
            if award_name.lower() in self.existing_records:
                return self.existing_records[award_name.lower()]
            if award_website.lower() in self.existing_records:
                return self.existing_records[award_website.lower()]
        # If not in cache, query Airtable
        try:
            # Use robust escaping for formula value, then URL-encode
            safe_name = self._escape_formula_value(award_name.lower())
            formula = f'LOWER({{Award Name}}) = {safe_name}'
            encoded_formula = urllib.parse.quote(formula, safe='')
            url = f"{self.base_url}?filterByFormula={encoded_formula}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            records = response.json().get('records', [])
            if records:
                return records[0]['id']
        except Exception as e:
            logger.error(f"Error finding existing record: {e}")
        return None

    def _calculate_completeness(self, award_data: Dict[str, Any]) -> str:
        """
        Calculate data completeness percentage.

        Args:
            award_data: Dictionary containing award data
        Returns:
            String representation of completeness (e.g., "75%")
        """
        essential_fields = [
            "Award Name", "Category", "Entry Deadline", "Eligibility Criteria",
            "Application Procedures", "Award Website", "Prize Amount",
            "Application Fee", "Award Status"
        ]
        # Count filled essential fields
        filled_essential = sum(1 for field in essential_fields if award_data.get(field))
        essential_completeness = filled_essential / len(essential_fields)
        
        # Count filled non-essential fields
        non_essential_fields = [field for field in award_data.keys() if field not in essential_fields]
        filled_non_essential = sum(1 for field in non_essential_fields if award_data.get(field))
        non_essential_completeness = filled_non_essential / len(non_essential_fields) if non_essential_fields else 0
        
        # Calculate overall completeness (essential fields weighted more heavily)
        completeness = (essential_completeness * 0.7) + (non_essential_completeness * 0.3)
        
        # Convert to percentage
        percentage = int(completeness * 100)
        
        # Map to categories
        if percentage >= 90:
            return "Complete"
        elif percentage >= 70:
            return "Mostly Complete"
        elif percentage >= 50:
            return "Partially Complete"
        else:
            return "Incomplete"
