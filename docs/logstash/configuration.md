# Logstash Configuration Guide

## Overview

Logstash configuration uses a powerful pipeline-based approach with three main stages: Input, Filter, and Output. This guide covers comprehensive configuration options for data simulation and Elasticsearch integration.

## Configuration Structure

Logstash configurations are structured as:

```ruby
# Pipeline configuration
input {
  # Input plugins configuration
}

filter {
  # Filter plugins configuration
}

output {
  # Output plugins configuration
}
```

### Multiple Pipelines

For complex scenarios, you can define multiple pipelines:

```ruby
# pipelines.yml
- pipeline.id: main
  path.config: "/etc/logstash/conf.d/main.conf"
  
- pipeline.id: enrichment
  path.config: "/etc/logstash/conf.d/enrichment.conf"
  
- pipeline.id: monitoring
  path.config: "/etc/logstash/conf.d/monitoring.conf"
```

## Input Configuration

### Generator Input

Generate synthetic data for testing:

```ruby
input {
  generator {
    lines => [
      "2023-10-10T10:00:00Z INFO Application started",
      "2023-10-10T10:00:01Z DEBUG Processing request",
      "2023-10-10T10:00:02Z INFO Request completed",
      "2023-10-10T10:00:03Z WARN High memory usage",
      "2023-10-10T10:00:04Z ERROR Database connection failed"
    ]
    count => 1000
    interval => 0.1
    message_format => "%{+yyyy-MM-dd'T'HH:mm:ss.SSSZ} %{LOGLEVEL:level} %{GREEDYDATA:message}"
  }
}
```

**Parameters**:
- `lines`: Array of message templates
- `count`: Number of times to generate each message
- `interval`: Delay between generations (seconds)
- `message_format`: Custom message format with field references

### File Input

Read data from log files:

```ruby
input {
  file {
    path => "/var/log/app/*.log"
    start_position => "beginning"
    sincedb_path => "/dev/null"
    exclude => "*.gz"
    codec => multiline {
      pattern => "^%{TIMESTAMP_ISO8601}"
      negate => true
      what => "previous"
    }
    tags => ["application", "file"]
  }
}
```

**Parameters**:
- `path`: File path patterns (supports wildcards)
- `start_position`: `beginning` or `end`
- `sincedb_path`: Database file for tracking file position
- `exclude`: Files to exclude
- `codec`: Data format and multiline handling

### TCP/UDP Input

Network-based input for real-time data:

```ruby
input {
  tcp {
    port => 5140
    host => "0.0.0.0"
    codec => json_lines
    tags => ["tcp", "realtime"]
  }
  
  udp {
    port => 514
    host => "0.0.0.0"
    codec => json
    tags => ["udp", "syslog"]
  }
}
```

**Parameters**:
- `port`: Listening port
- `host`: Bind address
- `codec`: Data format (json, plain, etc.)
- `tags`: Tags for identification

### HTTP Input

Receive data via HTTP endpoints:

```ruby
input {
  http {
    port => 8080
    host => "0.0.0.0"
    codec => json
    additional_codecs => ["application/json"]
    tags => ["http", "webhook"]
  }
}
```

### Cloud Service Inputs

Integration with cloud services:

```ruby
input {
  sqs {
    queue_name => "log-queue"
    region => "us-east-1"
    access_key_id => "${AWS_ACCESS_KEY}"
    secret_access_key => "${AWS_SECRET_KEY}"
    codec => json
  }
  
  pubsub {
    project_id => "my-project"
    topic => "log-topic"
    subscription => "log-subscription"
    json_key_file => "/path/to/service-account.json"
    codec => json
  }
}
```

## Filter Configuration

### Grok Pattern Matching

Extract structured data from unstructured logs:

```ruby
filter {
  grok {
    match => { 
      "message" => "%{COMBINEDAPACHELOG}"
    }
    tag_on_failure => ["_grokparsefailure"]
    overwrite => ["clientip", "ident", "auth", "timestamp", "verb", "request", "httpversion", "response", "bytes", "referrer", "agent"]
  }
}
```

**Common Grok Patterns**:
- `%{COMBINEDAPACHELOG}`: Apache combined log format
- `%{COMMONAPACHELOG}`: Apache common log format
- `%{TIMESTAMP_ISO8601}`: ISO 8601 timestamp
- `%{IP:clientip}`: IP address extraction
- `%{LOGLEVEL:level}`: Log level extraction

### Date Processing

Parse and normalize timestamps:

```ruby
filter {
  date {
    match => [ 
      "timestamp", "ISO8601",
      "log_time", "dd/MMM/yyyy:HH:mm:ss",
      "access_time", "dd/MMM/yyyy:HH:mm:ss.SSS"
    ]
    target => "@timestamp"
    add_field => { "original_timestamp" => "%{timestamp}" }
  }
}
```

### Mutate Filter

Field manipulation and enrichment:

