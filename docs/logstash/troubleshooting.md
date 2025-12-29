# Logstash Troubleshooting Guide

## Overview

This guide covers common issues, error scenarios, and troubleshooting steps for Logstash data simulation and Elasticsearch integration. It's organized by component and includes diagnostic commands, common error messages, and solutions.

## General Troubleshooting

### System Requirements Check

Before diving into specific issues, verify your system meets requirements:

```bash
# Check Java version
java -version
# Should be Java 8 or higher

# Check Logstash version
./bin/logstash --version

# Check available memory
free -h

# Check disk space
df -h

# Check network connectivity
ping -c 3 google.com
```

### Log Locations

Logstash generates logs in various locations:

```bash
# Logstash logs
/var/log/logstash/
./logs/

# Pipeline logs
/var/log/logstash/pipeline/
./logs/pipeline/

# JVM logs
/var/log/logstash/jvm/
./logs/jvm/

# Dead letter queue
/var/lib/logstash/dead_letter_queue/
```

### Enable Debug Mode

For detailed troubleshooting, enable debug logging:

```bash
# Run with debug logging
./bin/logstash -f config.conf --log.level=DEBUG

# Run with pipeline debugging
./bin/logstash -f config.conf --pipeline.workers 1 --log.level=DEBUG

# Enable verbose output
./bin/logstash -f config.conf --verbose
```

## Configuration Issues

### Common Error Messages

#### 1. "Could not find any input plugin"

**Error**: `Could not find any input plugin named 'invalid_plugin'`

**Causes**:
- Typo in plugin name
- Plugin not installed
- Incorrect plugin syntax

**Solutions**:
```bash
# Check available plugins
./bin/logstash-plugin list

# Validate configuration syntax
./bin/logstash --config.test_and_exit -f config.conf

# Check plugin documentation
curl -s "https://www.elastic.co/guide/en/logstash/current/input-plugins.html"
```

#### 2. "Expected one of #, =>"

**Error**: `Expected one of #, => at line 5, column 12`

**Causes**:
- Missing comma in array
- Incorrect array syntax
- YAML/JSON format issues

**Solutions**:
```bash
# Check configuration syntax
./bin/logstash --config.test_and_exit -f config.conf

# Validate with online tool
# Use online YAML/JSON validators

# Fix syntax example
# Incorrect:
input {
  generator {
    lines => ["line1" "line2" "line3"]
  }
}

# Correct:
input {
  generator {
    lines => [
      "line1",
      "line2", 
      "line3"
    ]
  }
}
```

#### 3. "Unknown setting 'invalid_setting'"

**Error**: `Unknown setting 'invalid_setting' for plugin`

**Causes**:
- Typo in setting name
- Setting not supported by plugin version
- Incorrect plugin configuration

**Solutions**:
```bash
# Check plugin documentation
./bin/logstash-plugin list --verbose

# Validate specific plugin
./bin/logstash --config.test_and_exit -f config.conf

# Common plugin settings to check
# generator: lines, count, interval, message_format
# file: path, start_position, sincedb_path
# elasticsearch: hosts, index, template_name
```

### Pipeline Issues

#### 1. Pipeline Dead Letter Queue

**Symptoms**:
- Events not reaching output
- High memory usage
- Pipeline warnings

**Diagnostics**:
```bash
# Check dead letter queue
ls -la /var/lib/logstash/dead_letter_queue/

# Check pipeline stats
curl -X GET "localhost:9600/_node/stats/pipeline?pretty"

# Monitor pipeline flow
./bin/logstash -f config.conf --log.level=DEBUG | grep "pipeline"
```

**Solutions**:
```ruby
# Add error handling
filter {
  if "_grokparsefailure" in [tags] {
    mutate { add_tag => ["processing_error"] }
  }
}

output {
  # Add fallback output
  if "processing_error" in [tags] {
    file {
      path => "/var/log/processing_errors.log"
    }
  }
  
  # Add dead letter queue handling
  elasticsearch {
    # ... normal configuration
    dead_letter_queue_enable => true
    dead_letter_queue_path => "/var/lib/logstash/dead_letter"
  }
}
```

#### 2. Pipeline Bottlenecks

**Symptoms**:
- High CPU usage
- Slow processing
- Memory leaks

**Diagnostics**:
```bash
# Monitor pipeline performance
curl -X GET "localhost:9600/_node/stats/pipeline?pretty"

# Check JVM metrics
curl -X GET "localhost:9600/_node/stats/jvm?pretty"

# Monitor worker threads
top -p $(pgrep -f logstash)

# Check queue sizes
curl -X GET "localhost:9600/_node/stats/pipeline?pretty" | jq '.pipeline.events.queue'
```

