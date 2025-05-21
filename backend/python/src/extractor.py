"""
Data extraction module for the Book Awards Websearch Agent.
Handles extracting detailed information from book award websites.
"""

import re
import time
import requests
from bs4 import BeautifulSoup
import logging
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin

from .config import AWARD_FIELDS, USER_AGENT, REQUEST_DELAY

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataExtractor:
    """Class to handle extraction of book award data from websites."""
    
    def __init__(self):
        """Initialize the DataExtractor with default headers and session."""
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.google.com/',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def extract_award_data(self, url: str, title: str = None) -> Optional[Dict[str, Any]]:
        """
        Extract all available book award data from a website.
        
        Args:
            url: URL of the book award website
            title: Optional title from search results
            
        Returns:
            Dictionary containing extracted award data, or None if failed
        """
        logger.info(f"Extracting data from: {url}")
        
        try:
            # Initialize award data with empty values for all fields
            award_data = {field: "" for field in AWARD_FIELDS}
            
            # Set the award website
            award_data["Award Website"] = url
            
            # If title is provided from search, use it as initial award name
            if title:
                award_data["Award Name"] = self._clean_award_name(title)
            
            # Get the main page content
            soup = self._get_page_content(url)
            if not soup:
                logger.error(f"Failed to retrieve content from {url} after retries. Marking as failed.")
                return None
            
            # Extract data from the main page
            award_data = self._extract_main_page_data(soup, url, award_data)
            
            # Look for and extract data from related pages
            award_data = self._extract_related_pages_data(soup, url, award_data)
            
            return award_data
            
        except Exception as e:
            logger.error(f"Error extracting data from {url}: {type(e).__name__}: {e}")
            return None

    def extract_award_data_with_reason(self, url: str, title: str = None):
        """
        Extract award data, returning (data, fail_reason).
        On failure, fail_reason is a short string (e.g., '403 Forbidden', 'DNS error').
        On success, fail_reason is None.
        """
        try:
            result, reason = self._extract_award_data_with_reason_internal(url, title)
            return result, reason
        except Exception as e:
            return None, f"{type(e).__name__}: {e}"

    def _extract_award_data_with_reason_internal(self, url: str, title: str = None):
        fail_reason = None
        try:
            award_data = {field: "" for field in AWARD_FIELDS}
            award_data["Award Website"] = url
            if title:
                award_data["Award Name"] = self._clean_award_name(title)
            soup, fail_reason = self._get_page_content_with_reason(url)
            if not soup:
                return None, fail_reason or "unknown error"
            award_data = self._extract_main_page_data(soup, url, award_data)
            award_data = self._extract_related_pages_data(soup, url, award_data)
            return award_data, None
        except Exception as e:
            return None, f"{type(e).__name__}: {e}"

    def _get_page_content_with_reason(self, url: str):
        """
        Like _get_page_content, but returns (soup, fail_reason)
        """
        import socket
        from requests.exceptions import HTTPError, ConnectionError
        from urllib3.exceptions import NameResolutionError
        max_attempts = 4
        base_delay = 3
        for attempt in range(1, max_attempts + 1):
            try:
                if not url.startswith(('http://', 'https://')):
                    url = f'https://{url}'
                response = self.session.get(url, headers=self.headers, timeout=30)
                response.raise_for_status()
                return BeautifulSoup(response.text, 'html.parser'), None
            except HTTPError as e:
                status = getattr(e.response, 'status_code', None)
                if status == 403:
                    return None, "403 Forbidden"
                if status:
                    fail_reason = f"HTTP {status}"
                else:
                    fail_reason = "HTTP error"
                if attempt == max_attempts:
                    return None, fail_reason
                time.sleep(base_delay * attempt)
            except NameResolutionError as e:
                return None, "DNS error"
            except socket.gaierror as e:
                return None, "DNS error"
            except ConnectionError as e:
                if attempt == max_attempts:
                    return None, "Connection error"
                time.sleep(base_delay * attempt)
            except Exception as e:
                if attempt == max_attempts:
                    return None, f"{type(e).__name__}: {e}"
                time.sleep(base_delay * attempt)
        return None, "unknown error"
    
    def _get_page_content(self, url: str) -> Optional[BeautifulSoup]:
        """
        Get the HTML content of a page and parse it with BeautifulSoup, with retries and exponential backoff.
        
        Args:
            url: URL to retrieve
            
        Returns:
            BeautifulSoup object or None if retrieval fails
        """
        max_attempts = 4
        base_delay = 3
        for attempt in range(1, max_attempts + 1):
            try:
                if not url.startswith(('http://', 'https://')):
                    url = f'https://{url}'
                response = self.session.get(url, headers=self.headers, timeout=30)
                response.raise_for_status()
                return BeautifulSoup(response.text, 'html.parser')
            except HTTPError as e:
                status = getattr(e.response, 'status_code', None)
                logger.error(f"Attempt {attempt} - HTTP error retrieving {url}: {type(e).__name__}: {e} (status: {status})")
                if status == 403:
                    logger.error(f"403 Forbidden for {url}. This site may block bots or require advanced scraping (proxy, Selenium, or manual intervention). Consider checking in a browser or using a proxy.")
                    return None
                if attempt == max_attempts:
                    logger.error(f"Failed to retrieve {url} after {max_attempts} attempts.")
                    return None
                time.sleep(base_delay * attempt)
            except NameResolutionError as e:
                logger.error(f"DNS error (NameResolutionError) for {url}: {e}. The domain may not exist or is unreachable. Skipping further retries.")
                return None
            except socket.gaierror as e:
                logger.error(f"DNS error (gaierror) for {url}: {e}. The domain may not exist or is unreachable. Skipping further retries.")
                return None
            except ConnectionError as e:
                logger.error(f"Attempt {attempt} - Connection error retrieving {url}: {type(e).__name__}: {e}. This may be due to bot-blocking or server issues.")
                if attempt == max_attempts:
                    logger.error(f"Failed to retrieve {url} after {max_attempts} attempts.")
                    return None
                time.sleep(base_delay * attempt)
            except Exception as e:
                logger.error(f"Attempt {attempt} - Unexpected error retrieving {url}: {type(e).__name__}: {e}")
                if attempt == max_attempts:
                    logger.error(f"Failed to retrieve {url} after {max_attempts} attempts.")
                    return None
                time.sleep(base_delay * attempt)
    
    def _extract_main_page_data(self, soup: BeautifulSoup, url: str, award_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract award data from the main page.
        
        Args:
            soup: BeautifulSoup object of the page
            url: URL of the page
            award_data: Current award data dictionary
            
        Returns:
            Updated award data dictionary
        """
        # Extract award name if not already set
        if not award_data["Award Name"]:
            award_data["Award Name"] = self._extract_award_name(soup)
        
        # Extract other basic information
        award_data["Category"] = self._extract_category(soup)
        award_data["Entry Deadline"] = self._extract_deadline(soup)
        award_data["Eligibility Criteria"] = self._extract_eligibility(soup)
        award_data["Application Procedures"] = self._extract_application_procedures(soup)
        award_data["Prize Amount"] = self._extract_prize_amount(soup)
        award_data["Application Fee"] = self._extract_application_fee(soup)
        award_data["Award Status"] = self._extract_award_status(soup)
        award_data["Awarding Organization"] = self._extract_organization(soup)
        
        # Extract contact information
        contact_info = self._extract_contact_info(soup)
        award_data["Contact Person"] = contact_info.get("person", "")
        award_data["Contact Email"] = contact_info.get("email", "")
        award_data["Contact Phone"] = contact_info.get("phone", "")
        award_data["Physical Address"] = contact_info.get("address", "")
        
        # Extract additional details
        award_data["Extra Benefits"] = self._extract_benefits(soup)
        award_data["In-Person Celebration"] = self._extract_celebration(soup)
        award_data["Number of Categories"] = self._extract_categories_count(soup)
        award_data["Geographic Restrictions"] = self._extract_geographic_restrictions(soup)
        award_data["Accepted Formats"] = self._extract_accepted_formats(soup)
        award_data["ISBN Required"] = self._extract_isbn_required(soup)
        award_data["Judging Criteria"] = self._extract_judging_criteria(soup)
        
        # Look for past winners URL
        award_data["Past Winners URL"] = self._extract_past_winners_url(soup, url)
        
        return award_data
    
    def _extract_related_pages_data(self, soup: BeautifulSoup, base_url: str, award_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract data from related pages like guidelines, FAQ, etc.
        
        Args:
            soup: BeautifulSoup object of the main page
            base_url: URL of the main page
            award_data: Current award data dictionary
            
        Returns:
            Updated award data dictionary
        """
        # Look for relevant links
        relevant_links = self._find_relevant_links(soup, base_url)
        
        for link_type, link_url in relevant_links.items():
            logger.info(f"Checking related page: {link_type} at {link_url}")
            
            # Get the related page content
            related_soup = self._get_page_content(link_url)
            if not related_soup:
                continue
                
            time.sleep(REQUEST_DELAY)  # Avoid rate limiting
            
            # Extract data based on the type of page
            if link_type == "guidelines":
                # Update eligibility and application procedures if empty
                if not award_data["Eligibility Criteria"]:
                    award_data["Eligibility Criteria"] = self._extract_eligibility(related_soup)
                if not award_data["Application Procedures"]:
                    award_data["Application Procedures"] = self._extract_application_procedures(related_soup)
                
            elif link_type == "faq":
                # Look for additional information in FAQs
                if not award_data["ISBN Required"]:
                    award_data["ISBN Required"] = self._extract_isbn_required(related_soup)
                if not award_data["Accepted Formats"]:
                    award_data["Accepted Formats"] = self._extract_accepted_formats(related_soup)
                
            elif link_type == "winners":
                # Set the past winners URL
                award_data["Past Winners URL"] = link_url
                
            elif link_type == "about":
                # Look for organization information
                if not award_data["Awarding Organization"]:
                    award_data["Awarding Organization"] = self._extract_organization(related_soup)
                
            elif link_type == "contact":
                # Extract contact information
                contact_info = self._extract_contact_info(related_soup)
                if not award_data["Contact Person"]:
                    award_data["Contact Person"] = contact_info.get("person", "")
                if not award_data["Contact Email"]:
                    award_data["Contact Email"] = contact_info.get("email", "")
                if not award_data["Contact Phone"]:
                    award_data["Contact Phone"] = contact_info.get("phone", "")
                if not award_data["Physical Address"]:
                    award_data["Physical Address"] = contact_info.get("address", "")
        
        return award_data
    
    def _find_relevant_links(self, soup: BeautifulSoup, base_url: str) -> Dict[str, str]:
        """
        Find relevant links on the page for further data extraction.
        
        Args:
            soup: BeautifulSoup object of the page
            base_url: Base URL for resolving relative links
            
        Returns:
            Dictionary mapping link types to URLs
        """
        relevant_links = {}
        
        # Keywords to look for in link text and URLs
        link_keywords = {
            "guidelines": ["guidelines", "rules", "how to enter", "submission", "apply", "entry"],
            "faq": ["faq", "frequently asked", "questions"],
            "winners": ["winners", "past winners", "previous winners", "laureates"],
            "about": ["about", "about us", "history", "mission"],
            "contact": ["contact", "contact us", "get in touch"]
        }
        
        # Find all links on the page
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text(strip=True).lower()
            
            # Skip empty links, anchors, or javascript
            if not href or href.startswith('#') or href.startswith('javascript:'):
                continue
                
            # Resolve relative URLs
            full_url = urljoin(base_url, href)
            
            # Check if the link matches any of our keywords
            for link_type, keywords in link_keywords.items():
                if any(keyword in text.lower() for keyword in keywords) or any(keyword in href.lower() for keyword in keywords):
                    relevant_links[link_type] = full_url
                    break
        
        return relevant_links
    
    def _clean_award_name(self, name: str) -> str:
        """
        Clean and format an award name.
        
        Args:
            name: Raw award name
            
        Returns:
            Cleaned award name
        """
        # Remove common suffixes
        suffixes = [
            "- Official Website", "| Official Site", "Official Page",
            "Home Page", "Homepage", "Home", "| Apply Now", "- Apply Today"
        ]
        
        cleaned_name = name
        for suffix in suffixes:
            cleaned_name = cleaned_name.replace(suffix, "")
            
        # Remove trailing punctuation and whitespace
        cleaned_name = cleaned_name.strip(" -|:,.")
        
        return cleaned_name
    
    def _extract_award_name(self, soup: BeautifulSoup) -> str:
        """Extract the award name from the page."""
        # Try to find the award name in the title
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text(strip=True)
            return self._clean_award_name(title)
            
        # Try to find the award name in the largest heading
        for tag in ['h1', 'h2']:
            heading = soup.find(tag)
            if heading:
                return heading.get_text(strip=True)
                
        return "Unknown Award"
    
    def _extract_category(self, soup: BeautifulSoup) -> str:
        """Extract the award category."""
        # Look for category keywords in the page
        category_keywords = {
            "Fiction": ["fiction", "novel", "short story", "stories"],
            "Non-fiction": ["non-fiction", "nonfiction", "memoir", "biography", "essay"],
            "Poetry": ["poetry", "poem", "verse"],
            "Children's": ["children", "young adult", "ya", "middle grade", "picture book"],
            "Multiple": ["multiple categories", "various categories"]
        }
        
        page_text = soup.get_text().lower()
        
        for category, keywords in category_keywords.items():
            if any(keyword in page_text for keyword in keywords):
                return category
                
        return "Non-fiction"  # Default to Non-fiction as in the CSV
    
    def _extract_deadline(self, soup: BeautifulSoup) -> str:
        """Extract the entry deadline."""
        # Look for deadline patterns in the text
        deadline_patterns = [
            r'deadline[:\s]*([A-Za-z]+\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4})',
            r'entries close[:\s]*([A-Za-z]+\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4})',
            r'submission deadline[:\s]*([A-Za-z]+\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4})',
            r'due by[:\s]*([A-Za-z]+\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4})',
            r'closes on[:\s]*([A-Za-z]+\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4})',
            r'(\d{1,2}/\d{1,2}/\d{2,4})',  # MM/DD/YYYY or DD/MM/YYYY
            r'(\d{1,2}-\d{1,2}-\d{2,4})'   # MM-DD-YYYY or DD-MM-YYYY
        ]
        
        page_text = soup.get_text()
        
        for pattern in deadline_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                return match.group(1)
                
        return ""
    
    def _extract_eligibility(self, soup: BeautifulSoup) -> str:
        """Extract eligibility criteria."""
        # Look for sections that might contain eligibility information
        eligibility_sections = soup.find_all(['div', 'section', 'p'], 
                                           class_=lambda c: c and any(word in str(c).lower() for word in 
                                                                    ['eligibility', 'guidelines', 'rules', 'criteria']))
        
        # Also look for headings that indicate eligibility sections
        eligibility_headings = soup.find_all(['h2', 'h3', 'h4'], 
                                           string=lambda s: s and any(word in s.lower() for word in 
                                                                    ['eligibility', 'who can enter', 'requirements']))
        
        eligibility_text = ""
        
        # Extract text from sections
        for section in eligibility_sections:
            eligibility_text += section.get_text(strip=True) + " "
            
        # Extract text from sections following eligibility headings
        for heading in eligibility_headings:
            next_elem = heading.find_next(['p', 'div', 'ul', 'ol'])
            if next_elem:
                eligibility_text += next_elem.get_text(strip=True) + " "
                
        # Clean up the text
        eligibility_text = re.sub(r'\s+', ' ', eligibility_text).strip()
        
        # If we found something, return it
        if eligibility_text:
            return eligibility_text[:500]  # Limit length
            
        return ""
    
    def _extract_application_procedures(self, soup: BeautifulSoup) -> str:
        """Extract application procedures."""
        # Look for sections that might contain application procedures
        procedure_sections = soup.find_all(['div', 'section', 'p'], 
                                         class_=lambda c: c and any(word in str(c).lower() for word in 
                                                                  ['how to enter', 'submission', 'apply', 'procedure']))
        
        # Also look for headings that indicate procedure sections
        procedure_headings = soup.find_all(['h2', 'h3', 'h4'], 
                                         string=lambda s: s and any(word in s.lower() for word in 
                                                                  ['how to enter', 'submission', 'apply', 'procedure']))
        
        procedure_text = ""
        
        # Extract text from sections
        for section in procedure_sections:
            procedure_text += section.get_text(strip=True) + " "
            
        # Extract text from sections following procedure headings
        for heading in procedure_headings:
            next_elem = heading.find_next(['p', 'div', 'ul', 'ol'])
            if next_elem:
                procedure_text += next_elem.get_text(strip=True) + " "
                
        # Clean up the text
        procedure_text = re.sub(r'\s+', ' ', procedure_text).strip()
        
        # If we found something, return it
        if procedure_text:
            return procedure_text[:500]  # Limit length
            
        return ""
    
    def _extract_prize_amount(self, soup: BeautifulSoup) -> str:
        """Extract the prize amount."""
        # Look for currency symbols followed by numbers
        prize_patterns = [
            r'(\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # $X,XXX.XX
            r'(€\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',   # €X,XXX.XX
            r'(£\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',   # £X,XXX.XX
            r'prize of (\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'award of (\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'cash prize of (\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'grand prize[:\s]*(\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
        ]
        
        page_text = soup.get_text()
        
        for pattern in prize_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                return match.group(1)
                
        return ""
    
    def _extract_application_fee(self, soup: BeautifulSoup) -> str:
        """Extract the application fee."""
        # Look for fee patterns
        fee_patterns = [
            r'(entry fee|submission fee|application fee)[:\s]*(\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'fee[:\s]*(\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
            r'(\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?) (entry fee|submission fee|application fee)',
            r'(€\d{1,3}(?:,\d{3})*(?:\.\d{2})?) (entry fee|submission fee|application fee)',
            r'(£\d{1,3}(?:,\d{3})*(?:\.\d{2})?) (entry fee|submission fee|application fee)'
        ]
        
        page_text = soup.get_text()
        
        for pattern in fee_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                # If the pattern has the fee in the second group
                if 'entry fee' in match.group(1).lower() or 'submission fee' in match.group(1).lower() or 'application fee' in match.group(1).lower():
                    return match.group(2)
                else:
                    return match.group(1)
                    
        return ""
    
    def _extract_award_status(self, soup: BeautifulSoup) -> str:
        """Extract the award status."""
        # Look for status keywords
        page_text = soup.get_text().lower()
        
        if re.search(r'(submissions? (now )?open|entries? (now )?open|apply now)', page_text):
            return "Open"
        elif re.search(r'(submissions? closed|entries? closed|no longer accepting)', page_text):
            return "Closed"
        elif re.search(r'(upcoming|coming soon|next deadline|will open)', page_text):
            return "Upcoming"
            
        return "Open"  # Default to Open
    
    def _extract_organization(self, soup: BeautifulSoup) -> str:
        """Extract the awarding organization."""
        # Look for organization in the footer or about section
        footer = soup.find('footer')
        if footer:
            copyright_text = re.search(r'©\s*\d{4}\s*([^.]+)', footer.get_text())
            if copyright_text:
                return copyright_text.group(1).strip()
                
        # Look for "About" sections
        about_sections = soup.find_all(['div', 'section'], 
                                     class_=lambda c: c and 'about' in str(c).lower())
        
        for section in about_sections:
            # Look for organization patterns
            org_match = re.search(r'(presented by|organized by|sponsored by|a program of)\s+([^.]+)', 
                                section.get_text(), re.IGNORECASE)
            if org_match:
                return org_match.group(2).strip()
                
        return ""
    
    def _extract_contact_info(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract contact information."""
        contact_info = {
            "person": "",
            "email": "",
            "phone": "",
            "address": ""
        }
        
        # Look for email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, soup.get_text())
        if emails:
            contact_info["email"] = emails[0]
            
        # Look for phone numbers
        phone_pattern = r'(\+\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})'
        phones = re.findall(phone_pattern, soup.get_text())
        if phones:
            contact_info["phone"] = ''.join(phones[0]).strip()
            
        # Look for contact person
        contact_sections = soup.find_all(['div', 'section', 'p'], 
                                       class_=lambda c: c and 'contact' in str(c).lower())
        
        for section in contact_sections:
            # Look for person name patterns (e.g., "Contact: John Doe")
            person_match = re.search(r'(contact|coordinator|director|manager):\s*([A-Z][a-z]+\s+[A-Z][a-z]+)', 
                                   section.get_text(), re.IGNORECASE)
            if person_match:
                contact_info["person"] = person_match.group(2).strip()
                break
                
        # Look for physical address
        address_sections = soup.find_all(['div', 'section', 'p'], 
                                       class_=lambda c: c and ('address' in str(c).lower() or 'location' in str(c).lower()))
        
        for section in address_sections:
            # Simple heuristic: if it has multiple lines and contains a zip/postal code pattern
            text = section.get_text(strip=True)
            if re.search(r'\b[A-Z]{2}\s+\d{5}(-\d{4})?\b', text) or re.search(r'\b[A-Z]\d[A-Z]\s+\d[A-Z]\d\b', text):
                contact_info["address"] = text
                break
                
        return contact_info
    
    def _extract_benefits(self, soup: BeautifulSoup) -> str:
        """Extract extra benefits."""
        # Look for benefits keywords
        benefit_keywords = [
            "recognition", "exposure", "promotion", "publicity", "media coverage",
            "certificate", "trophy", "medal", "seal", "sticker", "badge"
        ]
        
        benefits_sections = soup.find_all(['div', 'section', 'p', 'ul', 'li'], 
                                        string=lambda s: s and any(keyword in s.lower() for keyword in benefit_keywords))
        
        benefits_text = ""
        for section in benefits_sections:
            benefits_text += section.get_text(strip=True) + " "
            
        # Clean up the text
        benefits_text = re.sub(r'\s+', ' ', benefits_text).strip()
        
        # If we found something, return it
        if benefits_text:
            return benefits_text[:300]  # Limit length
            
        return ""
    
    def _extract_celebration(self, soup: BeautifulSoup) -> str:
        """Extract information about in-person celebration."""
        # Look for celebration keywords
        celebration_keywords = [
            "ceremony", "gala", "event", "celebration", "award dinner", 
            "reception", "in person", "in-person"
        ]
        
        page_text = soup.get_text().lower()
        
        if any(keyword in page_text for keyword in celebration_keywords):
            return "Yes"
        else:
            return "No"
    
    def _extract_categories_count(self, soup: BeautifulSoup) -> str:
        """Extract the number of categories."""
        # Look for category count patterns
        category_patterns = [
            r'(\d+) categories',
            r'(\d+) award categories',
            r'categories \((\d+)\)'
        ]
        
        page_text = soup.get_text()
        
        for pattern in category_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                return match.group(1)
                
        # Count category listings if available
        category_lists = soup.find_all(['ul', 'ol'], 
                                     class_=lambda c: c and ('category' in str(c).lower() or 'categories' in str(c).lower()))
        
        if category_lists:
            # Count the list items in the first matching list
            items = category_lists[0].find_all('li')
            return str(len(items))
            
        return ""
    
    def _extract_geographic_restrictions(self, soup: BeautifulSoup) -> str:
        """Extract geographic restrictions."""
        # Look for geographic restriction patterns
        geo_patterns = [
            r'open to (authors|publishers) (from|in) ([^.]+)',
            r'(only|exclusively) for (authors|publishers) (from|in) ([^.]+)',
            r'restricted to (authors|publishers) (from|in) ([^.]+)',
            r'open to ([^.]+) (authors|publishers)',
            r'(international|worldwide|global)'
        ]
        
        page_text = soup.get_text()
        
        for pattern in geo_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                if 'international' in pattern or 'worldwide' in pattern or 'global' in pattern:
                    if match.group(0).lower() in ['international', 'worldwide', 'global']:
                        return "No geographic restrictions"
                else:
                    # Extract the geographic restriction
                    if 'open to' in pattern and 'from' in pattern:
                        return match.group(3).strip()
                    elif 'open to' in pattern and 'authors' in pattern:
                        return match.group(1).strip()
                    elif 'only' in pattern or 'exclusively' in pattern:
                        return match.group(4).strip()
                    elif 'restricted to' in pattern:
                        return match.group(3).strip()
                    
        return ""
    
    def _extract_accepted_formats(self, soup: BeautifulSoup) -> str:
        """Extract accepted formats."""
        # Look for format keywords
        format_keywords = {
            "Print": ["print", "hardcover", "paperback", "physical copy"],
            "Digital": ["digital", "e-book", "ebook", "electronic", "pdf", "epub", "mobi"],
            "Audio": ["audio", "audiobook"]
        }
        
        page_text = soup.get_text().lower()
        
        accepted_formats = []
        for format_type, keywords in format_keywords.items():
            if any(keyword in page_text for keyword in keywords):
                accepted_formats.append(format_type)
                
        if accepted_formats:
            return ", ".join(accepted_formats)
            
        return ""
    
    def _extract_isbn_required(self, soup: BeautifulSoup) -> str:
        """Extract whether ISBN is required."""
        page_text = soup.get_text().lower()
        
        if re.search(r'isbn (is )?(required|necessary|needed)', page_text) or "isbn required" in page_text:
            return "Yes"
        elif re.search(r'isbn (is )?(optional|not required|not necessary)', page_text):
            return "No"
            
        return ""
    
    def _extract_judging_criteria(self, soup: BeautifulSoup) -> str:
        """Extract judging criteria."""
        # Look for sections that might contain judging criteria
        criteria_sections = soup.find_all(['div', 'section', 'p'], 
                                        class_=lambda c: c and any(word in str(c).lower() for word in 
                                                                 ['judging', 'criteria', 'evaluation']))
        
        # Also look for headings that indicate criteria sections
        criteria_headings = soup.find_all(['h2', 'h3', 'h4'], 
                                        string=lambda s: s and any(word in s.lower() for word in 
                                                                 ['judging', 'criteria', 'evaluation', 'how entries are judged']))
        
        criteria_text = ""
        
        # Extract text from sections
        for section in criteria_sections:
            criteria_text += section.get_text(strip=True) + " "
            
        # Extract text from sections following criteria headings
        for heading in criteria_headings:
            next_elem = heading.find_next(['p', 'div', 'ul', 'ol'])
            if next_elem:
                criteria_text += next_elem.get_text(strip=True) + " "
                
        # Clean up the text
        criteria_text = re.sub(r'\s+', ' ', criteria_text).strip()
        
        # If we found something, return it
        if criteria_text:
            return criteria_text[:500]  # Limit length
            
        return ""
    
    def _extract_past_winners_url(self, soup: BeautifulSoup, base_url: str) -> str:
        """Extract URL for past winners."""
        # Look for links to past winners
        winner_keywords = ["winners", "past winners", "previous winners", "laureates", "honorees"]
        
        for keyword in winner_keywords:
            winner_links = soup.find_all('a', string=lambda s: s and keyword.lower() in s.lower())
            
            if winner_links:
                href = winner_links[0].get('href')
                if href:
                    return urljoin(base_url, href)
                    
        return ""