```ruby
filter {
  mutate {
    # Add new fields
    add_field => { 
      "environment" => "production"
      "data_source" => "logstash_simulation"
    }
    
    # Convert data types
    convert => { 
      "response_code" => "integer"
      "response_size" => "integer"
      "processing_time" => "float"
    }
    
    # Replace values
    gsub => [ 
      "message", "[\r\n]+", " ",
      "user_agent", "\"", ""
    ]
    
    # Rename fields
    rename => { 
      "response" => "http_response"
      "bytes" => "response_bytes"
    }
    
    # Remove fields
    remove_field => ["temp_field", "debug_info"]
  }
}
```

### GeoIP Enrichment

Add geographic information to IP addresses:

```ruby
filter {
  if [client_ip] {
    geoip {
      source => "client_ip"
      target => "geoip"
      database => "/path/to/GeoLite2-City.mmdb"
      add_tag => ["geoip_success"]
    }
  } else {
    mutate { add_tag => ["geoip_missing"] }
  }
}
```

### Ruby Scripting

Custom processing logic:

```ruby
filter {
  ruby {
    code => '
      # Custom timestamp replacement
      patterns = [
        { "pattern" => "\\d{4}/\\d{2}/\\d{2}", "replacement" => "REPLACED_TIMESTAMP1" },
        { "pattern" => "\\d{2}/\\d{2}/\\d{2}", "replacement" => "REPLACED_TIMESTAMP2" },
        { "pattern" => "\\d{4}-\\d{2}-\\d{2}", "replacement" => "REPLACED_TIMESTAMP3" }
      ]
      
      patterns.each do |pattern|
        event.set("message", event.get("message").gsub(/#{pattern["pattern"]}/, pattern["replacement"]))
      end
      
      # Add computed fields
      if event.get("message") =~ /ERROR/
        event.set("severity", "high")
      elsif event.get("message") =~ /WARN/
        event.set("severity", "medium")
      else
        event.set("severity", "low")
      end
      
      # Extract URLs from message
      urls = event.get("message").scan(/https?:\/\/[^\s]+/)
      if urls.length > 0
        event.set("extracted_urls", urls)
      end
    '
  }
}
```

### Conditional Processing

Route events based on conditions:

```ruby
filter {
  # Log level based processing
  if [level] == "ERROR" {
    mutate { 
      add_tag => ["alert", "error"]
      add_field => { "priority" => "high" }
    }
  } else if [level] == "WARN" {
    mutate { 
      add_tag => ["warning"]
      add_field => { "priority" => "medium" }
    }
  }
  
  # Network zone classification
  if [client_ip] and [client_ip] =~ /^10\./ {
    mutate { add_field => { "network_zone" => "internal" } }
  } else if [client_ip] {
    mutate { add_field => { "network_zone" => "external" } }
  }
  
  # HTTP response categorization
  if [response_code] >= 200 and [response_code] < 300 {
    mutate { add_field => { "response_category" => "success" } }
  } else if [response_code] >= 400 and [response_code] < 500 {
    mutate { add_field => { "response_category" => "client_error" } }
  } else if [response_code] >= 500 {
    mutate { add_field => { "response_category" => "server_error" } }
  }
}
```

### User Agent Parsing

Parse and categorize user agents:

```ruby
filter {
  useragent {
    source => "agent"
    target => "user_agent"
  }
  
  if [user_agent][name] {
    mutate { 
      add_field => { "client_type" => "browser" }
      add_field => { "client_name" => "%{[user_agent][name]}" }
    }
  } else if [user_agent][device] {
    mutate { 
      add_field => { "client_type" => "device" }
      add_field => { "client_name" => "%{[user_agent][device]}" }
    }
  }
}
```

## Output Configuration

### Elasticsearch Output

Direct indexing to Elasticsearch:

```ruby
output {
  elasticsearch {
    hosts => ["http://localhost:9200"]
    index => "simulation-logs-%{+YYYY.MM.dd}"
    template_name => "simulation-logs"
    template_pattern => "simulation-logs-*"
    template_overwrite => true
    
    # Authentication
    user => "elastic"
    password => "${ELASTIC_PASSWORD}"
    
    # SSL/TLS configuration
    ssl => true
    cacert => "/path/to/ca.crt"
    
    # Performance tuning
    flush_size => 500
    idle_flush_time => 1
    
    # Document routing
    document_type => "_doc"
  }
}
```

### File Output

Write processed data to files:

```ruby
output {
  file {
    path => "/var/log/logstash/output"
    filename => "processed-%{+YYYY.MM.dd}.log"
    codec => json_lines
    create_if_deleted => true
    max_files => 10
    file_max_bytes => "100MB"
    gzip => false
  }
}
```

### HTTP Output

Send data to HTTP endpoints:

```ruby
output {
  http {
    url => "http://log-collector:8080/logs"
    http_method => "post"
    format => "json"
    headers => {
      "Content-Type" => "application/json"
      "Authorization" => "Bearer ${API_TOKEN}"
    }
    pool_max => 10
    pool_max_per_route => 2
    retry_non_idempotent => true
  }
}
```

