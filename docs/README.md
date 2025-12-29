# Data Framework Documentation

## Overview

The Data Framework is a comprehensive system for generating and injecting synthetic data for simulation purposes. It provides a simplified approach to data generation compared to traditional tools like EventGen, with features like templated data generation, automatic timestamp updates, and flexible deployment options.

## Key Features

- **Simple and Templated**: Easy-to-use template-based data generation
- **Remote Template Hosting**: Data templates can be hosted in separate repositories
- **Simplified Architecture**: More straightforward than EventGen and other generators
- **Real-time Timestamps**: Automatically changes event timestamps to arrive in real-time
- **Multiple Output Formats**: Supports various output destinations (Splunk, files, etc.)
- **Ansible Automation**: Full automation support for deployment and operations

## Architecture

The framework consists of several key components:

1. **Core Engine**: Splunk EventGen-based data generation engine
2. **Configuration Layer**: Template-based configuration system
3. **Automation Layer**: Ansible playbooks for deployment and management
4. **Utility Scripts**: Python and shell scripts for specialized operations
5. **Sample Data**: Extensive collection of sample data templates

## Documentation Structure

This documentation is organized into the following sections:

### Getting Started
- [Installation Guide](installation.md) - Setup and installation instructions
- [Quick Start](quickstart.md) - Get up and running quickly
- [Configuration Guide](configuration.md) - Detailed configuration options

### Core Components
- [Data Generation Engine](data-generation.md) - Core EventGen functionality
- [Template System](templates.md) - Template creation and management
- [Output Destinations](outputs.md) - Supported output formats and destinations

### Operations
- [Operations Guide](operation.md) - Day-to-day operations
- [Automation with Ansible](ansible.md) - Ansible playbooks and automation
- [Utility Scripts](scripts.md) - Available utility scripts

### Advanced Topics
- [Architecture Overview](architecture.md) - Detailed system architecture
- [Performance Tuning](performance.md) - Optimization and performance
- [Troubleshooting](troubleshooting.md) - Common issues and solutions

### Reference
- [Configuration Reference](config-reference.md) - Complete configuration reference
- [API Documentation](api.md) - API reference (if applicable)
- [Glossary](glossary.md) - Terms and definitions

## Quick Links

- **New Users**: Start with [Installation Guide](installation.md) and [Quick Start](quickstart.md)
- **Operators**: See [Operations Guide](operation.md) and [Automation with Ansible](ansible.md)
- **Developers**: Refer to [Architecture Overview](architecture.md) and [API Documentation](api.md)

## Dependencies

- **Python 3.8+**: Core runtime requirement
- **Ansible 2.4+**: For automation and deployment
- **Splunk**: Target platform for data ingestion (optional)

## Support

For support and questions:
1. Check the [Troubleshooting](troubleshooting.md) guide
2. Review the [Configuration Reference](config-reference.md)
3. Consult the [Glossary](glossary.md) for terminology

## Version History

- **Current**: Active development with enhanced template system
- **Previous**: Basic EventGen integration with limited automation

---

*This documentation is continuously updated. Last updated: $(date)*