**Solutions**:
```ruby
# Optimize worker count
# In logstash.yml
pipeline.workers: 4
pipeline.batch.size: 125
pipeline.batch.delay: 50

# Optimize filter performance
filter {
  # Use efficient grok patterns
  grok {
    match => { 
      "message" => "%{COMBINEDAPACHELOG}"
    }
    tag_on_failure => ["_grokparsefailure"]
  }
  
  # Avoid complex Ruby scripts when possible
  mutate {
    add_field => { "processed_at" => "%{@timestamp}" }
  }
}

# Optimize output settings
output {
  elasticsearch {
    # Increase batch size
    flush_size => 1000
    idle_flush_time => 5
    
    # Optimize connection pooling
    pool_max => 50
    pool_max_per_route => 10
  }
}
```

## Elasticsearch Integration Issues

### Connection Problems

#### 1. "Connection refused"

**Error**: `Logstash - java.lang.IllegalStateException: Cannot connect to Elasticsearch`

**Causes**:
- Elasticsearch not running
- Wrong host/port
- Firewall blocking connection
- Network issues

**Solutions**:
```bash
# Test Elasticsearch connectivity
curl -X GET "http://localhost:9200/"

# Check Elasticsearch status
curl -X GET "http://localhost:9200/_cluster/health?pretty"

# Verify network connectivity
telnet localhost 9200

# Check firewall rules
sudo ufw status
sudo iptables -L -n | grep 9200

# Fix configuration
output {
  elasticsearch {
    hosts => ["http://correct-host:9200"]
    # Add multiple hosts for failover
    hosts => ["http://es1:9200", "http://es2:9200"]
  }
}
```

#### 2. Authentication Failures

**Error**: `AuthenticationException[security] failed to authenticate user [logstash]`

**Causes**:
- Incorrect credentials
- User doesn't exist
- Insufficient permissions

**Solutions**:
```ruby
# Use environment variables for credentials
output {
  elasticsearch {
    hosts => ["http://localhost:9200"]
    user => "${ELASTIC_USER}"
    password => "${ELASTIC_PASSWORD}"
  }
}

# Or use API key authentication
output {
  elasticsearch {
    hosts => ["http://localhost:9200"]
    api_key => {
      id => "${ELASTIC_API_KEY_ID}"
      api_key => "${ELASTIC_API_KEY}"
    }
  }
}
```

#### 3. SSL/TLS Issues

**Error**: `SSLHandshakeException: PKIX path building failed`

**Causes**:
- Invalid certificates
- Certificate chain issues
- Protocol mismatches

**Solutions**:
```ruby
# Configure SSL properly
output {
  elasticsearch {
    hosts => ["https://secure-elasticsearch:9200"]
    ssl => true
    ssl_certificate_verification => true
    cacert => "/path/to/ca.crt"
    client_key => "/path/to/client.key"
    client_cert => "/path/to/client.crt"
    
    # For testing only (disable in production)
    ssl_certificate_verification => false
  }
}
```

### Indexing Issues

#### 1. "Index template missing"

**Error**: `MapperParsingException[mapping] failed to parse mapping`

**Causes**:
- Template not applied
- Invalid mapping syntax
- Template conflicts

**Solutions**:
```ruby
# Ensure template is applied
output {
  elasticsearch {
    hosts => ["http://localhost:9200"]
    template_name => "my-template"
    template_overwrite => true
    template => '{
      "index_patterns": ["logs-*"],
      "mappings": {
        "properties": {
          "@timestamp": {"type": "date"},
          "level": {"type": "keyword"},
          "message": {"type": "text"}
        }
      }
    }'
  }
}
```

#### 2. "Document parsing failed"

**Error**: `MapperParsingException[document] failed to parse document`

**Causes**:
- Invalid document structure
- Type conflicts
- Field mapping issues

**Solutions**:
```ruby
# Ensure proper field types
filter {
  # Convert to correct types
  mutate {
    convert => { 
      "response_code" => "integer"
      "response_size" => "integer"
      "timestamp" => "integer"
    }
  }
  
  # Handle null values
  mutate {
    replace => { 
      "empty_field" => "N/A"
      "null_value" => ""
    }
  }
}
```

## Performance Issues

### Memory Problems

#### Symptoms

- Out of memory errors
- High JVM heap usage
- Frequent garbage collection

#### Diagnostics