### TCP/UDP Output

Send data via network protocols:

```ruby
output {
  tcp {
    host => "log-aggregator"
    port => 514
    codec => json
  }
  
  udp {
    host => "syslog-server"
    port => 514
    codec => json
  }
}
```

## Advanced Configuration

### Pipeline Workers

Optimize performance with worker configuration:

```ruby
# In logstash.yml
pipeline.workers: 4
pipeline.batch.size: 125
pipeline.batch.delay: 50
```

### Environment Variables

Use environment variables in configuration:

```ruby
input {
  tcp {
    port => "${TCP_PORT:5140}"
    host => "${BIND_HOST:0.0.0.0}"
  }
}

filter {
  mutate {
    add_field => { 
      "environment" => "${ENVIRONMENT:development}"
      "cluster" => "${CLUSTER_NAME:local}"
    }
  }
}

output {
  elasticsearch {
    hosts => ["${ELASTIC_HOST:http://localhost:9200}"]
    index => "${INDEX_PREFIX:logs}-%{+YYYY.MM.dd}"
  }
}
```

### Conditional Outputs

Route to different outputs based on conditions:

```ruby
output {
  if "alert" in [tags] {
    http {
      url => "http://alert-system:8080/webhook"
      http_method => "post"
      format => "json"
    }
  }
  
  if [level] == "ERROR" {
    file {
      path => "/var/log/errors"
      filename => "errors-%{+YYYY.MM.dd}.log"
    }
  }
  
  if [environment] == "production" {
    elasticsearch {
      hosts => ["http://prod-elasticsearch:9200"]
      index => "prod-logs-%{+YYYY.MM.dd}"
    }
  } else {
    elasticsearch {
      hosts => ["http://dev-elasticsearch:9200"]
      index => "dev-logs-%{+YYYY.MM.dd}"
    }
  }
}
```

## Configuration Templates

### Web Access Log Template

```ruby
input {
  tcp {
    port => 5140
    codec => json
  }
}

filter {
  # Parse web access log
  grok {
    match => { 
      "message" => "%{COMBINEDAPACHELOG}"
    }
  }
  
  # Extract and categorize
  mutate {
    add_field => { "log_type" => "web_access" }
    add_field => { "processed_at" => "%{@timestamp}" }
  }
  
  # GeoIP enrichment
  if [clientip] {
    geoip {
      source => "clientip"
      target => "geoip"
    }
  }
  
  # Response categorization
  if [response] >= 200 and [response] < 300 {
    mutate { add_field => { "status_category" => "success" } }
  } else if [response] >= 400 {
    mutate { add_field => { "status_category" => "error" } }
  }
}

output {
  elasticsearch {
    hosts => ["http://localhost:9200"]
    index => "web-access-%{+YYYY.MM.dd}"
  }
}
```

### Application Log Template

```ruby
input {
  generator {
    lines => [
      "2023-10-10T10:00:00Z INFO Application startup completed",
      "2023-10-10T10:00:01Z DEBUG User authentication: user123",
      "2023-10-10T10:00:02Z INFO Database connection established",
      "2023-10-10T10:00:03Z WARN Memory usage at 85%",
      "2023-10-10T10:00:04Z ERROR Failed to process request: timeout"
    ]
    count => 1000
    interval => 0.5
  }
}

filter {
  # Parse application log
  grok {
    match => { 
      "message" => "%{TIMESTAMP_ISO8601:timestamp} %{LOGLEVEL:level} %{GREEDYDATA:log_message}"
    }
  }
  
  # Add application context
  mutate {
    add_field => { 
      "application" => "myapp"
      "version" => "1.0.0"
      "environment" => "production"
    }
  }
  
  # Alert conditions
  if [level] == "ERROR" {
    mutate { add_tag => ["alert", "critical"] }
  }
}

output {
  elasticsearch {
    hosts => ["http://localhost:9200"]
    index => "application-logs-%{+YYYY.MM.dd}"
  }
  
  if "alert" in [tags] {
    http {
      url => "http://alert-manager:8080/alerts"
      http_method => "post"
      format => "json"
    }
  }
}
```

## Best Practices

### 1. Performance Optimization

- Use appropriate worker counts
- Optimize batch sizes
- Minimize complex Ruby scripts
- Use efficient Grok patterns

### 2. Error Handling

- Add failure tags for parsing errors
- Use conditional processing for missing fields
- Implement retry logic for outputs

### 3. Security

- Use environment variables for sensitive data
- Implement SSL/TLS for network communications
- Validate input data before processing

### 4. Monitoring

- Add processing timestamps
- Include pipeline metrics
- Use structured logging

This configuration guide provides comprehensive coverage of Logstash configuration options for data simulation and Elasticsearch integration. For specific examples, see the `examples/confs/` directory.
