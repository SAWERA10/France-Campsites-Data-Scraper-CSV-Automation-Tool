# France Campsites Data Scraper

## Project Overview

France Campsites Data Scraper is a Python automation project built to collect, clean, and export campsite and caravan-site data from OpenStreetMap using the Overpass API. The project extracts structured business records from public map data and converts them into a clean CSV file for research, lead generation, business analysis, and data collection workflows.

## My Role

My role in this project was Python Web Scraping and Data Extraction Developer. I designed and developed the complete scraping workflow, including API data collection, parsing, cleaning, duplicate removal, data formatting, and CSV export.

## Key Features

- Extracts campsite and caravan-site records from France
- Uses OpenStreetMap and Overpass API as the public data source
- Supports multiple Overpass API mirrors for better reliability
- Collects business name, category, address, city, postal code, latitude, longitude, website, and phone number
- Cleans and formats extracted records
- Normalizes phone numbers and website URLs
- Removes duplicate records using name and coordinate-based matching
- Preserves French accents using UTF-8 encoding
- Exports the final cleaned dataset into a CSV file
- Includes logging for tracking progress and errors

## Technologies Used

- Python
- Requests
- Pandas
- Regular Expressions
- OpenStreetMap
- Overpass API
- CSV Data Processing
- Data Cleaning
- Data Extraction
- Python Automation

## Data Fields Extracted

The final CSV file includes the following fields:

- Business Name
- Category
- Full Address
- City
- Postal Code
- Latitude
- Longitude
- Website URL
- Phone Number

## How the Project Works

The script sends a query to the Overpass API to collect campsite and caravan-site records across France. It processes nodes, ways, and relations from OpenStreetMap. After receiving the data, the script parses important business information, cleans the records, removes duplicates, and exports the final results into a CSV file named `france_campsites_cleaned.csv`.

## Installation

Clone this repository:

```bash
git clone https://github.com/SAWERA10/France-Campsites-Data-Scraper-CSV-Automation-Tool.git
cd france-campsites-data-scraper
```

Create and activate a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Install required packages:

```bash
pip install requests pandas
```

## Usage

Run the Python script:

```bash
python france_campsites_scraper.py
```

After the script finishes, the cleaned CSV file will be created in the project folder.

## Output

The project generates a CSV file:

```text
france_campsites_cleaned.csv
```

This file contains cleaned and structured campsite data ready for analysis, business use, or import into spreadsheets and databases.

