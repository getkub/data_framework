# Data Framework Documentation

## Overview

The Data Framework is a comprehensive system for generating and injecting synthetic data for simulation purposes. It provides integrated solutions for EventGen-based data generation and Logstash-based data processing with Elasticsearch integration.

## Key Features

- **Dual Engine Support**: Both EventGen and Logstash data generation engines
- **Template-based Generation**: Easy-to-use template-based data generation
- **Real-time Processing**: Transform and enrich data in real-time pipelines
- **Multiple Output Destinations**: Splunk, Elasticsearch, files, HTTP endpoints, and more
- **Automated Deployment**: Full Ansible automation for deployment and management
- **Timestamp Automation**: Automatically changes event timestamps to arrive in real-time
- **Advanced Filtering**: Grok patterns, Ruby scripting, and conditional processing
- **GeoIP Enrichment**: Automatic geographic location enrichment
- **Performance Optimization**: Multi-processing, threading, and batch processing

## Architecture

The framework consists of two main data generation engines:

### EventGen Engine
- **Purpose**: Synthetic data generation based on samples and templates
- **Strengths**: High-performance, simple configuration, token-based replacement
- **Use Cases**: Log replay, synthetic data generation, timestamp manipulation

### Logstash Engine
- **Purpose**: Real-time data processing and transformation
- **Strengths**: Advanced filtering, pipeline processing, Elasticsearch integration
- **Use Cases**: Data enrichment, format conversion, complex routing

### Integration Points
- **Ansible Automation**: Unified deployment and management
- **Configuration Management**: Template-based configuration system
- **Output Destinations**: Multiple supported outputs for different use cases
- **Monitoring**: Comprehensive logging and performance monitoring

## Documentation Structure

This documentation is organized into two main sections:

### EventGen Documentation
- [EventGen Overview](eventgen/README.md) - EventGen engine overview and features
- [EventGen Architecture](eventgen/architecture.md) - Detailed system architecture
- [EventGen Quick Start](eventgen/quickstart.md) - Get started with EventGen
- [EventGen Configuration](eventgen/configuration.md) - Configuration reference and examples
- [EventGen Scripts](eventgen/scripts.md) - Utility scripts and automation
- [EventGen Troubleshooting](eventgen/troubleshooting.md) - Common issues and solutions
- [EventGen Glossary](eventgen/glossary.md) - EventGen-specific terminology

### Logstash Documentation
- [Logstash Overview](logstash/README.md) - Logstash engine overview and features
- [Logstash Quick Start](logstash/quickstart.md) - Get started with Logstash
- [Logstash Configuration](logstash/configuration.md) - Configuration reference and examples
- [Logstash Elasticsearch Integration](logstash/elasticsearch.md) - Elasticsearch integration guide
- [Logstash Troubleshooting](logstash/troubleshooting.md) - Common issues and solutions
- [Logstash Examples](logstash/examples/) - Real-world configuration examples

### Shared Documentation
- [Installation Guide](installation.md) - System setup and installation
- [Operations Guide](operation.md) - Day-to-day operations and management
- [Ansible Automation](ansible.md) - Ansible playbooks and automation
- [Utility Scripts](scripts.md) - Shared utility scripts
- [Troubleshooting](troubleshooting.md) - General troubleshooting guide
- [Glossary](glossary.md) - Comprehensive terminology reference

## Quick Links

### For New Users
- **Getting Started**: [Installation Guide](installation.md) → [EventGen Quick Start](eventgen/quickstart.md) or [Logstash Quick Start](logstash/quickstart.md)
- **Understanding Architecture**: [EventGen Architecture](eventgen/architecture.md) and [Logstash Overview](logstash/README.md)
- **Basic Configuration**: [EventGen Configuration](eventgen/configuration.md) or [Logstash Configuration](logstash/configuration.md)

### For Operators
- **Daily Operations**: [Operations Guide](operation.md)
- **Automation**: [Ansible Automation](ansible.md)
- **Monitoring**: [Troubleshooting](troubleshooting.md)
- **Scripts**: [Utility Scripts](scripts.md)

### For Developers
- **Advanced Configuration**: [EventGen Configuration](eventgen/configuration.md) and [Logstash Configuration](logstash/configuration.md)
- **Integration**: [Logstash Elasticsearch Integration](logstash/elasticsearch.md)
- **Examples**: [EventGen Examples](eventgen/) and [Logstash Examples](logstash/examples/)

### For Specific Use Cases

#### EventGen Use Cases
- **Data Replay**: [EventGen Quick Start](eventgen/quickstart.md) → replay existing data
- **Synthetic Generation**: [EventGen Configuration](eventgen/configuration.md) → generator input
- **Timestamp Manipulation**: [EventGen Configuration](eventgen/configuration.md) → token replacement

