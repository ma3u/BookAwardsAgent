# Book Awards Agent

A comprehensive tool for discovering, tracking, and managing book awards. The application automatically searches for book awards, extracts detailed information, and updates an Airtable base. It combines Python for data processing and Node.js for the web interface.

## Table of Contents

- [Key Features](#key-features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [For Users](#for-users)
  - [Getting Started](#getting-started)
  - [Python Backend Usage](#python-backend-usage)
  - [Node.js Backend](#nodejs-backend)
- [For Developers](#for-developers)
  - [Project Structure](#project-structure)
  - [Core Components](#core-components)
  - [Development Setup](#development-setup)
  - [Extending the Application](#extending-the-application)
- [Deployment](#deployment)
- [License](#license)
- [Contributing](#contributing)
- [Examples](#examples)
- [Data Model](#data-model)
- [Testing and Validation](#testing-and-validation)
- [Customization](#customization)
- [Troubleshooting](#troubleshooting)
- [Getting Help](#getting-help)
- [Limitations](#limitations)

## Key Features

- **Automated Discovery**: Find book awards from various sources
- **Data Extraction**: Extract comprehensive award details including deadlines, eligibility, and submission guidelines
- **Airtable Integration**: Keep your awards database up-to-date automatically
- **User-friendly Interface**: Easy-to-use web interface for managing awards
- **Customizable Search**: Tailor your search with specific criteria

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

## For Users

### Getting Started

1. **Installation**: Follow the installation steps in the Prerequisites and Installation sections
2. **Configuration**: Set up your `.env` file with Airtable credentials
3. **Run the Application**: Use the Python backend to start collecting award data

### Python Backend Usage

The Python backend provides the core functionality for searching and processing book awards:

```bash
# Basic usage
python -m src

# Search for awards without updating Airtable
python -m src --search-only

# Process specific URLs from a file
python -m src --input-file urls.txt

# Update Airtable from existing data file
python -m src --update-only --input-file book_awards_data.json
```

### Node.js Backend

The Node.js backend provides a web interface for managing awards:

```bash
# Test configuration
cd backend/js
node test-config.js

# Start the web server (if implemented)
npm start
```

## For Developers

### Project Structure

```text
BookAwardsAgent/
├── backend/
│   ├── js/                 # Node.js backend
│   │   ├── config.js       # Configuration loader
│   │   ├── test-config.js  # Configuration test
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

### Core Components

#### 1. Web Search Module (`websearch.py`)

- **Purpose**: Searches for book awards using DuckDuckGo API
- **Key Features**:
  - Performs web searches using predefined queries
  - Filters results to find relevant book awards
  - Handles rate limiting and error cases
  - Removes duplicate results

#### 2. Data Extractor (`extractor.py`)

- **Purpose**: Extracts detailed information from award websites
- **Key Features**:
  - Parses HTML content to extract award details
  - Handles various website structures
  - Extracts contact information, deadlines, and submission guidelines
  - Normalizes data for consistent storage

#### 3. Airtable Updater (`airtable_updater.py`)

- **Purpose**: Manages interaction with Airtable
- **Key Features**:
  - Creates, updates, and deletes records in Airtable
  - Handles batch operations for better performance
  - Implements error handling and retry logic
  - Tracks changes and updates


### Development Setup

#### Python Environment

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Run tests
pytest
```

#### Node.js Environment

```bash
# Install dependencies
cd backend/js
npm install

# Run tests
npm test
```


### Extending the Application

1. **Adding New Data Sources**

   - Modify `websearch.py` to include new search queries
   - Update `extractor.py` to handle new website structures

2. **Customizing Data Storage**

   - Modify `airtable_updater.py` to work with different database systems
   - Implement new data export formats as needed

3. **Enhancing the Web Interface**

   - Extend the Node.js backend with new API endpoints
   - Update the frontend to display additional data

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

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

```text
Copyright [2024] [Ma3u]

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

## Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Clone** your fork:

   ```bash
   git clone https://github.com/yourusername/BookAwardsAgent.git
   ```

3. **Create a feature branch**:

   ```bash
   git checkout -b feature/your-feature
   ```

4. **Commit your changes**:

   ```bash
   git commit -m "Add your feature"
   ```

5. **Push** to the branch:

   ```bash
   git push origin feature/your-feature
   ```

6. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 style guide for Python code
- Write clear, concise commit messages
- Add tests for new features
- Update documentation as needed
- Keep the codebase clean and well-documented

## Examples

### Basic Usage

Search for awards and update Airtable:

```bash
python -m src
```

### Advanced Scenarios

Search without updating Airtable (useful for testing):

```bash
python -m src --search-only
```

Process specific award URLs from a file:

```bash
python -m src --input-file urls.txt
```

Update Airtable from an existing data file:

```bash
python -m src --update-only --input-file book_awards_data.json
```

### Environment Configuration

You can configure the application using environment variables instead of the config file:

```bash
# Required Airtable configuration
export AIRTABLE_API_KEY="your_api_key_here"
export AIRTABLE_BASE_ID="your_base_id_here"

# Optional configuration
export AIRTABLE_TABLE_NAME="Book Awards"
export MAX_SEARCH_RESULTS=10
export REQUEST_DELAY=2
```

### Running in Production

For production use, consider:

1. Setting up a cron job or scheduled task
2. Implementing proper logging and monitoring
3. Setting up error notifications
4. Using environment variables for sensitive data

## Data Model

> **Note:** If any data cannot be written to Airtable due to permissions or schema mismatches, the failed request (and the SQL schema for the attempted fields) will be logged in `failed_airtable_requests.sql` in the project root. See [Troubleshooting](#troubleshooting) for details, including how to re-run or manipulate these statements in SQL.

The application collects and manages the following information for each book award:

### Core Information

- **Award Name**: Official name of the award
- **Category**: Type of award (Fiction, Non-fiction, etc.)
- **Award Status**: Current status (Open, Closed, Upcoming)
- **Award Website**: Official URL
- **Vetting Notes**: Data provenance or vetting status. By default, all records imported by this agent are marked as `imported by Web Scraper` to distinguish them from manually entered or externally sourced records.
- **Awarding Organization**: Organization that presents the award

### Submission Details

- **Entry Deadline**: Application deadline
- **Eligibility Criteria**: Who can apply
- **Application Procedures**: How to apply
- **Application Fee**: Cost to enter (if any)
- **Accepted Formats**: What formats are accepted
- **ISBN Required**: Whether an ISBN is needed

### Prizes & Recognition

- **Prize Amount**: Monetary value (if any)
- **Extra Benefits**: Additional benefits for winners
- **In-Person Celebration**: Details about award ceremonies
- **Past Winners URL**: Link to previous winners

### Contact Information

- **Contact Person**: Primary contact
- **Email**: Contact email
- **Phone**: Contact phone number
- **Physical Address**: Organization's address

### Technical Metadata

- **Data Source**: Where the information was obtained
- **Last Updated**: When the information was last verified
- **Data Quality**: Confidence score for the collected data
- **In-Person Celebration**: Whether an in-person event is part of the award
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

### Failed Airtable Requests & SQL Logging

If an Airtable insert or update fails (e.g., due to permissions or schema issues), the Book Awards Agent will log the failed request as a SQL statement in:

```text
failed_airtable_requests.sql
```

This file is always written to the project root directory (e.g. `/Users/ma3u/projects/BookAwardsAgent/failed_airtable_requests.sql`).

- **Schema**: The file begins with a `CREATE TABLE IF NOT EXISTS` statement matching the fields attempted in the failed request.
- **Failed Requests**: Each failed request is appended as an `INSERT INTO ...` statement, with all attempted field values and the error message.
- **Log Info**: Every time a failed request is logged, an info message with the absolute file path is written to the main log output.

#### Example SQL Output

```sql
-- SQL schema for failed Airtable requests
CREATE TABLE IF NOT EXISTS book_awards_failed (
    `Award Name` TEXT,
    `Award Website` TEXT,
    `Category` TEXT,
    `Prize Amount` FLOAT,
    error TEXT
);

-- CREATE failed
INSERT INTO book_awards_failed (`Award Name`, `Award Website`, `Category`, `Prize Amount`, error)
VALUES ('National Book Award', 'https://www.nationalbook.org', 'Fiction', 5000, 'Insufficient permissions to create new select option "Incomplete"');
```

#### How to Re-run or Manipulate Failed SQL

1. **Copy the schema and failed INSERT statements** from `failed_airtable_requests.sql`.
2. **Paste them into your SQL environment** (e.g., Airflow SQL Explorer, SQLite, or any compatible SQL database).
3. **Run the statements** to recreate the failed records for further analysis, troubleshooting, or data migration.

##### Data Manipulation Example
You can use standard SQL to update, filter, or export the failed data. For example:

```sql
-- Find all failures due to select option issues
SELECT * FROM book_awards_failed WHERE error LIKE '%select option%';

-- Export all fields except the error column
SELECT `Award Name`, `Award Website`, `Category`, `Prize Amount` FROM book_awards_failed;
```

##### Using Data in Airtable
- Airtable itself does not support direct SQL imports, but you can:
  - Export the data from your SQL environment as CSV.
  - Import the CSV into Airtable using the "CSV Import" app or manual upload.
  - Use the error column to filter or clean data before re-import.

**Tip:** Use your SQL environment to fix or enrich the data before re-attempting the upload to Airtable.

---

### Common Issues

1. **No Search Results**
   - Verify internet connection
   - Check if DuckDuckGo API is accessible
   - Review search queries in `config.py`

2. **Airtable Connection Issues**
   - Verify API key and base ID
   - Check network connectivity
   - Ensure the API key has proper permissions

3. **Data Extraction Failures**

   - Check if the website structure has changed
   - Review error logs for specific issues
   - Update the extractor for the new website structure

### Getting Help

For additional support:
1. Check the [GitHub Issues](https://github.com/Ma3u/BookAwardsAgent/issues) page
2. Review the project's [Wiki](https://github.com/Ma3u/BookAwardsAgent/wiki)
3. Open a new issue with detailed error information

- **Agent fails to find book awards**: Try modifying the search queries in `config.py`
- **Incomplete data extraction**: Check the extraction patterns in `extractor.py`
- **Module not found errors**: Ensure you've activated the virtual environment and installed dependencies
- **Airtable connection issues**: Verify your API key and base ID in the `.env` file
- For Airtable integration issues, verify your API credentials and table structure

## Limitations
- The agent relies on website structure for data extraction, which may change over time
- Some fields may require manual verification for complete accuracy
- Rate limiting may affect the number of awards that can be processed in a single run
