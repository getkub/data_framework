# Logstash Elasticsearch Integration

## Overview

Logstash provides seamless integration with Elasticsearch for indexing, searching, and analyzing generated data. This guide covers comprehensive Elasticsearch integration patterns for data simulation scenarios.

## Integration Architecture

```
┌─────────────────────────────────────────────────────────┐
│                Data Flow Architecture                    │
├─────────────────────────────────────────────────────────┤
│  Logstash    │    Elasticsearch    │  Kibana        │
│  ┌─────────┐  │  ┌─────────────┐  │  ┌───────────┐  │
│  │  Input   │  │  │   Indexing   │  │  │Visualization│  │
│  │  Filter   │──▶│  │             │──▶│  │             │──▶│
│  │  Output   │  │  │   Storage   │  │  │   Dashboards│  │
│  └─────────┘  │  └─────────────┘  │  └───────────┘  │
│                 │                   │                 │
│                 │                   │                 │
└─────────────────┴───────────────────┴─────────────────┘
```

## Basic Elasticsearch Output

### Simple Configuration

```ruby
output {
  elasticsearch {
    hosts => ["http://localhost:9200"]
    index => "simulation-logs-%{+YYYY.MM.dd}"
  }
}
```

### Advanced Configuration

```ruby
output {
  elasticsearch {
    # Connection settings
    hosts => ["https://prod-elasticsearch:9200", "https://backup-elasticsearch:9200"]
    sniffing => true
    sniffing_delay => 5
    
    # Authentication
    user => "elastic"
    password => "${ELASTIC_PASSWORD}"
    
    # SSL/TLS
    ssl => true
    cacert => "/etc/ssl/ca.crt"
    client_key => "/etc/ssl/client.key"
    client_cert => "/etc/ssl/client.crt"
    
    # Index management
    index => "simulation-logs-%{+YYYY.MM.dd}"
    template_name => "simulation-logs"
    template_pattern => "simulation-logs-*"
    template_overwrite => true
    
    # Performance tuning
    flush_size => 500
    idle_flush_time => 1
    retry_max_items => 500
    retry_max_interval => 5
    
    # Document settings
    document_type => "_doc"
    doc_as_upsert => true
  }
}
```

## Index Templates

### Basic Template

```ruby
output {
  elasticsearch {
    hosts => ["http://localhost:9200"]
    index => "logs-%{+YYYY.MM.dd}"
    template_name => "logs-template"
    template => '
      {
        "index_patterns": ["logs-*"],
        "settings": {
          "number_of_shards": 1,
          "number_of_replicas": 1,
          "index.refresh_interval": "5s"
        },
        "mappings": {
          "properties": {
            "@timestamp": {
              "type": "date",
              "format": "strict_date_optional_time||epoch_millis"
            },
            "level": {
              "type": "keyword"
            },
            "message": {
              "type": "text",
              "analyzer": "standard"
            },
            "source_ip": {
              "type": "ip"
            },
            "geoip": {
              "properties": {
                "location": {
                  "type": "geo_point"
                },
                "country_name": {
                  "type": "keyword"
                },
                "city_name": {
                  "type": "keyword"
                }
              }
            }
          }
        }
      }
    '
  }
}
```

### Advanced Template with Multiple Types

```ruby
output {
  elasticsearch {
    hosts => ["http://localhost:9200"]
    index => "data-%{type}-%{+YYYY.MM.dd}"
    template_name => "multi-type-data"
    template => '
      {
        "index_patterns": ["data-*"],
        "settings": {
          "number_of_shards": 3,
          "number_of_replicas": 2,
          "index.refresh_interval": "5s",
          "index.max_result_window": 604800000
        },
        "mappings": {
          "dynamic_templates": [
            {
              "path_match": "web_*",
              "mapping": {
                "properties": {
                  "http_method": { "type": "keyword" },
                  "uri_path": { "type": "text" },
                  "response_code": { "type": "integer" },
                  "response_size": { "type": "integer" },
                  "user_agent": { "type": "text" }
                }
              }
            },
            {
              "path_match": "app_*",
              "mapping": {
                "properties": {
                  "log_level": { "type": "keyword" },
                  "application": { "type": "keyword" },
                  "module": { "type": "keyword" },
                  "error_code": { "type": "keyword" }
                }
              }
            },
            {
              "path_match": "security_*",
              "mapping": {
                "properties": {
                  "event_type": { "type": "keyword" },
                  "severity": { "type": "keyword" },
                  "source_ip": { "type": "ip" },
                  "target_ip": { "type": "ip" },
                  "rule_id": { "type": "keyword" }
                }
              }
            }
          ]
        }
      }
    '
  }
}
```

## Data Routing and Indexing

### Time-based Indexing

```ruby
output {
  elasticsearch {
    hosts => ["http://localhost:9200"]
    index => "logs-%{type}-%{+YYYY.MM.dd}"
    
    # Daily indices for high volume
    if [type] == "web_access" {
      index => "web-access-%{+YYYY.MM.dd}"
    } else if [type] == "application" {
      index => "app-logs-%{+YYYY.MM.dd}"
    } else if [type] == "security" {
      index => "security-events-%{+YYYY.MM.dd}"
    }
  }
}
```

