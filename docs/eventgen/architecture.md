# Architecture Overview

## System Architecture

The Data Framework is built on a modular architecture that separates concerns and provides flexibility in deployment and operation. The system consists of several layers that work together to provide synthetic data generation capabilities.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Data Framework                            │
├─────────────────────────────────────────────────────────────┤
│  User Interface & Automation Layer                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Ansible   │  │   Scripts   │  │   CLI Tools │         │
│  │  Playbooks  │  │  & Utils    │  │             │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
├─────────────────────────────────────────────────────────────┤
│  Configuration & Template Layer                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Config    │  │   Templates │  │   Samples   │         │
│  │  Templates  │  │   System    │  │   Data      │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
├─────────────────────────────────────────────────────────────┤
│  Core Processing Layer                                       │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Splunk EventGen Engine                     │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │ │
│  │  │ Generators  │  │  Transformers│  │  Outputters │    │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘    │ │
│  └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  Output & Destination Layer                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │    Splunk   │  │    Files    │  │   Network   │         │
│  │   Streams   │  │   System    │  │   Endpoints │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Splunk EventGen Engine

The heart of the framework is the Splunk EventGen engine, which provides:

- **Data Generation**: Creates synthetic data based on templates and samples
- **Timestamp Manipulation**: Automatically updates timestamps to current time
- **Rate Control**: Controls the rate and volume of data generation
- **Plugin Architecture**: Extensible through generator and output plugins

**Key Files:**
- `ansible/configs/ev_core/splunk_eventgen/eventgen_core.py` - Main engine
- `ansible/configs/ev_core/splunk_eventgen/lib/` - Core libraries
- `ansible/configs/ev_core/splunk_eventgen/lib/plugins/` - Plugin system

### 2. Configuration System

The configuration system uses a template-based approach:

- **Default Configurations**: Base templates for common scenarios
- **Token System**: Pattern matching and replacement for dynamic content
- **Output Configuration**: Flexible output destination configuration
- **Time Tokens**: Predefined timestamp patterns for various log formats

**Key Files:**
- `ansible/configs/df_configs/df_default_configs.txt` - Base configuration
- `ansible/configs/df_configs/df_time_tokens.txt` - Timestamp patterns
- `ansible/configs/df_configs/df_default_outputs.txt` - Output settings

### 3. Automation Layer

Ansible provides comprehensive automation capabilities:

- **Deployment**: Automated setup and configuration
- **Data Building**: Processes templates and builds data sets
- **Execution**: Runs data generation jobs
- **Management**: Manages the lifecycle of data generation

**Key Files:**
- `ansible/main_playbooks/replay.yml` - Main execution playbook
- `ansible/roles/` - Modular role definitions
- `ansible/group_vars/` - Configuration variables

### 4. Utility Scripts

Specialized scripts for specific tasks:

- **Data Replay**: Scripts for replaying existing data
- **Packet Generation**: Network packet generation from CSV data
- **Bulk Operations**: Scripts for bulk data operations
- **System Integration**: Scripts for system integration

**Key Files:**
- `scripts/replayData.sh` - Data replay functionality
- `python_scripts/raw_packet_from_csv.py` - Packet generation
- `scripts/bulkLoadData.sh` - Bulk data operations

## Data Flow

### 1. Configuration Phase
```
User Input → Template Processing → Configuration Generation → Validation
```

### 2. Data Generation Phase
```
Sample Data → Token Replacement → Timestamp Update → Rate Control → Output
```

### 3. Output Phase
```
Generated Data → Output Plugin → Destination → Confirmation
```

## Plugin Architecture

The framework supports a plugin architecture for extensibility:

### Generator Plugins
- **Default**: Basic data generation
- **Counter**: Sequential data generation
- **Replay**: Replay existing data
- **Jinja**: Template-based generation
- **Weblog**: Web log specific generation

### Output Plugins
- **Splunk Stream**: Direct Splunk integration
- **File**: File system output
- **HTTP**: HTTP endpoint output
- **TCP/UDP**: Network socket output
- **Syslog**: Syslog protocol output

### Rater Plugins
- **Config**: Configuration-based rate control
- **Counter**: Counter-based rate control
- **Per Day Volume**: Volume-based rate control

## Deployment Models

### 1. Standalone Mode
- Single machine deployment
- All components on one host
- Suitable for development and testing

### 2. Distributed Mode
- Multiple generation servers
- Centralized controller
- Redis for coordination
- Suitable for production scale

### 3. Cloud Mode
- Container-based deployment
- Scalable infrastructure
- Managed services integration

## Security Considerations

### 1. Data Security
- Sanitization of sensitive data
- Token-based data masking
- Secure data transmission

### 2. Access Control
- Role-based access control
- API authentication
- Network security

### 3. Compliance
- Data privacy compliance
- Audit logging
- Data retention policies

## Performance Characteristics

### 1. Scalability
- Horizontal scaling through multiple generators
- Load balancing across output destinations
- Configurable concurrency

### 2. Throughput
- Configurable generation rates
- Batch processing capabilities
- Optimized data pipelines

### 3. Resource Usage
- Memory-efficient processing
- CPU-optimized generation
- Network-aware output

## Integration Points

### 1. Splunk Integration
- Direct Splunk Stream API
- HEC (HTTP Event Collector) support
- Indexer acknowledgment

### 2. External Systems
- REST API integration
- Database connectivity
- Message queue support

### 3. Monitoring
- Performance metrics
- Health checks
- Alerting integration

## Configuration Hierarchy

```
1. Global Defaults (df_default_configs.txt)
2. Environment Variables
3. Ansible Group Variables
4. Playbook Variables
5. Runtime Parameters
```

This hierarchy allows for flexible configuration override at different levels while maintaining sensible defaults.

## Error Handling

### 1. Validation
- Configuration validation
- Data format validation
- Destination connectivity checks

### 2. Recovery
- Automatic retry mechanisms
- Fallback destinations
- Graceful degradation

### 3. Logging
- Comprehensive logging
- Error categorization
- Debug information

This architecture provides a robust, scalable, and flexible foundation for synthetic data generation while maintaining simplicity and ease of use.
