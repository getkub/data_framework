#!/usr/bin/env python3
"""
Simulate Elastic Security data + ESQL detection rule.

Ingests a reference NDJSON event stream (e.g. data/sequence/security/linux/*.ndjson)
into an Elasticsearch data stream and optionally creates/enables an ESQL detection
rule that matches the simulated behaviour, so alerts are generated in the Security
app (.alerts-security.alerts-default).

Credentials are NEVER stored in this file. The password is read from the
ELASTIC_PASSWORD environment variable (set by the caller / wrapper script).

Usage examples
--------------
    # 1) Just ingest data (no rule)
    ELASTIC_PASSWORD=xxx python3 simulate_esql.py \\
        --ndjson ../../data/sequence/security/linux/command_and_control_frequent_egress_netcon_from_sus_executable.ndjson \\
        --data-stream logs-linux.security-default

    # 2) Ingest data AND create an ESQL rule (as done for reference id 101)
    ELASTIC_PASSWORD=xxx python3 simulate_esql.py \\
        --ndjson ../../data/sequence/security/linux/command_and_control_frequent_egress_netcon_from_sus_executable.ndjson \\
        --data-stream logs-linux.security-default \\
        --rule-id c2-frequent-egress-netcon-101 \\
        --rule-name "[Sim] High Number of Egress Network Connections from Unusual Executable" \\
        --description "Simulation: C2 egress network activity (reference id 101)." \\
        --query-file esql_c2_query.esql \\
        --severity high --risk-score 73 --interval 5m

See README.md for full documentation.
"""

import argparse
import base64
import json
import os
import ssl
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# HTTP helpers (Elasticsearch + Kibana, self-signed TLS)
# ---------------------------------------------------------------------------
_CTX = ssl.create_default_context()
_CTX.check_hostname = False
_CTX.verify_mode = ssl.CERT_NONE


def _auth_header(user: str, password: str) -> dict:
    token = base64.b64encode(f"{user}:{password}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


def _request(url: str, user: str, password: str, method: str = "GET",
             payload=None, timeout: int = 30, kibana: bool = False):
    headers = _auth_header(user, password)
    headers["Content-Type"] = "application/json"
    if kibana:
        headers["kbn-xsrf"] = "true"
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, method=method, headers=headers, data=data)
    try:
        with urllib.request.urlopen(req, context=_CTX, timeout=timeout) as resp:
            raw = resp.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        return {"_http_error": e.code, "_body": body}

# ---------------------------------------------------------------------------
# ECS-ish mappings applied to the (auto-created) index template so common
# fields get sensible types (keyword / ip / date) instead of dynamic pickling.
# ---------------------------------------------------------------------------
COMMON_MAPPINGS = {
    "@timestamp": {"type": "date"},
    "event": {"properties": {
        "action": {"type": "keyword"}, "type": {"type": "keyword"},
        "category": {"type": "keyword"}, "kind": {"type": "keyword"},
    }},
    "host": {"properties": {
        "name": {"type": "keyword"},
        "os": {"properties": {"type": {"type": "keyword"}}},
        "ip": {"type": "ip"},
    }},
    "process": {"properties": {
        "name": {"type": "keyword"},
        "executable": {"type": "keyword"},
        "args": {"type": "keyword"},
        "command_line": {"type": "keyword", "index": False},
        "pid": {"type": "long"},
        "parent": {"properties": {"name": {"type": "keyword"},
                                  "executable": {"type": "keyword"}}},
    }},
    "destination": {"properties": {
        "ip": {"type": "ip"}, "port": {"type": "long"},
        "domain": {"type": "keyword"},
    }},
    "source": {"properties": {"ip": {"type": "ip"}, "port": {"type": "long"}}},
    "user": {"properties": {
        "id": {"type": "keyword"}, "name": {"type": "keyword"},
        "target": {"properties": {"id": {"type": "keyword"},
                                  "name": {"type": "keyword"}}},
    }},
    "agent": {"properties": {"id": {"type": "keyword"}, "type": {"type": "keyword"}}},
    "file": {"properties": {"path": {"type": "keyword"}}},
}


