# Logstash Quick Start Guide

## Getting Started Quickly

This guide will help you get Logstash up and running in minutes for data simulation and Elasticsearch integration. Follow these steps to start generating and processing synthetic data.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Java 8+** - Core runtime requirement
- **Logstash 7.x+** - Download from Elastic
- **Elasticsearch** - For data indexing (optional but recommended)
- **curl** - For testing HTTP endpoints

## Step 1: Install Logstash

### Option A: Download and Install

```bash
# Download Logstash
wget https://artifacts.elastic.co/downloads/logstash/logstash-7.17.0-linux-x86_64.tar.gz

# Extract
tar -xzf logstash-7.17.0-linux-x86_64.tar.gz

# Navigate to directory
cd logstash-7.17.0/
```

### Option B: Package Manager

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install logstash

# CentOS/RHEL
sudo yum install logstash

# macOS with Homebrew
brew tap elastic/tap
brew install elastic/tap/logstash-full
```

## Step 2: Basic Configuration

Create your first Logstash configuration file:

```bash
# Create configuration directory
mkdir -p ~/logstash-configs

# Create basic configuration
cat > ~/logstash-configs/quickstart.conf << 'EOF'
input {
  generator {
    lines => [
      "2023-10-10T10:00:00Z INFO Starting application",
      "2023-10-10T10:00:01Z DEBUG Processing request from 192.168.1.100",
      "2023-10-10T10:00:02Z INFO Request completed successfully",
      "2023-10-10T10:00:03Z WARN High memory usage detected",
      "2023-10-10T10:00:04Z ERROR Database connection failed"
    ]
    count => 100
    interval => 1
  }
}

filter {
  # Parse timestamp
  date {
    match => [ "message", "ISO8601" ]
  }

  # Extract log level
  grok {
    match => { 
      "message" => "%{TIMESTAMP_ISO8601:timestamp} %{LOGLEVEL:log_level} %{GREEDYDATA:log_message}" 
    }
  }

  # Add processing timestamp
  mutate {
    add_field => { 
      "processed_at" => "%{@timestamp}"
      "environment" => "test"
    }
  }
}

output {
  stdout {
    codec => rubydebug
  }
  
  # Uncomment if you have Elasticsearch running
  # elasticsearch {
  #   hosts => ["http://localhost:9200"]
  #   index => "quickstart-logs-%{+YYYY.MM.dd}"
  # }
}
EOF
```

## Step 3: Run Your First Pipeline

### Test the Configuration

```bash
# Test configuration syntax
./bin/logstash --config.test_and_exit -f ~/logstash-configs/quickstart.conf
```

### Run the Pipeline

```bash
# Start Logstash with auto-reload
./bin/logstash -f ~/logstash-configs/quickstart.conf --config.reload.automatic
```

You should see output similar to:
```
{
       "message" => "2023-10-10T10:00:00Z INFO Starting application",
      "@version" => "1",
    "@timestamp" => 2023-10-10T10:00:00.000Z,
          "host" => "hostname",
    "log_level" => "INFO",
  "log_message" => "Starting application",
  "processed_at" => "2023-10-10T10:00:00.000Z",
   "environment" => "test"
}
```

## Step 4: Elasticsearch Integration

### Start Elasticsearch (if not running)

```bash
# Using Docker
docker run -d --name elasticsearch -p 9200:9200 -e "discovery.type=single-node" elasticsearch:7.17.0

# Or download and run locally
# Follow Elasticsearch installation guide
```

### Update Configuration for Elasticsearch

Edit your configuration to enable Elasticsearch output:

```bash
cat > ~/logstash-configs/elasticsearch.conf << 'EOF'
input {
  generator {
    lines => [
      "2023-10-10T10:00:00Z INFO Web server started on port 8080",
      "2023-10-10T10:00:01Z DEBUG GET /api/users from 192.168.1.100",
      "2023-10-10T10:00:02Z INFO POST /api/data from 192.168.1.101",
      "2023-10-10T10:00:03Z WARN Rate limit exceeded for 192.168.1.102",
      "2023-10-10T10:00:04Z ERROR Database timeout occurred"
    ]
    count => 1000
    interval => 0.1
  }
}

