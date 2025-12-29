# Utility Scripts Guide

## Overview

The Data Framework includes a collection of utility scripts for specialized operations, data processing, and system integration. These scripts provide additional functionality beyond the core EventGen engine and Ansible automation.

## Script Categories

### 1. Data Generation Scripts
- `replayData.sh` - Replay existing data with timestamp updates
- `bulkLoadData.sh` - Bulk data loading operations
- `create_dummy_inputs.sh` - Create dummy input data

### 2. System Integration Scripts
- `file_syslogGen.sh` - File-based syslog generation
- `message_syslogGen.sh` - Message-based syslog generation
- `sanitise.sh` - Data sanitization utilities

### 3. Python Utilities
- `raw_packet_from_csv.py` - Network packet generation from CSV

## Data Generation Scripts

### replayData.sh

**Purpose**: Replay existing CSV data with automatic timestamp updates and EventGen integration.

**Usage**:
```bash
./replayData.sh <input_file> <format> [debug]
```

**Parameters**:
- `input_file`: Path to sanitized CSV file
- `format`: Either `sample` or `replay`
- `debug`: Optional `debug` flag for verbose output

**Example**:
```bash
# Sample mode replay
./replayData.sh /path/to/data.csv sample

# Replay mode with debug
./replayData.sh /path/to/data.csv replay debug
```

**How it works**:
1. Validates input file format and headers
2. Creates EventGen configuration from templates
3. Copies sample data to EventGen directory
4. Starts EventGen processes
5. Monitors execution and cleans up processes

**Input Format Requirements**:
CSV file must contain headers: `index`, `_raw`, `sourcetype`

```csv
index,_raw,sourcetype,host
main,"2023-01-01 10:00:00,000 INFO Application started",application,server1
main,"2023-01-01 10:00:01,000 DEBUG Processing request",application,server1
```

**Configuration Templates**:
- Sample mode: Uses `eventgen_sample_configs.template`
- Replay mode: Uses `eventgen_replay_configs.template`

### bulkLoadData.sh

**Purpose**: Load large volumes of data efficiently using bulk operations.

**Usage**:
```bash
./bulkLoadData.sh <source_directory> <destination> [options]
```

**Example**:
```bash
# Basic bulk load
./bulkLoadData.sh /data/source /tmp/destination

# With custom options
./bulkLoadData.sh /data/source /tmp/destination --parallel=4 --batch-size=1000
```

### create_dummy_inputs.sh

**Purpose**: Generate dummy input data for testing purposes.

**Usage**:
```bash
./create_dummy_inputs.sh <output_file> <count> <type>
```

**Example**:
```bash
# Create 1000 dummy web logs
./create_dummy_inputs.sh /tmp/web_logs.csv 1000 web

# Create dummy security events
./create_dummy_inputs.sh /tmp/security_events.csv 500 security
```

## System Integration Scripts

### file_syslogGen.sh

**Purpose**: Generate syslog data from files and send to syslog servers.

**Usage**:
```bash
./file_syslogGen.sh <input_file> <syslog_server> <port>
```

**Example**:
```bash
# Send file content to syslog server
./file_syslogGen.sh /var/log/app.log syslog.example.com 514

# With custom facility and severity
./file_syslogGen.sh /var/log/app.log syslog.example.com 514 --facility=local0 --severity=info
```

**Features**:
- Reads log files line by line
- Converts to syslog format
- Sends to remote syslog servers
- Supports custom facility and severity levels

### message_syslogGen.sh

**Purpose**: Generate syslog messages from predefined templates or custom messages.

**Usage**:
```bash
./message_syslogGen.sh <message_template> <count> <syslog_server> <port>
```

**Example**:
```bash
# Generate 100 messages from template
./message_syslogGen.sh "User {{user}} logged in from {{ip}}" 100 syslog.example.com 514

# Use predefined template
./message_syslogGen.sh --template=login_events 50 syslog.example.com 514
```

### sanitise.sh

**Purpose**: Sanitize sensitive data from log files while preserving structure.

**Usage**:
```bash
./sanitise.sh <input_file> <output_file> <rules_file>
```

**Example**:
```bash
# Basic sanitization
./sanitise.sh /data/raw_logs.csv /data/sanitized_logs.csv ruleset_sanitise.txt

# With custom rules
./sanitise.sh /data/raw_logs.csv /data/sanitized_logs.csv custom_rules.txt
```

**Sanitization Rules**:
Based on `ruleset_sanitise.txt` configuration:
- IP address masking
- User name replacement
- Email address obfuscation
- Credit card number removal
- Custom pattern replacement

## Python Utilities

### raw_packet_from_csv.py

**Purpose**: Generate network packets from CSV data using Scapy.

**Requirements**:
- Must run as root (for packet manipulation)
- Requires Scapy library
- PyPy interpreter recommended

**Usage**:
```bash
# Run with PyPy
pypy raw_packet_from_csv.py

# Or with standard Python (if Scapy is available)
sudo python3 raw_packet_from_csv.py
```

**Input CSV Format**:
```csv
dst,src,sport,dport,payload
192.168.1.100,192.168.1.1,12345,80,GET / HTTP/1.1
192.168.1.101,192.168.1.1,12346,443,GET /api/data HTTP/1.1
```

