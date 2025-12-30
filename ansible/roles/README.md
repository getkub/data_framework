# Elasticsearch Data Ingestion - Operational Guide

## Quick Start

### Set Environment
```bash
cd ansible
export ELASTIC_API_KEY="your_api_key_here"
```

### Build & Deploy Specific Datasets
```bash
# Build bulk files for reference IDs 401, 403, 101
ansible-playbook -i hosts main_playbooks/build_by_id.yml \
  -e "reference_ids=[401,403,101]"

# Deploy the built files to Elasticsearch
ansible-playbook -i hosts main_playbooks/deploy_by_id.yml \
  -e "reference_ids=[401,403,101]"
```

## Reference IDs

Find available reference IDs in the CSV files:
- `data/sequence/security/01_windows_reference.csv`
- `data/sequence/security/01_linux_reference.csv`

Each reference contains:
- **ID**: Unique identifier (e.g., 401, 101)
- **Filename**: Source NDJSON file
- **Data Stream**: Target Elasticsearch data stream
- **Pipeline**: Ingest pipeline to use

## Configuration

### Cluster Settings
Edit `ansible/group_vars/elastic.yml`:
```yaml
elastic_host: "your-elasticsearch-host"
elastic_port: "9200"
elastic_protocol: "https"
```

### API Key
Set via environment variable:
```bash
export ELASTIC_API_KEY="your_api_key_here"
```

## Workflow

1. **Build Phase**: Converts NDJSON → bulk format
   - Cleans build directory
   - Creates `*.bulk.ndjson` files
   - Ready for deployment

2. **Deploy Phase**: Sends bulk files to Elasticsearch
   - Uses correct data stream & pipeline per reference
   - Independent from build phase
   - Can be run separately

## Examples

### Single Dataset
```bash
ansible-playbook -i hosts main_playbooks/build_by_id.yml -e "reference_ids=[401]"
ansible-playbook -i hosts main_playbooks/deploy_by_id.yml -e "reference_ids=[401]"
```

### Multiple Datasets
```bash
ansible-playbook -i hosts main_playbooks/build_by_id.yml -e "reference_ids=[401,403,101]"
ansible-playbook -i hosts main_playbooks/deploy_by_id.yml -e "reference_ids=[401,403,101]"
```

### Windows Security Data
```bash
ansible-playbook -i hosts main_playbooks/build_by_id.yml -e "reference_ids=[401,402,403]"
ansible-playbook -i hosts main_playbooks/deploy_by_id.yml -e "reference_ids=[401,402,403]"
```

### Linux Security Data
```bash
ansible-playbook -i hosts main_playbooks/build_by_id.yml -e "reference_ids=[101,102,103]"
ansible-playbook -i hosts main_playbooks/deploy_by_id.yml -e "reference_ids=[101,102,103]"
```

## Prerequisites

- Ansible installed
- Python 3 available
- Elasticsearch cluster accessible
- Valid API key with bulk permissions
- Data streams and pipelines configured
