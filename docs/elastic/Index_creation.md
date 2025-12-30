# Elasticsearch Index Creation and Data Ingestion Guide

This guide covers the process of creating Elasticsearch indices and ingesting data using various methods, including bulk operations and Elastic integrations.

## Prerequisites

- Elasticsearch cluster running and accessible
- Kibana instance (for integration setup)
- API key or authentication credentials
- Data in NDJSON format

## Data Preparation

### Converting NDJSON to Bulk Format

Before ingesting data into Elasticsearch, convert your NDJSON files to Elasticsearch bulk API format:

```bash
jq -c . 10_brute_force.ndjson | awk '{print "{ \"create\": {} }\n" $0}' > bulk.ndjson
```

This command:
- Uses `jq -c` to compact each JSON object
- Adds the Elasticsearch bulk `create` action for each document
- Outputs to `bulk.ndjson` file

## Elastic Integrations Setup

### Initialize Fleet

First, set up Elastic Fleet for managing integrations:

```http
POST kbn:/api/fleet/setup
```

### Discover Available Packages

List available integration packages:

```http
GET kbn:/api/fleet/epm/packages/windows
```

### Install Integration Package

Install a specific version of the Windows integration:

```http
POST kbn:/api/fleet/epm/packages/windows/3.3.0
{
  "force": true
}
```

## Pipeline Discovery

### List Available Ingest Pipelines

Find the correct ingest pipeline for your data:

```http
GET _ingest/pipeline?filter_path=*.description
```

### Check Package Details

Get detailed information about a specific package:

```http
GET kbn:/api/fleet/epm/packages/windows/3.3.0
```

### Verify Data Stream

Check if the target data stream exists:

```http
GET _data_stream/logs-windows.security-default
```

## Data Ingestion

### Bulk Insert with Pipeline

Ingest data using the bulk API with a specific ingest pipeline:

```bash
curl -k -X POST \
  "https://localhost:9200/logs-windows.security-default/_bulk?pipeline=logs-system.security-2.6.3-standard" \
  -H "Authorization: ApiKey ${YOUR_API_KEY}" \
  -H "Content-Type: application/x-ndjson" \
  --data-binary "@bulk.ndjson"
```

**Parameters:**
- Replace `logs-windows.security-default` with your target data stream
- Update the pipeline name (`logs-system.security-2.6.3-standard`) based on your integration
- Set `YOUR_API_KEY` to your actual Elasticsearch API key
- Ensure `bulk.ndjson` contains your prepared bulk data

## Troubleshooting

- Verify your Elasticsearch cluster is running and accessible
- Check API key permissions for bulk operations
- Ensure the ingest pipeline exists and is correctly configured
- Validate your NDJSON data format before conversion
- Monitor Elasticsearch logs for ingestion errors

## Next Steps

- Set up index templates for custom mappings
- Configure index lifecycle management (ILM) policies
- Implement monitoring and alerting for ingestion pipelines
- Consider using Logstash or Beats for continuous data ingestion

```