### Conditional Indexing

```ruby
output {
  elasticsearch {
    hosts => ["http://localhost:9200"]
    index => "logs-%{+YYYY.MM.dd}"
    
    # Route to different indices based on data
    if [level] == "ERROR" {
      index => "error-logs-%{+YYYY.MM.dd}"
    } else if [level] == "WARN" {
      index => "warning-logs-%{+YYYY.MM.dd}"
    } else {
      index => "info-logs-%{+YYYY.MM.dd}"
    }
  }
}
```

### Document Routing

```ruby
output {
  elasticsearch {
    hosts => ["http://localhost:9200"]
    index => "logs-%{+YYYY.MM.dd}"
    
    # Route documents to specific shards
    routing => "%{customer_id}"
    
    # Set document ID
    document_id => "%{unique_id}"
  }
}
```

## Performance Optimization

### Bulk Operations

```ruby
output {
  elasticsearch {
    hosts => ["http://localhost:9200"]
    index => "bulk-logs-%{+YYYY.MM.dd}"
    
    # Bulk settings
    flush_size => 1000
    idle_flush_time => 10
    retry_max_items => 1000
    retry_max_interval => 10
    
    # Pool settings
    pool_max => 50
    pool_max_per_route => 25
  }
}
```

### Connection Pooling

```ruby
output {
  elasticsearch {
    hosts => ["http://es1:9200", "http://es2:9200", "http://es3:9200"]
    
    # Load balancing
    sniffing => true
    sniffing_delay => 5
    resurrect_delay => 5
    
    # Connection pool
    pool_max => 100
    pool_max_per_route => 10
    timeout => 60
  }
}
```

## Security Configuration

### SSL/TLS Configuration

```ruby
output {
  elasticsearch {
    hosts => ["https://secure-elasticsearch:9200"]
    
    # SSL settings
    ssl => true
    ssl_certificate_verification => true
    cacert => "/etc/ssl/ca-bundle.crt"
    client_key => "/etc/ssl/client.key"
    client_cert => "/etc/ssl/client.crt"
    
    # Protocol
    protocol => "https"
    http_compression => true
  }
}
```

### Authentication

```ruby
output {
  elasticsearch {
    hosts => ["https://secure-elasticsearch:9200"]
    
    # Basic authentication
    user => "logstash_user"
    password => "${ELASTIC_PASSWORD}"
    
    # API key authentication
    api_key => {
      id => "${ELASTIC_API_KEY_ID}"
      api_key => "${ELASTIC_API_KEY}"
    }
    
    # Cloud authentication
    cloud_id => "my-cloud:abc123"
    cloud_auth => "${ELASTIC_CLOUD_AUTH}"
  }
}
```

## High Availability Setup

### Multi-Cluster Configuration

```ruby
output {
  elasticsearch {
    hosts => [
      "https://es-primary:9200",
      "https://es-secondary:9200",
      "https://es-tertiary:9200"
    ]
    
    # Failover settings
    sniffing => true
    sniffing_delay => 3
    resurrect_delay => 3
    
    # Health checks
    healthcheck_path => "/_cluster/health"
    healthcheck_timeout => 10
  }
}
```

### Index Lifecycle Management

```ruby
output {
  elasticsearch {
    hosts => ["http://localhost:9200"]
    index => "logs-%{+YYYY.MM.dd}"
    
    # ILM settings
    ilm_enabled => true
    ilm_rollover_alias => "logs-write"
    ilm_pattern => "{now/d}-000001"
    ilm_policy => "logs-policy"
  }
}
```

## Monitoring and Health Checks

### Cluster Health Monitoring

```ruby
output {
  elasticsearch {
    hosts => ["http://localhost:9200"]
    index => "logs-%{+YYYY.MM.dd}"
    
    # Health check settings
    healthcheck_path => "/_cluster/health"
    healthcheck_timeout => 5
    healthcheck_interval => 30
    
    # Validate on startup
    validate_after_inactivity => 1000
  }
}
```

### Performance Monitoring

```ruby
output {
  elasticsearch {
    hosts => ["http://localhost:9200"]
    index => "logs-%{+YYYY.MM.dd}"
    
    # Performance metrics
    metrics_path => "/var/log/logstash/metrics"
    metrics_enabled => true
    
    # Bulk request tracking
    bulk_request_metrics => true
  }
}
```

## Data Transformation for Elasticsearch

### Field Mapping Preparation

```ruby
filter {
  # Prepare fields for Elasticsearch mapping
  mutate {
    # Convert to appropriate types
    convert => { 
      "response_time" => "float"
      "response_size" => "integer"
      "error_count" => "integer"
    }
    
    # Add Elasticsearch-specific fields
    add_field => { 
      "@version" => "1"
      "data_source" => "logstash_simulation"
      "processed_timestamp" => "%{@timestamp}"
    }
    
    # Handle null values
    replace => { 
      "empty_field" => "N/A"
      "null_value" => ""
    }
  }
}
```