```bash
# Monitor JVM memory
curl -X GET "localhost:9600/_node/stats/jvm?pretty"

# Check heap usage
curl -X GET "localhost:9600/_node/stats/jvm?pretty" | jq '.jvm.mem.heap_used_percent'

# Monitor GC activity
curl -X GET "localhost:9600/_node/stats/jvm?pretty" | jq '.jvm.gc.collectors'
```

#### Solutions

```bash
# Increase JVM heap size
export LS_JAVA_OPTS="-Xmx2g -Xms2g"

# Or in logstash.yml
pipeline.workers: 2  # Reduce workers
pipeline.batch.size: 250  # Reduce batch size

# Configure GC settings
export LS_JAVA_OPTS="-XX:+UseG1GC -XX:+UseStringDeduplication"
```

### CPU Issues

#### Symptoms

- High CPU usage
- Slow processing
- System overload

#### Diagnostics

```bash
# Monitor CPU usage
top -p $(pgrep -f logstash)

# Check worker utilization
curl -X GET "localhost:9600/_node/stats/pipeline?pretty"

# Profile pipeline performance
./bin/logstash -f config.conf --pipeline.workers 1 --log.level=DEBUG
```

#### Solutions

```ruby
# Optimize filter performance
filter {
  # Use efficient grok patterns
  grok {
    match => { 
      "message" => "%{COMBINEDAPACHELOG}"
    }
    # Avoid expensive operations
    break_on_match => true
  }
  
  # Minimize Ruby script complexity
  mutate {
    add_field => { "processed_at" => "%{@timestamp}" }
  }
}

# Optimize output settings
output {
  elasticsearch {
    # Increase batch size for efficiency
    flush_size => 2000
    idle_flush_time => 10
    
    # Reduce network overhead
    http_compression => true
  }
}
```

## Input-Specific Issues

### Generator Input Problems

#### 1. No Events Generated

**Symptoms**:
- Generator input not producing events
- No output from pipeline

**Diagnostics**:
```bash
# Check generator configuration
grep -A 10 -B 5 "generator" config.conf

# Monitor pipeline stats
curl -X GET "localhost:9600/_node/stats/pipeline?pretty" | jq '.pipeline.events.in'

# Test with simple configuration
input {
  generator {
    lines => ["test message"]
    count => 1
  }
}

output {
  stdout { }
}
```

**Solutions**:
```ruby
# Fix generator configuration
input {
  generator {
    lines => [
      "2023-10-10T10:00:00Z INFO Test message 1",
      "2023-10-10T10:00:01Z INFO Test message 2"
    ]
    count => 100
    interval => 1  # Generate every second
    message_format => "%{+yyyy-MM-dd'T'HH:mm:ss.SSSZ} %{WORD:level} %{GREEDYDATA:message}"
  }
}
```

### File Input Problems

#### 1. File Not Found

**Error**: `FileNotFoundException: /path/to/file.log`

**Causes**:
- Incorrect file path
- File permissions
- File doesn't exist

**Solutions**:
```bash
# Check file existence
ls -la /path/to/file.log

# Check permissions
namei -r /path/to/file.log

# Use absolute paths
input {
  file {
    path => "/absolute/path/to/file.log"
    start_position => "beginning"
  }
}
```

#### 2. Multiline Issues

**Symptoms**:
- Events split incorrectly
- Incomplete log lines
- Timestamp parsing errors

**Diagnostics**:
```bash
# Test multiline configuration
echo -e "2023-10-10T10:00:00Z INFO Line 1\nContinuation of line 1" | ./bin/logstash -f test.conf

# Check sincedb
ls -la /var/lib/logstash/plugins/inputs/file/
```

**Solutions**:
```ruby
input {
  file {
    path => "/var/log/app/*.log"
    start_position => "beginning"
    sincedb_path => "/dev/null"  # Start fresh for testing
    codec => multiline {
      pattern => "^%{TIMESTAMP_ISO8601}"
      negate => true
      what => "previous"
      max_lines => 500
      max_bytes => "50KB"
    }
  }
}
```

## Filter-Specific Issues

### Grok Pattern Problems

#### 1. Pattern Match Failures

**Symptoms**:
- `_grokparsefailure` tags
- Fields not extracted
- Poor performance

**Diagnostics**:
```bash
# Test grok patterns online
# Use: https://grokdebug.herokuapp.com/

# Add debug output
filter {
  grok {
    match => { 
      "message" => "%{COMBINEDAPACHELOG}"
    }
    tag_on_failure => ["_grokparsefailure"]
  }
  
  if "_grokparsefailure" in [tags] {
    mutate {
      add_field => { "original_message" => "%{message}" }
      add_tag => ["debug_grok"]
    }
  }
}
```

