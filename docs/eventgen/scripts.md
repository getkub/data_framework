# Utility Scripts

This directory contains various utility scripts for data generation, processing, and simulation tasks.

## scrape_elastic_integrations.py

**Description:**  
Scrapes the elastic/integrations repository to collect integration metadata and sample_event.json files.

**Features:**
- Clones/updates the elastic/integrations repository
- Extracts integration metadata (name, description, version, author)
- Collects sample_event.json files from each integration
- Generates CSV with complete integration inventory
- Organizes sample files in a structured directory layout

**Usage:**

First set up virtual environment (if not already created):
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows
pip install requests
```

Run the scraper:
```bash
cd scripts
python3 scrape_elastic_integrations.py
```

**Output:**
- `data/integrations/repo/` - Git clone of elastic/integrations (gitignored)
- `data/integrations/samples/` - Collected sample_event.json files
- `data/integrations/integration_metadata.csv` - Integration metadata CSV

**CSV Fields:**
- `name` - Integration name
- `description` - Integration description
- `version` - Integration version
- `author` - Integration author
- `has_sample` - Boolean indicating if sample_event.json exists
- `sample_path` - Path to the sample_event.json file


## bulkLoadData.sh

Loads data in bulk based on rules from a mapping file. Generates eventgen configurations and indexes data into Splunk.

**Usage:**
```bash
./bulkLoadData.sh
```

## cloneSampleData.sh

Generates data by cloning template exactly one time. Designed for replaying sanitized CSV data.

**Usage:**
```bash
./cloneSampleData.sh <sanitised_file_in_csv> [debug]
```

## file_syslogGen.sh

Simulates rsyslog data into various facilities and locations using netcat.

**Usage:**
```bash
./file_syslogGen.sh <port_number> [sd|msg]
```

## message_syslogGen.sh

Generates continuous syslog messages with random parameters for testing purposes.

**Usage:**
```bash
./message_syslogGen.sh
```

## replayData.sh

Generates data for specific functional testing. Supports both sample and replay modes.

**Usage:**
```bash
./replayData.sh <sanitised_file_in_csv> <replay|sample> [debug]
```

## sanitise.sh

Sanitises data based on Perl regex patterns. Performs in-place replacement on the input file.

**Usage:**
```bash
./sanitise.sh <file_to_sanitise_absolute_path>
```

## create_dummy_inputs.sh

Creates dummy data files for testing inputs.conf.

**Usage:**
```bash
./create_dummy_inputs.sh <ruleset_file>