### GeoIP Enrichment for Mapping

```ruby
filter {
  if [client_ip] {
    geoip {
      source => "client_ip"
      target => "geoip"
      database => "/path/to/GeoLite2-City.mmdb"
      add_tag => ["geoip_enriched"]
    }
    
    # Prepare geo fields for Elasticsearch geo_point
    mutate {
      add_field => {
        "location" => "%{[geoip][latitude]},%{[geoip][longitude]}"
      }
    }
  }
}
```

## Troubleshooting Elasticsearch Integration

### Connection Issues

```ruby
# Test connectivity
output {
  elasticsearch {
    hosts => ["http://localhost:9200"]
    index => "test-logs"
    
    # Debug settings
    timeout => 30
    retry_on_conflict => true
    
    # Enable logging
    http_compression => false
  }
}
```

### Index Template Issues

```ruby
output {
  elasticsearch {
    hosts => ["http://localhost:9200"]
    index => "logs-%{+YYYY.MM.dd}"
    
    # Template management
    template_name => "logs-template"
    template_overwrite => true
    manage_template => false  # Set to true to manage templates
  }
}
```

### Performance Issues

```ruby
output {
  elasticsearch {
    hosts => ["http://localhost:9200"]
    index => "logs-%{+YYYY.MM.dd}"
    
    # Performance tuning
    flush_size => 200
    idle_flush_time => 5
    retry_max_items => 200
    
    # Connection pooling
    pool_max => 20
    pool_max_per_route => 5
  }
}
```

## Best Practices

### 1. Index Strategy

- Use time-based indices for time-series data
- Implement index lifecycle management (ILM)
- Use appropriate shard counts based on data volume

### 2. Performance Optimization

- Optimize bulk sizes for your Elasticsearch cluster
- Use connection pooling for high-throughput scenarios
- Monitor and adjust flush intervals

### 3. Data Modeling

- Design mappings that match your query patterns
- Use appropriate field types (keyword vs text)
- Implement nested objects for complex data

### 4. Security

- Always use SSL/TLS in production
- Implement proper authentication
- Use API keys instead of passwords when possible

### 5. Monitoring

- Monitor cluster health and performance
- Track indexing latency and errors
- Set up alerts for integration issues

## Integration Examples

### Web Access Logs with GeoIP

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
  
  # Add GeoIP information
  if [clientip] {
    geoip {
      source => "clientip"
      target => "geoip"
    }
  }
  
  # Prepare for Elasticsearch
  mutate {
    add_field => { 
      "log_type" => "web_access"
      "processed_at" => "%{@timestamp}"
    }
  }
}

output {
  elasticsearch {
    hosts => ["http://localhost:9200"]
    index => "web-access-%{+YYYY.MM.dd}"
    template_name => "web-access-template"
    template => '
      {
        "index_patterns": ["web-access-*"],
        "mappings": {
          "properties": {
            "clientip": { "type": "ip" },
            "geoip": {
              "properties": {
                "location": { "type": "geo_point" },
                "country_name": { "type": "keyword" },
                "city_name": { "type": "keyword" }
              }
            },
            "response": { "type": "integer" },
            "bytes": { "type": "integer" }
          }
        }
      }
    '
  }
}
```

### Multi-Type Data Pipeline

```ruby
input {
  generator {
    lines => [
      "2023-10-10T10:00:00Z INFO web 192.168.1.100 GET /index.html 200",
      "2023-10-10T10:00:01Z ERROR app 192.168.1.101 Database connection failed",
      "2023-10-10T10:00:02Z WARN security 192.168.1.102 Failed login attempt",
      "2023-10-10T10:00:03Z INFO web 192.168.1.103 POST /api/data 201"
    ]
    count => 1000
    interval => 0.1
  }
}

filter {
  # Parse structured data
  grok {
    match => { 
      "message" => "%{TIMESTAMP_ISO8601:timestamp} %{WORD:type} %{IP:client_ip} %{GREEDYDATA:details}"
    }
  }
  
  # Route to different processing based on type
  if [type] == "web" {
    mutate { add_field => { "category" => "web_access" } }
  } else if [type] == "app" {
    mutate { add_field => { "category" => "application" } }
  } else if [type] == "security" {
    mutate { add_field => { "category" => "security_event" } }
  }
}

output {
  elasticsearch {
    hosts => ["http://localhost:9200"]
    index => "%{category}-%{+YYYY.MM.dd}"
    
    # Type-specific templates
    if [category] == "web_access" {
      template_name => "web-access-template"
    } else if [category] == "application" {
      template_name => "application-template"
    } else if [category] == "security_event" {
      template_name => "security-template"
    }
  }
}
```

This Elasticsearch integration guide provides comprehensive coverage of Logstash-Elasticsearch integration patterns for data simulation. For specific configuration examples, see the examples directory.