**Solutions**:
```ruby
# Use simpler patterns
filter {
  grok {
    match => { 
      "message" => [
        "%{COMBINEDAPACHELOG}",
        "%{COMMONAPACHELOG}"
      ]
    }
    tag_on_failure => ["_grokparsefailure"]
  }
}

# Use dissect for structured data
filter {
  dissect {
    mapping => {
      "message" => "%{timestamp} %{level} %{message_part}"
    }
  }
}
```

### Ruby Script Issues

#### 1. Script Syntax Errors

**Error**: `RubyCompilationException: Syntax error`

**Causes**:
- Invalid Ruby syntax
- Missing quotes
- Incorrect method calls

**Solutions**:
```ruby
# Test Ruby syntax
filter {
  ruby {
    code => '
      # Simple test first
      event.set("test", "value")
    '
  }
}

# Use proper error handling
filter {
  ruby {
    code => '
      begin
        # Your code here
        event.set("field", "value")
      rescue => e
        event.set("ruby_error", e.message)
        event.tag("ruby_error")
      end
    '
  }
}
```

## Output-Specific Issues

### Elasticsearch Output Problems

#### 1. Bulk Rejection

**Error**: `ElasticsearchException[bulk] rejected execution`

**Causes**:
- Invalid document format
- Mapping conflicts
- Cluster issues

**Diagnostics**:
```bash
# Check Elasticsearch logs
tail -f /var/log/elasticsearch/elasticsearch.log

# Check cluster health
curl -X GET "http://localhost:9200/_cluster/health?pretty"

# Monitor indexing rate
curl -X GET "http://localhost:9200/_cat/count/logs?pretty"
```

**Solutions**:
```ruby
# Add document validation
filter {
  # Ensure required fields
  if ![timestamp] or ![message] {
    mutate { add_tag => ["validation_error"] }
  }
  
  # Convert to correct types
  mutate {
    convert => { 
      "response_code" => "integer"
      "response_size" => "integer"
    }
  }
}

output {
  elasticsearch {
    # Add retry logic
    retry_on_conflict => true
    retry_max_items => 100
    
    # Reduce batch size
    flush_size => 500
  }
}
```

## Network Issues

### Connectivity Problems

#### 1. Port Conflicts

**Symptoms**:
- Port already in use
- Connection refused
- Service startup failures

**Diagnostics**:
```bash
# Check port usage
netstat -tlnp | grep :9200
ss -tlnp | grep :9200

# Check process conflicts
ps aux | grep -E "(logstash|elasticsearch)"

# Test port availability
telnet localhost 9200
```

**Solutions**:
```bash
# Kill conflicting processes
pkill -f logstash
pkill -f elasticsearch

# Use different ports
# Logstash API
export LOGSTASH_API_HTTP_PORT=9601

# Elasticsearch
# Use different port in configuration
output {
  elasticsearch {
    hosts => ["http://localhost:9210"]
  }
}
```

## Recovery Procedures

### Data Recovery

```bash
# Check dead letter queue
ls -la /var/lib/logstash/dead_letter_queue/

# Recover failed events
# Process dead letter queue with separate pipeline

# Restart from checkpoint
# Remove sincedb files to reprocess from beginning
rm /var/lib/logstash/plugins/inputs/file/*.db
```

### Service Recovery

```bash
# Restart Logstash
sudo systemctl restart logstash

# Or manually
pkill -f logstash
./bin/logstash -f config.conf

# Check service status
sudo systemctl status logstash
curl -X GET "localhost:9600/_node/stats?pretty"
```

## Getting Help

### Log Collection

When seeking help, collect relevant information:

```bash
# System information
uname -a
java -version
./bin/logstash --version

# Configuration files
cat config.conf
cat logstash.yml

# Log files
tail -100 /var/log/logstash/logstash-plain.log
tail -100 /var/log/logstash/pipeline.log

# Environment variables
env | grep -E "(LOGSTASH|JAVA|LS_)"
```

### Debug Commands

```bash
# Full debug output
./bin/logstash -f config.conf --log.level=DEBUG --verbose

# Pipeline debugging
./bin/logstash -f config.conf --pipeline.workers 1

# Configuration testing
./bin/logstash --config.test_and_exit -f config.conf

# Plugin information
./bin/logstash-plugin list --verbose
```

### Support Channels

1. **Documentation**: Check relevant documentation sections
2. **Logs**: Review error logs for specific error messages
3. **Community**: Post questions with relevant logs and configuration
4. **Issues**: Create detailed bug reports with reproduction steps

This troubleshooting guide covers most common Logstash issues. For specific problems not covered here, refer to the official Elasticsearch documentation or community forums.