def ensure_index_template(es_url: str, user: str, password: str, data_stream: str) -> None:
    """Create (idempotently) an index template that enables a data stream."""
    template_name = data_stream.replace("/", "_")
    body = {
        "index_patterns": [data_stream],
        "data_stream": {},
        "priority": 500,
        "template": {
            "settings": {"index": {"number_of_shards": 1, "number_of_replicas": 1}},
            "mappings": {"properties": COMMON_MAPPINGS},
        },
    }
    result = _request(f"{es_url}/_index_template/{template_name}", user, password,
                      method="PUT", payload=body)
    if result.get("acknowledged"):
        print(f"[template] OK   {template_name} -> data stream '{data_stream}'")
    else:
        print(f"[template] WARN {result.get('_body', result)}")


def ingest_ndjson(es_url: str, user: str, password: str, ndjson: str,
                  data_stream: str) -> int:
    """Re-timestamp every line to 'now' and bulk-ingest into the data stream."""
    base = datetime.now(timezone.utc)
    bulk_lines = []
    n = 0
    with open(ndjson) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            doc = json.loads(line)
            ts = (base + timedelta(seconds=n)).strftime("%Y-%m-%dT%H:%M:%S.000Z")
            doc["@timestamp"] = ts
            bulk_lines.append('{ "create": {} }')
            bulk_lines.append(json.dumps(doc, separators=(",", ":")))
            n += 1

    if not bulk_lines:
        print("[ingest]  ERROR no documents parsed from", ndjson)
        return 0

    body = ("\n".join(bulk_lines) + "\n").encode()
    req = urllib.request.Request(f"{es_url}/{data_stream}/_bulk", data=body, method="POST")
    req.add_header("Content-Type", "application/x-ndjson")
    for k, v in _auth_header(user, password).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, context=_CTX, timeout=60) as resp:
            result = json.load(resp)
    except urllib.error.HTTPError as e:
        print("[ingest]  ERROR HTTP", e.code, e.read().decode(errors="replace"))
        return 0

    if result.get("errors"):
        print("[ingest]  ERROR some docs failed:")
        for item in result.get("items", []):
            op = item.get("create", {})
            if op.get("status", 200) >= 300:
                print("          -", op.get("status"), op.get("error", {}).get("reason"))
        return 0
    print(f"[ingest]  OK   {n} docs -> {data_stream}")
    return n


def _esql(es_url: str, user: str, password: str, query: str):
    return _request(f"{es_url}/_query", user, password, method="POST",
                    payload={"query": query})


def create_or_update_rule(kibana_url: str, user: str, password: str, rule: dict) -> str:
    """Create a rule if rule_id does not exist, otherwise update it. Returns rule id."""
    rule_id = rule["rule_id"]
    existing = _request(f"{kibana_url}/api/detection_engine/rules?rule_id={rule_id}",
                        user, password, method="GET", kibana=True)
    if existing.get("id"):
        result = _request(f"{kibana_url}/api/detection_engine/rules",
                          user, password, method="PUT", payload=rule, kibana=True)
        status = "updated"
    else:
        result = _request(f"{kibana_url}/api/detection_engine/rules",
                          user, password, method="POST", payload=rule, kibana=True)
        status = "created"
    rid = result.get("id") or result.get("_body")
    print(f"[rule]    {status.upper()}  id={rid}  rule_id={rule_id}  enabled={result.get('enabled')}")
    return result.get("id") or ""


def trigger_run(kibana_url: str, user: str, password: str, rule_id: str) -> None:
    """Fire the rule immediately so it evaluates the just-ingested data."""
    result = _request(f"{kibana_url}/internal/alerting/rule/{rule_id}/_run_soon",
                      user, password, method="POST", kibana=True)
    if result.get("_http_error"):
        print(f"[run]     INFO manual run skipped ({result['_http_error']}); "
              "rule will fire on its scheduled interval.")
    else:
        print("[run]     OK   triggered manual evaluation")


