# Book Awards Agent

This is a full-stack application that automatically searches for book awards, extracts detailed information, and updates an Airtable base. It combines Python for data processing and Node.js for the web interface.

## Project Structure

```text
BookAwardsAgent/
├── backend/
│   ├── js/                 # Node.js backend
│   │   ├── config.js       # Configuration loader
│   │   └── test-config.js  # Configuration test
│   │   └── package.json    # Node.js dependencies
│   └── python/             # Python backend
│       ├── src/            # Python source code
│       │   ├── config.py   # Configuration settings
│       │   ├── websearch.py
│       │   ├── extractor.py
│       │   ├── airtable_updater.py
│       │   └── main.py
│       └── requirements.txt # Python dependencies
├── .env.example           # Example environment variables
├── .gitignore            # Git ignore file
└── README.md             # This documentation
```

## Prerequisites

- Python 3.8 or higher
- Node.js 14.x or higher
- An Airtable account with API access
- Git

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Ma3u/BookAwardsAgent.git
   cd BookAwardsAgent
   ```

2. Set up Python environment:
   ```bash
   # Create and activate virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install Python dependencies
   cd backend/python
   pip install -r requirements.txt
   ```

3. Set up Node.js environment:
   ```bash
   cd ../../backend/js
   npm install
   ```

4. Configure environment variables:
   ```bash
   cp ../../.env.example ../../.env
   # Edit ../../.env with your Airtable credentials
   ```

## Configuration

### Environment Variables
Create a `.env` file in the project root with these variables:

```env
# Airtable Configuration
AIRTABLE_API_KEY=your_api_key_here
AIRTABLE_BASE_ID=your_base_id_here
AIRTABLE_TABLE_NAME=Book Awards
```

## Usage

### Python Backend

Run the Python data processing pipeline:


```bash
cd backend/python
python -m src.main
```


### Node.js Backend

Test the Node.js configuration:


```bash
cd backend/js
node test-config.js
```


## Development

### Python

- Virtual environment is recommended
- Install development dependencies:
  ```bash
  pip install -r requirements.txt
  ```

### Node.js

- Install dependencies:
  ```bash
  cd backend/js
  npm install
  ```

## Deployment

### Python

1. Install production dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Node.js

1. Install production dependencies:
   ```bash
   cd backend/js
   npm install --production
   ```

## License

[Specify your license here]

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

Examples:
```bash
# Search only without updating Airtable
python src/main.py --search-only

# Process specific URLs from a file
python src/main.py --input-file urls.txt

# Update Airtable from existing data file
python src/main.py --update-only --input-file book_awards_data.json
```

### Environment Variables
Instead of modifying the config file, you can set environment variables:
```
export AIRTABLE_API_KEY="your_api_key"
export AIRTABLE_BASE_ID="your_base_id"
export AIRTABLE_TABLE_NAME="Book Awards"
```

## Data Fields
The agent collects the following information for each book award:

- Award Name
- Category
- Entry Deadline
- Eligibility Criteria
- Application Procedures
- Award Website
- Prize Amount
- Application Fee
- Award Status
- Award Logo
- Awarding Organization
- Contact Information (Person, Email, Phone, Address)
- Past Winners URL
- Extra Benefits
- In-Person Celebration
- Number of Categories
- Geographic Restrictions
- Accepted Formats
- ISBN Required
- Judging Criteria
- And many more fields matching the provided CSV structure

## Testing and Validation
Run the validation script to test the agent's functionality:
```
python tests/test_validation.py
```

This will:
1. Test the websearch functionality
2. Test data extraction with sample URLs
3. Validate data completeness
4. Test Airtable integration (if credentials are provided)

## Customization
You can customize the agent's behavior by modifying the following files:

- `config.py`: Adjust search queries, field definitions, and other settings
- `websearch.py`: Modify search behavior and result filtering
- `extractor.py`: Enhance data extraction patterns for specific fields
- `airtable_updater.py`: Customize Airtable integration logic

## Troubleshooting
- If the agent fails to find book awards, try modifying the search queries in `config.py`
- If data extraction is incomplete, check the extraction patterns in `extractor.py`
- For Airtable integration issues, verify your API credentials and table structure

## Limitations
- The agent relies on website structure for data extraction, which may change over time
- Some fields may require manual verification for complete accuracy
- Rate limiting may affect the number of awards that can be processed in a single run