#### Logstash Use Cases
- **Data Simulation**: [Logstash Quick Start](logstash/quickstart.md) → generator input
- **Elasticsearch Integration**: [Logstash Elasticsearch Integration](logstash/elasticsearch.md) → direct indexing
- **Data Transformation**: [Logstash Configuration](logstash/configuration.md) → filters and enrichment
- **Real-time Processing**: [Logstash Configuration](logstash/configuration.md) → TCP/UDP inputs

## Choosing the Right Engine

### Use EventGen When:
- You need high-performance synthetic data generation
- You have existing log samples to replay
- You want simple token-based configuration
- You need Splunk integration
- You prefer template-based approaches

### Use Logstash When:
- You need real-time data processing
- You require advanced filtering and transformation
- You need Elasticsearch integration
- You want complex pipeline processing
- You need data enrichment (GeoIP, user agents, etc.)
- You prefer Grok pattern matching

### Use Both When:
- You want EventGen to generate data and Logstash to process it
- You need data generation with advanced transformation
- You want to leverage both engines' strengths
- You have complex simulation requirements

## Common Workflows

### Workflow 1: EventGen → Splunk
```
EventGen Generator → Token Replacement → Splunk Stream → Splunk Index
```

### Workflow 2: EventGen → Logstash → Elasticsearch
```
EventGen Generator → TCP/UDP → Logstash Filter → Elasticsearch Index
```

### Workflow 3: Logstash Direct Simulation → Elasticsearch
```
Logstash Generator → Filter/Enrichment → Elasticsearch Index
```

### Workflow 4: File Replay → Logstash → Elasticsearch
```
Log Files → Logstash Input → Grok Processing → Elasticsearch Index
```

## Dependencies

### System Requirements
- **Java 8+**: Required for Logstash
- **Python 3.8+**: Required for EventGen
- **Ansible 2.4+**: For automation and deployment
- **Memory**: Minimum 2GB RAM, recommended 4GB+
- **Disk**: Sufficient space for logs and temporary files

### Optional Components
- **Splunk**: For EventGen output and indexing
- **Elasticsearch**: For Logstash output and indexing
- **Redis**: For distributed Logstash deployments
- **Docker**: For containerized deployments

## Performance Characteristics

### EventGen Performance
- **Throughput**: 1,000 - 100,000+ events/second
- **Memory Usage**: 512MB - 2GB (depending on configuration)
- **CPU Usage**: 10-60% (depending on worker count)

### Logstash Performance
- **Throughput**: 100 - 10,000+ events/second (depending on filter complexity)
- **Memory Usage**: 1GB - 4GB (depending on pipeline complexity)
- **CPU Usage**: 20-80% (depending on filter operations)

## Security Considerations

### Data Protection
- **Sanitization**: Remove sensitive information from production data
- **Token Replacement**: Safe handling of sensitive patterns
- **Encryption**: SSL/TLS for network communications

### Access Control
- **Authentication**: Proper credential management
- **Authorization**: Role-based access control
- **Network Security**: Firewall rules and access controls

## Support and Community

### Documentation
- **Comprehensive Guides**: Detailed documentation for all components
- **Examples**: Real-world configuration examples
- **Best Practices**: Recommended approaches and patterns

### Community Support
- **Issues**: Bug tracking and feature requests
- **Forums**: Community discussion and support
- **Contributions**: Guidelines for contributing

## Version History

### Current Version
- **Dual Engine Support**: Both EventGen and Logstash engines
- **Enhanced Documentation**: Comprehensive documentation structure
- **Improved Integration**: Better Elasticsearch and Splunk integration
- **Automation**: Enhanced Ansible playbooks and roles

### Previous Versions
- **EventGen Only**: Basic EventGen-based data generation
- **Limited Documentation**: Basic setup and configuration guides
- **Manual Deployment**: Limited automation capabilities

## Getting Started

1. **Choose Your Engine**: Decide between EventGen and Logstash based on your needs
2. **Install Dependencies**: Ensure Java, Python, and required components are installed
3. **Follow Quick Start**: Use the appropriate quick start guide
4. **Configure Your Pipeline**: Set up inputs, filters, and outputs
5. **Test and Validate**: Verify your configuration and data flow
6. **Deploy and Monitor**: Use Ansible for deployment and set up monitoring

## Next Steps

Once you're familiar with the basics:

1. **Explore Examples**: Look at the examples directories for real-world configurations
2. **Advanced Configuration**: Learn about advanced features and optimizations
3. **Integration**: Set up integration with your existing systems
4. **Automation**: Implement Ansible-based deployment and management
5. **Monitoring**: Set up comprehensive monitoring and alerting

---

*This documentation covers the complete Data Framework with both EventGen and Logstash engines. Choose the documentation path that best fits your use case, or explore both engines for maximum flexibility.*