def verify(es_url: str, user: str, password: str, rule: dict) -> None:
    """Run the rule's ESQL query and report matches + stored alerts."""
    print("\n[verify]  Executing rule ESQL query...")
    q = rule.get("query", "")
    res = _esql(es_url, user, password, q)
    if res.get("_http_error"):
        print("[verify]  ERROR running query:", res.get("_body"))
        return
    if res.get("values"):
        print("[verify]  Queried rows (sample):")
        for row in res["values"][:20]:
            print("           ", row)
    else:
        print("[verify]  No rows returned by query.")

    rule_id = rule.get("rule_id")
    search = {
        "size": 10,
        "query": {"term": {"kibana.alert.rule.rule_id": {"value": rule_id}}},
    }
    alerts = _request(f"{es_url}/.alerts-security.alerts-default/_search", user,
                      password, method="POST", payload=search)
    total = (alerts.get("hits") or {}).get("total", {}).get("value", 0)
    print(f"[verify]  Alerts stored for rule '{rule_id}': {total}")
    for hit in (alerts.get("hits") or {}).get("hits", [])[:5]:
        s = hit.get("_source", {})
        print("          -", s.get("kibana.alert.status"),
              "|", s.get("kibana.alert.severity"),
              "|", s.get("kibana.alert.workflow_status"),
              "| rule:", s.get("kibana.alert.rule.name"))

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Simulate Elastic Security data + ESQL rule")
    ap.add_argument("--ndjson", required=True, help="Path to reference NDJSON event file")
    ap.add_argument("--data-stream", default="logs-linux.security-default",
                    help="Elasticsearch data stream to write to (default logs-linux.security-default)")
    ap.add_argument("--es-url", default=os.environ.get("ES_URL", "https://localhost:9200"))
    ap.add_argument("--kibana-url", default=os.environ.get("KIBANA_URL", "https://localhost:5601"))
    ap.add_argument("--user", default=os.environ.get("ES_USER", "elastic"))
    # Rule options (only used when --query-file / rule-id provided)
    ap.add_argument("--rule-id", help="ESQL rule rule_id (enables rule creation)")
    ap.add_argument("--rule-name", help="Rule display name")
    ap.add_argument("--description", default="Simulated Elastic Security detection.")
    ap.add_argument("--query-file", help="Path to file containing the ESQL query")
    ap.add_argument("--severity", default="high", choices=["low", "medium", "high", "critical"])
    ap.add_argument("--risk-score", type=int, default=50)
    ap.add_argument("--interval", default="5m", help="Rule run interval (default 5m)")
    ap.add_argument("--from", dest="from_window", default="now-6m", help="Look-back window")
    ap.add_argument("--skip-rule", action="store_true", help="Only ingest data, no rule")
    args = ap.parse_args()

    password = os.environ.get("ELASTIC_PASSWORD") or os.environ.get("ES_PASSWORD")
    if not password:
        print("ERROR: ELASTIC_PASSWORD env var is required "
              "(never store credentials in files).", file=sys.stderr)
        sys.exit(2)

    if not os.path.exists(args.ndjson):
        print("ERROR: ndjson file not found:", args.ndjson, file=sys.stderr)
        sys.exit(2)

    # 1) index template + ingestion
    ensure_index_template(args.es_url, args.user, password, args.data_stream)
    n = ingest_ndjson(args.es_url, args.user, password, args.ndjson, args.data_stream)
    if not n:
        print("ERROR: ingestion failed, aborting.", file=sys.stderr)
        sys.exit(1)

    # 2) optional: ESQL rule
    if not args.skip_rule:
        if not (args.rule_id and args.query_file):
            print("[rule]    INFO skipping rule (use --rule-id and --query-file to create one)")
        else:
            query = Path(args.query_file).read_text().strip()
            rule = {
                "rule_id": args.rule_id,
                "name": args.rule_name or f"[Sim] {args.rule_id}",
                "description": args.description,
                "risk_score": args.risk_score,
                "severity": args.severity,
                "type": "esql",
                "language": "esql",
                "query": query,
                "interval": args.interval,
                "from": args.from_window,
                "to": "now",
                "max_signals": 100,
                "enabled": True,
                "tags": ["simulation", "esql", args.data_stream],
                "false_positives": ["This is simulation data for testing the detection pipeline."],
                "references": [],
                "risk_score_mapping": [],
                "severity_mapping": [],
                "threat": [],
                "actions": [],
            }
            rid = create_or_update_rule(args.kibana_url, args.user, password, rule)
            if rid:
                trigger_run(args.kibana_url, args.user, password, rid)
                time.sleep(5)
                verify(args.es_url, args.user, password, rule)

    print("\nDone. Ingested", n, "docs into", args.data_stream)


if __name__ == "__main__":
    main()
