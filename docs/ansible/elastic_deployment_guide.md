# Elasticsearch Data Deployment via Ansible

This directory contains the Ansible playbooks used to generate bulk NDJSON payloads and push them to specific Elasticsearch data streams securely. 

## Prerequisites

Before running the playbooks, you must configure your environment safely so that credentials are valid and remain untracked by Git.

1. **Configure Environment Secrets** 
   You must export your `ELASTIC_API_KEY` into your local environment prior to running the playbooks. The project ignores `.secrets/` by default.

   Generate your local secret configuration file:
   ```bash
   mkdir -p .secrets
   cp .secrets/.env.local.example .secrets/.env.local
   ```
   Open `.secrets/.env.local` and add your real base64 encoded API key.

2. **Configure Network / Host**
   Ensure that the target host points to your Elastic instance. The default configuration connects to `localhost` via HTTPS. You can modify this in `ansible/group_vars/elastic.yml` if your Elasticsearch cluster is hosted remotely (e.g. Elastic Cloud).

---

## Deployment Workflow

The typical data deployment pipeline happens in three distinct steps:

### 1. Build Bulk Payloads
First, take your raw NDJSON event data files and convert them into an Elasticsearch bulk format based on their reference IDs (defined in mapping CSVs like `data/sequence/security/01_linux_reference.csv`).

```bash
source .secrets/.env.local && ansible-playbook ansible/elastic_playbooks/build_by_id.yml -e "reference_ids=[113]"
```
*(You can submit a list of comma-separated reference IDs if you want to bundle multiple rule configurations).*

### 2. Ensure Data Stream Exists
Prior to ingestion, it's best practice to ensure the target data stream endpoint actually exists. This avoids unexpected index mappings.

```bash
source .secrets/.env.local && ansible-playbook ansible/elastic_playbooks/setup_datastream.yml
```
*(This uses the `target_datastream` mapped in the playbooks, which defaults to `logs-endpoint.events.process-default`. To override it, append `-e target_datastream="my-custom-stream" `)*

### 3. Deploy the Data
Finally, push every processed bulk file straight into Elasticsearch using the credentials provisioned in `group_vars`.

```bash
source .secrets/.env.local && ansible-playbook ansible/elastic_playbooks/deploy_bulk.yml
```

---

## Modifying/Adding New Rule References

Whenever you want to add new simulation data, make sure to:
1. Save your simulated NDJSON in the `data/sequence/` folders.
2. Edit the relevant CSV in `data/sequence/.../` (e.g. `01_linux_reference.csv`) allocating a distinct ID and mapping it to the relative json payload and target `data_stream`.
3. Re-run Step 1 through 3 referencing your new ID.
