# Configuration Guide

## Overview

The Data Framework uses a flexible configuration system that allows you to customize every aspect of data generation, from input sources to output destinations. This guide covers all configuration options and best practices.

## Configuration Structure

Configuration files use the INI format with sections for different data samples:

```ini
[sample_name]
parameter1 = value1
parameter2 = value2

[another_sample]
parameter1 = value3
parameter2 = value4
```

## Core Configuration Parameters

### Basic Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `mode` | string | `sample` | Generation mode: `sample`, `replay` |
| `sampletype` | string | `csv` | Sample type: `csv`, `raw`, `file` |
| `backfill` | string | `-15m` | Time to backfill from (e.g., `-1h`, `-30m`) |
| `interval` | integer | `60` | Generation interval in seconds |
| `earliest` | string | `-60m` | Earliest time for generation |
| `latest` | string | `now` | Latest time for generation |
| `end` | integer/string | `1` | Number of intervals or end time |
| `count` | integer | `0` | Total number of events to generate (0 = unlimited) |

### Output Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `outputMode` | string | `file` | Output destination type |
| `fileName` | string | `/tmp/eventgen.test.log` | Output file path |
| `splunkHost` | string | `localhost` | Splunk host for splunkstream output |
| `splunkPort` | integer | `8089` | Splunk management port |
| `splunkUser` | string | `admin` | Splunk username |
| `splunkPass` | string | `changedme` | Splunk password |

## Output Modes

### 1. File Output

```ini
[your_sample]
outputMode = file
fileName = /path/to/output.log
```

**Additional Parameters:**
- `fileMaxBytes`: Maximum file size before rotation
- `fileBackupFiles`: Number of backup files to keep

### 2. Splunk Stream Output

```ini
[your_sample]
outputMode = splunkstream
splunkHost = your-splunk-server.com
splunkPort = 8089
splunkUser = admin
splunkPass = your-password
index = main
source = eventgen
sourcetype = generated_data
```

**Additional Parameters:**
- `index`: Splunk index to send data to
- `source`: Source name for events
- `sourcetype`: Sourcetype for events
- `host`: Host name for events

### 3. HTTP Event Output

```ini
[your_sample]
outputMode = httpevent
http_url = http://your-endpoint.com/api/events
http_method = POST
http_headers = {"Content-Type": "application/json"}
http_verify_ssl = true
```

**Additional Parameters:**
- `http_method`: HTTP method (GET, POST, PUT)
- `http_headers`: JSON object of HTTP headers
- `http_verify_ssl`: SSL verification (true/false)
- `http_timeout`: Request timeout in seconds

### 4. TCP/UDP Output

```ini
[your_sample]
outputMode = tcpout
server = your-server.com
port = 514
```

**For UDP:**
```ini
outputMode = udpout
server = your-server.com
port = 514
```

### 5. Syslog Output

```ini
[your_sample]
outputMode = syslogout
server = your-syslog-server.com
port = 514
protocol = udp
```

## Token Configuration

Tokens allow you to replace patterns in your data with dynamic values. The framework supports various token types for different use cases.

### Timestamp Tokens

Timestamp tokens replace date/time patterns with current timestamps:

```ini
# Basic timestamp format
token.0.token = \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}
token.0.replacementType = timestamp
token.0.replacement = %Y-%m-%d %H:%M:%S,%f

# ISO format
token.1.token = \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}
token.1.replacementType = timestamp
token.1.replacement = %Y-%m-%dT%H:%M:%S

# Apache log format
token.2.token = \d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2}.\d{3}
token.2.replacementType = timestamp
token.2.replacement = %d/%b/%Y:%H:%M:%S.%f
```

### Random Value Tokens

Generate random values for various data types:

```ini
# Random IP address
token.10.token = RANDOM_IP
token.10.replacementType = random
token.10.replacement = ip

# Random number
token.11.token = RANDOM_NUMBER
token.11.replacementType = random
token.11.replacement = integer
token.11.arg.min = 1
token.11.arg.max = 1000

# Random string
token.12.token = RANDOM_STRING
token.12.replacementType = random
token.12.replacement = string
token.12.arg.length = 10
```

### File-based Tokens

Replace tokens with values from files:

```ini
# Random line from file
token.20.token = RANDOM_HOSTNAME
token.20.replacementType = file
token.20.replacement = hostname.sample

# Sequential from file
token.21.token = SEQUENTIAL_USER
token.21.replacementType = file
token.21.replacement = userName.sample
token.21.arg.mode = sequential
```

### Lookup Tokens

Use lookup tables for value replacement:

```ini
# Lookup based on another field
token.30.token = LOOKUP_STATUS
token.30.replacementType = lookup
token.30.replacement = status_codes.csv
token.30.arg.field = status_code
token.30.arg.returnfield = status_description
```

## Sample Data Configuration

### CSV Sample Files

For CSV-based samples, the first row must contain headers:

```csv
index,_raw,sourcetype,host,source
main,"2023-01-01 10:00:00,000 INFO Application started",application,server1,/var/log/app.log
main,"2023-01-01 10:00:01,000 DEBUG Processing request",application,server1,/var/log/app.log
```

### Raw Sample Files

For raw text samples:

```ini
[your_sample]
mode = sample
sampletype = raw
sample = your_raw_sample.txt
```

### File-based Samples

Read from existing log files:

```ini
[your_sample]
mode = replay
sampletype = file
sample = /path/to/existing/log/file.log
```

## Rate Control Configuration

### Basic Rate Control

```ini
[your_sample]
interval = 60  # Generate every 60 seconds
count = 100    # Generate 100 events total
```

### Volume-based Rate Control

```ini
[your_sample]
rater = perdayvolume
perdayvolume = 1000000  # 1M events per day
```

### Backfill Configuration

```ini
[your_sample]
backfill = -1h    # Start 1 hour ago
earliest = -2h    # Don't go earlier than 2 hours ago
latest = now      # Don't go later than now
```

## Advanced Configuration

### Multi-process Configuration

```ini
[your_sample]
generatorWorkers = 4    # Number of generator processes
outputWorkers = 2       # Number of output processes
generatorQueueSize = 500 # Queue size for generators
```

### Threading vs Multiprocessing

```ini
[your_sample]
multithread = true      # Use threading instead of multiprocessing
```

### Profiling Configuration

```ini
[your_sample]
profiler = true         # Enable performance profiling
```

## Environment Variables

You can use environment variables in configuration:

```ini
[your_sample]
splunkHost = ${SPLUNK_HOST}
splunkPort = ${SPLUNK_PORT}
splunkUser = ${SPLUNK_USER}
splunkPass = ${SPLUNK_PASSWORD}
```

Set environment variables:

```bash
export SPLUNK_HOST=your-splunk-server.com
export SPLUNK_PORT=8089
export SPLUNK_USER=admin
export SPLUNK_PASSWORD=your-password
```

## Configuration Templates

### Web Server Logs

```ini
[web_access]
mode = sample
sampletype = csv
sample = weblog.sample
outputMode = splunkstream
splunkHost = your-splunk-server.com
splunkPort = 8089
splunkUser = admin
splunkPass = your-password
index = web
sourcetype = access_combined
interval = 1
count = 10000

# Apache timestamp format
token.0.token = \d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2}.\d{3}
token.0.replacementType = timestamp
token.0.replacement = %d/%b/%Y:%H:%M:%S.%f

# Random IP addresses
token.1.token = \d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}
token.1.replacementType = random
token.1.replacement = ip
```

### Application Logs

```ini
[app_logs]
mode = sample
sampletype = csv
sample = application.sample
outputMode = file
fileName = /tmp/application.log
interval = 5
count = 5000

# Application timestamp format
token.0.token = \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}
token.0.replacementType = timestamp
token.0.replacement = %Y-%m-%d %H:%M:%S,%f

# Random log levels
token.1.token = (INFO|DEBUG|WARN|ERROR)
token.1.replacementType = random
token.1.replacement = choice
token.1.arg.choices = INFO,DEBUG,WARN,ERROR
```

### Security Events

```ini
[security_events]
mode = sample
sampletype = csv
sample = security.sample
outputMode = httpevent
http_url = https://your-siem.com/api/events
http_method = POST
http_headers = {"Authorization": "Bearer ${API_TOKEN}", "Content-Type": "application/json"}
interval = 10
count = 1000

# Security timestamp format
token.0.token = \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z
token.0.replacementType = timestamp
token.0.replacement = %Y-%m-%dT%H:%M:%SZ

# Random user IDs
token.1.token = user_\d+
token.1.replacementType = random
token.1.replacement = string
token.1.arg.prefix = user_
token.1.arg.length = 8
```

## Best Practices

### 1. Configuration Organization

- Use descriptive sample names
- Group related configurations
- Use environment variables for sensitive data
- Keep configuration files under version control

### 2. Performance Optimization

- Adjust worker counts based on available resources
- Use appropriate queue sizes
- Consider threading vs multiprocessing based on workload

### 3. Security

- Never hardcode passwords in configuration files
- Use environment variables for credentials
- Implement proper access controls on configuration files

### 4. Monitoring

- Enable logging for troubleshooting
- Use profiling for performance analysis
- Monitor resource usage

## Validation

The framework validates configurations before execution:

### Syntax Validation

- Check INI format
- Validate parameter names and values
- Verify required parameters are present

### Runtime Validation

- Check file permissions
- Verify network connectivity
- Validate sample data format

### Common Validation Errors

1. **Missing required parameters**: Ensure all required parameters are present
2. **Invalid file paths**: Check file permissions and existence
3. **Network connectivity**: Verify destination accessibility
4. **Token syntax**: Validate regular expression patterns

## Troubleshooting Configuration Issues

### Enable Debug Logging

```bash
python3 __main__.py generate --verbosity 2 your_config.conf
```

### Test Configuration Syntax

```bash
python3 -c "
import configparser
config = configparser.ConfigParser()
config.read('your_config.conf')
print('Configuration is valid')
"
```

### Check Sample Data

```bash
# Verify CSV format
head -5 your_sample.csv
# Check headers
head -1 your_sample.csv | grep -E "(index|_raw|sourcetype)"
```

This configuration guide provides comprehensive coverage of all configuration options. For specific parameter details, refer to the Configuration Reference document.