filter {
  # Parse web access logs
  grok {
    match => { 
      "message" => "%{TIMESTAMP_ISO8601:timestamp} %{LOGLEVEL:log_level} %{GREEDYDATA:log_message}" 
    }
  }

  # Extract IP addresses from log messages
  grok {
    match => { 
      "log_message" => "from %{IP:client_ip}" 
    }
    tag_on_failure => ["_grokparsefailure_ip"]
  }

  # Add GeoIP information for client IPs
  if [client_ip] {
    geoip {
      source => "client_ip"
      target => "geoip"
    }
  }

  # Parse HTTP methods and endpoints
  grok {
    match => { 
      "log_message" => "%{WORD:http_method} %{URIPATH:uri_path}" 
    }
    tag_on_failure => ["_grokparsefailure_http"]
  }

  # Add computed fields
  mutate {
    add_field => { 
      "data_source" => "logstash_simulation"
      "processing_time" => "%{@timestamp}"
    }
  }
}

output {
  elasticsearch {
    hosts => ["http://localhost:9200"]
    index => "simulation-logs-%{+YYYY.MM.dd}"
    template_name => "simulation-logs"
    template_pattern => "simulation-logs-*"
  }
  
  stdout {
    codec => rubydebug
  }
}
EOF
```

### Run with Elasticsearch Output

```bash
./bin/logstash -f ~/logstash-configs/elasticsearch.conf --config.reload.automatic
```

## Step 5: Verify Data in Elasticsearch

### Check Index Creation

```bash
# List indices
curl -X GET "localhost:9200/_cat/indices?v"

# Should show simulation-logs-YYYY.MM.dd
```

### Search for Documents

```bash
# Search for all documents
curl -X GET "localhost:9200/simulation-logs-*/_search?pretty"

# Search for specific log levels
curl -X GET "localhost:9200/simulation-logs-*/_search?q=log_level:ERROR&pretty"

# Search for GeoIP enriched data
curl -X GET "localhost:9200/simulation-logs-*/_search?q=geoip.country_name:*&pretty"
```

## Step 6: Advanced Data Simulation

### Web Server Log Simulation

```bash
cat > ~/logstash-configs/webserver.conf << 'EOF'
input {
  generator {
    lines => [
      '192.168.1.100 - - [10/Oct/2023:13:55:36 +0000] "GET /index.html HTTP/1.1" 200 2326 "-" "Mozilla/5.0"',
      '192.168.1.101 - - [10/Oct/2023:13:55:37 +0000] "POST /api/login HTTP/1.1" 200 145 "http://example.com" "Mozilla/5.0"',
      '192.168.1.102 - - [10/Oct/2023:13:55:38 +0000] "GET /dashboard HTTP/1.1" 403 512 "-" "curl/7.68.0"',
      '192.168.1.103 - - [10/Oct/2023:13:55:39 +0000] "PUT /api/users/123 HTTP/1.1" 200 89 "http://example.com/admin" "Mozilla/5.0"',
      '192.168.1.104 - - [10/Oct/2023:13:55:40 +0000] "DELETE /api/sessions/456 HTTP/1.1" 200 23 "-" "Python-requests/2.25.1"'
    ]
    count => 5000
    interval => 0.01
  }
}

filter {
  # Parse Apache combined log format
  grok {
    match => { 
      "message" => "%{COMBINEDAPACHELOG}" 
    }
  }

  # Parse user agent
  useragent {
    source => "agent"
    target => "user_agent"
  }

  # Add GeoIP for client IP
  geoip {
    source => "clientip"
    target => "geoip"
  }

  # Convert response to integer
  mutate {
    convert => { "response" => "integer" }
    convert => { "bytes" => "integer" }
  }

  # Add response category
  if [response] >= 200 and [response] < 300 {
    mutate { add_field => { "response_category" => "success" } }
  } else if [response] >= 400 and [response] < 500 {
    mutate { add_field => { "response_category" => "client_error" } }
  } else if [response] >= 500 {
    mutate { add_field => { "response_category" => "server_error" } }
  }

  # Extract endpoint type
  if [request] =~ "^/api/" {
    mutate { add_field => { "endpoint_type" => "api" } }
  } else if [request] =~ "\.(html|css|js|png|jpg|gif)$" {
    mutate { add_field => { "endpoint_type" => "static" } }
  } else {
    mutate { add_field => { "endpoint_type" => "other" } }
  }
}

output {
  elasticsearch {
    hosts => ["http://localhost:9200"]
    index => "webserver-logs-%{+YYYY.MM.dd}"
  }
  
  stdout {
    codec => dots
  }
}
EOF
```

### Run Web Server Simulation

```bash
./bin/logstash -f ~/logstash-configs/webserver.conf --config.reload.automatic
```

## Step 7: Real-time Data Processing

### TCP Input for Real-time Data

```bash
cat > ~/logstash-configs/tcp_input.conf << 'EOF'
input {
  tcp {
    port => 5140
    codec => json_lines
  }
}

