# Glossary

## A

**Ansible**
- An open-source automation tool that the Data Framework uses for deployment, configuration management, and orchestration
- Used to automate the setup and execution of data generation jobs across multiple hosts

**API (Application Programming Interface)**
- A set of protocols and tools for building software applications
- In the context of Data Framework, refers to interfaces for data output and system integration

## C

**Configuration**
- Settings and parameters that control how data is generated, processed, and output
- Stored in INI-format files with sections for different data samples

**CSV (Comma-Separated Values)**
- A file format that stores tabular data in plain text, using commas to separate values
- Commonly used in Data Framework for sample data and input files

## D

**Data Framework**
- The overall system for generating and injecting synthetic data for simulation purposes
- Built on Splunk EventGen with additional automation and configuration layers

**Data Generation**
- The process of creating synthetic data based on templates, samples, and configuration parameters
- Can be done in real-time or replayed from existing data

## E

**EventGen**
- The core engine (Splunk EventGen) that powers the Data Framework's data generation capabilities
- Provides plugins, token replacement, and output management

**Environment Variables**
- System-wide variables that can be used to configure the Data Framework without hardcoding values in files
- Often used for sensitive information like passwords and hostnames

## F

**File Output**
- An output mode where generated data is written to local files
- Useful for testing, debugging, and offline processing

## G

**Generator Plugin**
- A plugin type in EventGen that controls how data is generated
- Examples include default, counter, replay, jinja, and weblog generators

## H

**HEC (HTTP Event Collector)**
- A Splunk feature that allows data to be sent via HTTP/HTTPS
- One of the output methods supported by the Data Framework

**Host**
- A target system or server where data is sent or where the framework is deployed
- Can refer to Splunk servers, data generators, or other systems

## I

**INI Format**
- A simple configuration file format with sections and key-value pairs
- Used throughout the Data Framework for configuration files

**Index**
- In Splunk terminology, a repository for data
- In CSV files, refers to the Splunk index where data should be stored

## J

**Jinja2**
- A modern and designer-friendly templating engine for Python
- Used in Data Framework for advanced templating and variable substitution

## L

**Log File**
- A file that records events or messages from software applications
- Can be used as input for data generation or as output for generated data

## M

**Multiprocessing**
- A programming technique where multiple processes are used to execute tasks concurrently
- In Data Framework, can be used to improve data generation performance

**Multithreading**
- A programming technique where multiple threads are used within a single process
- Alternative to multiprocessing for concurrent data generation

## O

**Output Mode**
- The method or destination for generated data
- Examples include file, splunkstream, httpevent, tcpout, udpout, syslogout

**Output Plugin**
- A plugin type in EventGen that controls where and how data is sent
- Handles different destinations like Splunk, files, HTTP endpoints, etc.

## P

**Plugin**
- A modular component that extends the functionality of the EventGen engine
- Three main types: generator, output, and rater plugins

**Process**
- An instance of a computer program that is being executed
- In Data Framework, refers to EventGen processes that generate data

## R

**Rate Control**
- Mechanisms to control the speed and volume of data generation
- Can be time-based, count-based, or volume-based

**Rater Plugin**
- A plugin type in EventGen that controls the rate of data generation
- Examples include config, counter, and perdayvolume raters

**Replay**
- A mode where existing data is replayed with updated timestamps
- Useful for testing with realistic data patterns

**Redis**
- An in-memory data structure store used as a message broker
- Used in distributed EventGen deployments for coordination

## S

**Sample**
- A dataset or template used as the basis for generating synthetic data
- Can be CSV files, raw text files, or other formats

**Sample Type**
- The format or type of input sample data
- Common types include csv, raw, and file

**Sanitization**
- The process of removing or masking sensitive information from data
- Important for privacy and compliance when using production data

**Script**
- A set of commands executed by an interpreter
- In Data Framework, refers to shell scripts and Python utilities for specialized tasks

**Sourcetype**
- In Splunk terminology, a format for data that determines how Splunk processes it
- In CSV files, specifies the sourcetype for generated events

**Splunk**
- A software platform for searching, monitoring, and analyzing machine-generated data
- Common destination for data generated by the Data Framework

