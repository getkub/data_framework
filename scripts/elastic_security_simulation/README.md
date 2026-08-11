# Elastic Security ESQL Simulation

Reusable scripts that simulate attacker behaviour in Elastic Security by:

1. Ingesting a reference **NDJSON event stream** into an Elasticsearch **data stream**
   (auto-built index template with ECS-friendly mappings).
2. Optionally creating an **enabled ESQL detection rule** that matches the simulated
   behaviour, producing real alerts in **Alerts → Security** (`.alerts-security.alerts-default`).

These were built from reference **id 101** of
`data/sequence/security/01_linux_reference.csv`
(*High Number of Egress Network Connections from Unusual Executable*), but work for any
`*.ndjson` file in `data/sequence/security/{linux,windows,network}`.

> **Security note:** no credentials are stored anywhere in this directory. The password is
> always supplied at runtime via the `ELASTIC_PASSWORD` env var, or resolved on-the-fly from
> the ECK k8s secret (same mechanism as
> `k8s_kubernetes/isolated/elastic/scripts/port-forward.sh`).

---

## Contents

| File                          | Purpose                                                        |
| ----------------------------- | -------------------------------------------------------------- |
| `simulate_elastic_security.sh`| Bash wrapper - resolves password, then runs the Python script. |
| `simulate_esql.py`            | Ingests NDJSON, manages index template, creates ESQL rule, verifies alerts. |
| `esql_c2_query.esql`          | Example ESQL query for reference id 101 (C2 egress).           |
| `README.md`                   | This documentation.                                            |

---

## Prerequisites

- Elasticsearch + Kibana reachable (defaults: `https://localhost:9200` / `https://localhost:5601`).
  Start the port-forwards first:
  ```bash
  cd ../k8s_kubernetes/isolated/elastic
  ./scripts/port-forward.sh          # keep running in a terminal
  ```