filter {
  # Add processing timestamp
  mutate {
    add_field => { 
      "received_at" => "%{@timestamp}"
      "processor" => "logstash-tcp"
    }
  }

  # Validate required fields
  if ![message] or ![level] {
    mutate { add_tag => ["_validation_error"] }
  }
}

output {
  elasticsearch {
    hosts => ["http://localhost:9200"]
    index => "realtime-logs-%{+YYYY.MM.dd}"
  }
  
  stdout {
    codec => rubydebug
  }
}
EOF
```

### Send Test Data to TCP Input

```bash
# Send JSON data to TCP port
echo '{"message": "Test log message", "level": "INFO", "source": "test"}' | nc localhost 5140

# Send multiple messages
for i in {1..10}; do
  echo "{\"message\": \"Test message $i\", \"level\": \"INFO\", \"source\": \"test\", \"counter\": $i}" | nc localhost 5140
  sleep 0.5
done
```

## Common Configuration Patterns

### 1. File Input with Multiple Formats

```ruby
input {
  file {
    path => "/var/log/app/*.log"
    start_position => "beginning"
    sincedb_path => "/dev/null"
    codec => multiline {
      pattern => "^%{TIMESTAMP_ISO8601}"
      negate => true
      what => "previous"
    }
  }
}
```

### 2. Conditional Processing

```ruby
filter {
  if [level] == "ERROR" {
    mutate { add_tag => ["alert"] }
  }
  
  if [clientip] and [clientip] =~ "^10\." {
    mutate { add_field => { "network_zone" => "internal" } }
  } else {
    mutate { add_field => { "network_zone" => "external" } }
  }
}
```

### 3. Multiple Outputs

```ruby
output {
  elasticsearch {
    hosts => ["http://localhost:9200"]
    index => "logs-%{+YYYY.MM.dd}"
  }
  
  file {
    path => "/var/log/logstash/output.log"
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

## Troubleshooting Common Issues

### 1. Configuration Syntax Errors

```bash
# Test configuration
./bin/logstash --config.test_and_exit -f your_config.conf

# Check for syntax errors
./bin/logstash -f your_config.conf --log.level=debug
```

### 2. Elasticsearch Connection Issues

```bash
# Test Elasticsearch connectivity
curl -X GET "localhost:9200/"

# Check cluster health
curl -X GET "localhost:9200/_cluster/health?pretty"
```

### 3. Performance Issues

```bash
# Monitor Logstash performance
./bin/logstash -f your_config.conf --pipeline.workers 4 --pipeline.batch.size 125

# Check JVM heap usage
curl -X GET "localhost:9600/_node/stats/jvm?pretty"
```

## Next Steps

Once you have the basic setup working:

1. **Explore Examples**: Look at the configuration examples in `examples/confs/`
2. **Advanced Filtering**: Learn about grok patterns and Ruby scripting
3. **Performance Tuning**: Optimize pipeline workers and batch sizes
4. **Monitoring**: Set up monitoring and alerting
5. **Security**: Configure TLS/SSL and authentication

## Getting Help

- **Documentation**: Check the full documentation in the `docs/` directory
- **Configuration Examples**: See `examples/confs/` for real-world examples
- **Troubleshooting**: Refer to the troubleshooting guide
- **Community**: Join the Elastic community forums for support

## Quick Reference

### Essential Commands

```bash
# Test configuration
./bin/logstash --config.test_and_exit -f config.conf

# Run with auto-reload
./bin/logstash -f config.conf --config.reload.automatic

# Run with debug logging
./bin/logstash -f config.conf --log.level=debug

# Check pipeline stats
curl -X GET "localhost:9600/_node/stats/pipeline?pretty"
```

### Common Input Plugins

- `generator` - Generate synthetic data
- `file` - Read from files
- `tcp/udp` - Network input
- `http` - HTTP endpoint input
- `beats` - Elastic Beats input

### Common Filter Plugins

- `grok` - Pattern matching
- `mutate` - Field manipulation
- `date` - Date parsing
- `geoip` - Geographic IP data
- `ruby` - Custom scripting

### Common Output Plugins

- `elasticsearch` - Elasticsearch output
- `file` - File output
- `stdout` - Console output
- `http` - HTTP endpoint output

You're now ready to use Logstash for data simulation and Elasticsearch integration! For more advanced usage, refer to the detailed documentation.