**Features**:
- Reads packet specifications from CSV
- Creates IP/UDP packets with custom payloads
- Sends packets using Scapy's L3RawSocket
- Supports various network protocols

**Configuration**:
```python
# Default CSV path
payloadCSV = baseDir + "/artefacts/rsyslog_mapped_data/scapy_mapping.csv"

# Socket configuration
conf.L3socket = L3RawSocket
```

## Script Configuration

### Environment Variables

Most scripts support environment variable configuration:

```bash
# General configuration
export DF_CONFIG_DIR="/path/to/configs"
export DF_OUTPUT_DIR="/path/to/output"
export DF_LOG_LEVEL="INFO"

# Splunk configuration
export SPLUNK_HOST="splunk.example.com"
export SPLUNK_PORT="8089"
export SPLUNK_USER="admin"
export SPLUNK_PASSWORD="your-password"

# Syslog configuration
export SYSLOG_SERVER="syslog.example.com"
export SYSLOG_PORT="514"
export SYSLOG_FACILITY="local0"
```

### Configuration Files

#### EventGen Templates

**eventgen_sample_configs.template**:
```ini
## Sample mode configuration
mode = sample
sampletype = csv
backfill = -15m
interval = 36000
earliest = -60m
latest = now
end = 1
```

**eventgen_replay_configs.template**:
```ini
## Replay mode configuration
mode = replay
sampletype = csv
backfill = -15m
interval = 120
earliest = -60m
latest = now
end = 1
```

#### Token Templates

**eventgen_tokens.template**:
```ini
## Token configuration
token.0.token = \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3,6}
token.0.replacementType = timestamp
token.0.replacement = %Y-%m-%d %H:%M:%S,%f
```

## Script Development

### Creating New Scripts

When creating new utility scripts, follow these guidelines:

1. **Script Structure**:
```bash
#!/bin/bash
# ======================================================
# Script: script_name.sh
# Purpose: Brief description
# Version: 1.0
# Author: Your Name
# ======================================================

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${SCRIPT_DIR}/../configs/script_config.conf"

# Functions
function validate_input() {
    # Input validation logic
}

function main() {
    # Main script logic
}

# Script execution
main "$@"
```

2. **Error Handling**:
```bash
# Error handling
set -euo pipefail

# Trap errors
trap 'echo "Error occurred at line $LINENO"; exit 1' ERR

# Validate inputs
if [[ ! -f "$INPUT_FILE" ]]; then
    echo "ERROR: Input file not found: $INPUT_FILE"
    exit 1
fi
```

3. **Logging**:
```bash
# Logging function
function log() {
    local level="$1"
    shift
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$level] $*"
}

function log_info() {
    log "INFO" "$@"
}

function log_error() {
    log "ERROR" "$@" >&2
}
```

### Python Script Guidelines

1. **Structure**:
```python
#!/usr/bin/env python3
"""
Script: script_name.py
Purpose: Brief description
Version: 1.0
Author: Your Name
"""

import sys
import os
import argparse
import logging

def setup_logging():
    """Configure logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Script description')
    parser.add_argument('input_file', help='Input file path')
    parser.add_argument('--output', help='Output file path')
    return parser.parse_args()

def main():
    """Main function"""
    args = parse_args()
    setup_logging()
    
    # Main logic here
    logging.info("Script started")
    
if __name__ == '__main__':
    main()
```

2. **Error Handling**:
```python
import sys
import traceback

def handle_error(func):
    """Decorator for error handling"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {str(e)}")
            traceback.print_exc()
            sys.exit(1)
    return wrapper

@handle_error
def main():
    pass
```

## Best Practices

### 1. Script Security

- Validate all inputs
- Use absolute paths
- Implement proper error handling
- Avoid hardcoding sensitive data

### 2. Performance

- Use appropriate data structures
- Implement parallel processing where beneficial
- Monitor resource usage
- Optimize I/O operations

### 3. Maintainability

- Follow consistent coding standards
- Include comprehensive documentation
- Use meaningful variable names
- Implement modular design

### 4. Testing

- Create test cases for critical functions
- Test with various input scenarios
- Validate output formats
- Performance test with large datasets

## Troubleshooting

### Common Issues

1. **Permission Denied**:
```bash
# Check script permissions
ls -la script_name.sh

# Fix permissions
chmod +x script_name.sh
```

2. **Missing Dependencies**:
```bash
# Check Python dependencies
pip3 list | grep scapy

# Install missing dependencies
pip3 install -r requirements.txt
```

3. **Configuration Issues**:
```bash
# Check configuration file syntax
python3 -c "import configparser; c=configparser.ConfigParser(); c.read('config.conf')"

# Validate environment variables
env | grep DF_
```

### Debug Mode

Enable debug output for troubleshooting:

```bash
# Bash scripts
export DEBUG=1
./script_name.sh --debug

# Python scripts
python3 script_name.py --verbose --debug
```

### Log Analysis

Analyze script logs for issues:

```bash
# View recent logs
tail -f /var/log/data_framework.log

# Search for errors
grep ERROR /var/log/data_framework.log

# Analyze performance
grep "Execution time" /var/log/data_framework.log
```

This utility scripts guide provides comprehensive coverage of all available scripts and their usage. For specific script examples, refer to the `scripts/` and `python_scripts/` directories.