- `python3` (stdlib only - no pip packages required).
- `kubectl` configured for the cluster that holds the `quickstart-es-elastic-user` secret
  (only needed if you don't set `ELASTIC_PASSWORD` yourself).

---

## Quickstart (re-simulate reference id 101)

```bash
cd scripts/elastic_security_simulation

# Option A: password resolved automatically from the k8s secret
./simulate_elastic_security.sh

# Option B: password explicitly (also fine)
export ELASTIC_PASSWORD='your-elastic-password'
./simulate_elastic_security.sh
```

What it does:

1. Creates index template `logs-linux.security-default` (data stream) if missing.
2. Re-timestamps every event to *now* (so a recent-window rule fires) and bulk-ingests
   16 docs into `logs-linux.security-default`.
3. Creates/updates ESQL rule `c2-frequent-egress-netcon-101` (enabled, high severity),
   executes the query and reports any stored alerts.

Expected result:

```
[template] OK   logs-linux.security-default -> data stream 'logs-linux.security-default'
[ingest]   OK   16 docs -> logs-linux.security-default
[rule]     CREATED  id=...  rule_id=c2-frequent-egress-netcon-101  enabled=True
...
[verify]  Alerts stored for rule 'c2-frequent-egress-netcon-101': 1+
```

---

## Simulating any other reference detection

Each row in `data/sequence/security/01_linux_reference.csv` maps a filename to a rule name
and target data stream. Ingest any of the `ndjson` files with your own ESQL query:

```bash
cd scripts/elastic_security_simulation

# Ingest only (no rule) - e.g. base64 decoding activity, ref id 102
./simulate_elastic_security.sh \
    --ndjson ../../data/sequence/security/linux/defense_evasion_base64_decoding_activity.ndjson \
    --data-stream logs-linux.security-default \
    --skip-rule

# Ingest + rule (Windows example, ref id 104 - subnet scanning)
./simulate_elastic_security.sh \
    --ndjson ../../data/sequence/security/windows/discovery_subnet_scanning_activity_from_compromised_host.ndjson \
    --data-stream logs-windows.security-default \
    --rule-id subnet-scanning-104 \
    --rule-name "[Sim] Potential Subnet Scanning Activity from Compromised Host" \
    --query-file my_query.esql \
    --severity medium --risk-score 47 --interval 5m
```

Useful flags (`simulate_esql.py --help` for all):

| Flag             | Default                      | Purpose                                |
| ---------------- | ---------------------------- | -------------------------------------- |
| `--ndjson`       | (required)                   | Input reference event file             |
| `--data-stream`  | `logs-linux.security-default`| ES data stream to write to             |
| `--query-file`   | -                            | File containing the ESQL query         |
| `--rule-id`      | -                            | Unique rule id (enables rule creation) |
| `--rule-name`    | -                            | Rule display name                      |
| `--severity`     | `high`                       | low / medium / high / critical         |
| `--risk-score`   | `50`                         | 0-100                                   |
| `--interval`     | `5m`                         | Rule run interval                      |
| `--from`         | `now-6m`                     | Rule look-back window                  |
| `--skip-rule`    | off                          | Only ingest, do not touch rules        |
| `--es-url` / `--kibana-url` / `--user` | `https://localhost:9200` / `https://localhost:5601` / `elastic` | Override endpoints |

---

## Writing the ESQL rule query

The query is the whole detection. It must run over the target data stream and return
rows only when a detection condition holds. Pattern used for id 101:

```esql
FROM logs-linux.security-default
| WHERE event.action == "connection_attempted"
| STATS egress_connections = COUNT(*) BY process.executable, process.name, host.name, source.ip
| WHERE egress_connections >= 10
| SORT egress_connections DESC
```

Test any query ad-hoc before creating the rule:

```bash
curl -sk -u elastic:"$ELASTIC_PASSWORD" https://localhost:9200/_query \
  -H 'Content-Type: application/json' \
  -d '{"query":"FROM logs-linux.security-default | STATS n = COUNT(*) BY process.executable"}'
```

---

## Cleaning up

```bash
# Remove a rule (Kibana API)
curl -sk -u elastic:"$ELASTIC_PASSWORD" -X DELETE \
  "https://localhost:5601/api/detection_engine/rules?rule_id=c2-frequent-egress-netcon-101" \
  -H 'kbn-xsrf: true'

# Delete the data stream (and its index template)
curl -sk -u elastic:"$ELASTIC_PASSWORD" -X DELETE \
  "https://localhost:9200/_data_stream/logs-linux.security-default"
curl -sk -u elastic:"$ELASTIC_PASSWORD" -X DELETE \
  "https://localhost:9200/_index_template/logs-linux.security-default"
```

---

## Wiring alerts into n8n (next step)

The rule currently has no actions, so alerts sit in `.alerts-security.alerts-default`.
To have n8n triage them, two options:

1. **Push (recommended):** add a connector + rule action in
   **Security -> Rules -> [rule] -> Actions**. Use a **Webhook** connector pointing at a
   fresh n8n *Webhook* workflow (`POST`, `http://localhost:5678/webhook/<path>`). Elastic
   POSTs each generated alert to n8n in real time.
2. **Poll:** an n8n workflow scheduled every minute queries
   `https://localhost:9200/.alerts-security.alerts-default/_search` filtering
   `kibana.alert.rule.rule_id: c2-frequent-egress-netcon-101` and `kibana.alert.status: active`.

---

## Troubleshooting

| Symptom                                      | Cause / fix                                        |
| -------------------------------------------- | -------------------------------------------------- |
| `ERROR: ELASTIC_PASSWORD env var required`   | Password not set and kubectl secret not reachable. `export ELASTIC_PASSWORD=...` |
| `connection refused`                         | Port-forward not running: `k8s_kubernetes/isolated/elastic/scripts/port-forward.sh` |
| `[ingest] ERROR some docs failed`            | Data stream/index closed, or mapping conflict - check the printed reason |
| Rule created but no alert                    | Events too old (they are re-timestamped to *now* on ingest) or query window too short - use `--from now-6m` |
| ESQL query error                             | Test the query first with the `curl /_query` snippet above |

---

## References

- Reference index: `data/sequence/security/01_linux_reference.csv`
- Sample data: `data/sequence/security/linux/*.ndjson`, `windows/*.ndjson`
- Ingestion pattern documented in: `docs/elastic/Index_creation.md`