**Splunk Stream**
- An output mode that sends data directly to Splunk using the Splunk Stream API
- Provides high-performance data ingestion

**Syslog**
- A standard logging protocol used for sending log messages
- Supported as both an input format and output destination

## T

**Template**
- A predefined pattern or structure used for generating data
- Can contain tokens that are replaced with dynamic values

**Timestamp**
- A sequence of characters that identifies when a particular event occurred
- Automatically updated by the Data Framework to ensure real-time data arrival

**Token**
- A placeholder in a template that gets replaced with dynamic values
- Can be timestamps, random values, file-based values, or lookup values

**Token Replacement**
- The process of substituting tokens in templates with actual values
- Core feature of the Data Framework for dynamic data generation

## V

**Variable**
- A symbolic name associated with a value that can change
- Used throughout the Data Framework for configuration and customization

## W

**Worker**
- A process or thread that performs data generation or output tasks
- Multiple workers can be used to improve performance

## Y

**YAML (YAML Ain't Markup Language)**
- A human-readable data serialization standard
- Used in Data Framework for Ansible configuration and variables

## Acronyms

| Acronym | Full Name | Description |
|----------|------------|-------------|
| API | Application Programming Interface | Interface for software communication |
| CSV | Comma-Separated Values | File format for tabular data |
| HEC | HTTP Event Collector | Splunk's HTTP data ingestion method |
| INI | Initialization | Configuration file format |
| JSON | JavaScript Object Notation | Data interchange format |
| SSH | Secure Shell | Network protocol for secure remote access |
| TCP | Transmission Control Protocol | Reliable network protocol |
| UDP | User Datagram Protocol | Fast but unreliable network protocol |
| URL | Uniform Resource Locator | Address for web resources |

## File Extensions

| Extension | Description | Usage in Data Framework |
|------------|-------------|------------------------|
| `.conf` | Configuration file | EventGen and framework configuration |
| `.csv` | Comma-Separated Values | Sample data and input files |
| `.log` | Log file | Output data and system logs |
| `.py` | Python script | Utility scripts and core engine |
| `.sh` | Shell script | Automation and utility scripts |
| `.yml` | YAML file | Ansible configuration and variables |
| `.txt` | Text file | Configuration templates and sample data |

## Common Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `generate` | Generate data using EventGen | `python3 __main__.py generate config.conf` |
| `replay` | Replay existing data | `./replayData.sh data.csv replay` |
| `ansible-playbook` | Run Ansible playbooks | `ansible-playbook -i hosts playbook.yml` |
| `pip3 install` | Install Python packages | `pip3 install -r requirements.txt` |

## Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `mode` | string | `sample` | Generation mode: sample, replay |
| `outputMode` | string | `file` | Output destination type |
| `interval` | integer | `60` | Generation interval in seconds |
| `count` | integer | `0` | Number of events to generate (0 = unlimited) |
| `backfill` | string | `-15m` | Time to backfill from |
| `sampletype` | string | `csv` | Sample data format |

## Error Types

| Error Type | Common Cause | Solution |
|-------------|---------------|----------|
| `ModuleNotFoundError` | Missing Python dependencies | Install required packages |
| `Connection refused` | Service not running or blocked | Check service status and firewall |
| `Permission denied` | File permission issues | Fix file permissions |
| `File not found` | Incorrect file paths | Use absolute paths or fix paths |

## Performance Metrics

| Metric | Description | Typical Values |
|---------|-------------|-----------------|
| Events/second | Data generation rate | 100-10,000+ depending on configuration |
| Memory usage | RAM consumption | Varies by data volume and complexity |
| CPU usage | Processor utilization | 10-80% depending on worker count |
| Network I/O | Data transfer rate | Depends on output destination |

## Security Terms

| Term | Description | Relevance |
|-------|-------------|------------|
| Sanitization | Removing sensitive data | Essential for privacy compliance |
| Encryption | Encoding data for security | Used for network communications |
| Authentication | Verifying identity | Required for Splunk and API access |
| Authorization | Controlling access | Determines what users can do |

This glossary provides comprehensive coverage of terminology used throughout the Data Framework documentation. For detailed explanations of specific concepts, refer to the relevant documentation sections.
