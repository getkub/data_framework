# n8n <-> Elastic Security - Alerts API Reference

Companion doc to `README.md`. This is the spec for building the n8n workflow that
pulls the simulated alerts out of Elastic, enriches/triages them, and shows the analyst
the triggering rule and its actual code (the ESQL query).

Everything below was verified against the live stack in this repo
(`k8s_kubernetes/isolated/elastic`, Elastic stack 9.5.0) using the `elastic` user.
Where an API was deprecated/unavailable we document the working replacement.
ASCII only - no special characters.

---

## Access prerequisites

| Service        | Local URL                 | Notes                                       |
| -------------- | ------------------------- | ------------------------------------------- |
| Elasticsearch  | https://localhost:9200    | alerts are read here (`_search`)            |
| Kibana         | https://localhost:5601    | rule details via Kibana API (optional)      |
| n8n            | http://localhost:5678     | the workflow that orchestrates the calls    |

- Keep the port-forward running:
  `k8s_kubernetes/isolated/elastic/scripts/port-forward.sh`
- Auth for all calls below: HTTP Basic `elastic` + the Elastic password.
  In n8n store this as a Credential (never hardcode it in a workflow or here).

---

## The full triage data-flow (3 steps)

```
Step 1: Fetch alerts
   --> for each alert:
         --> read the rule CODE from the alert (kibana.alert.rule.parameters.query)
             and/or call the rule API (Step 2) for the live rule
         --> Step 3: triage (workflow_status = acknowledged | closed)
```

n8n does the "for each" automatically: a search node that returns many alert hits
becomes a list of items, and downstream nodes run once per item.

---

## Step 1: Fetch open alerts (Elasticsearch)

Read the alerts-as-data index directly. This is exactly what the Security app does.

Method `POST` - `https://localhost:9200/.alerts-security.alerts-default/_search`

```json
{
  "size": 50,
  "sort": [ { "@timestamp": "desc" } ],
  "query": {
    "bool": {
      "filter": [
        { "term": { "kibana.alert.rule.rule_id": "c2-frequent-egress-netcon-101" } },
        { "term": { "kibana.alert.status": "active" } }
      ]
    }
  }
}
```

To fetch ALL detection alerts regardless of rule (better for a general triage queue):

```json
{
  "size": 50,
  "sort": [ { "@timestamp": "desc" } ],
  "query": {
    "bool": {
      "filter": [
        { "term": { "kibana.alert.status": "active" } },
        { "range": { "@timestamp": { "gte": "now-15m" } } }
      ]
    }
  }
}
```

**Key fields in each hit (`hits.hits[]._source`)** - n8n reads these:

| Field                                   | Example value                                          |
| --------------------------------------- | ------------------------------------------------------ |
| `_id` (doc id)                          | `469a0a6ab5773544b76c42cdb33924835facf776`             |
| `kibana.alert.rule.rule_id`             | `c2-frequent-egress-netcon-101`                        |
| `kibana.alert.rule.name`                | `[Sim] High Number of Egress Network Connections...`   |
| `kibana.alert.rule.description`         | `Simulation: high number of egress connections...`     |
| `kibana.alert.rule.severity`            | `high`                                                 |
| `kibana.alert.rule.risk_score`          | `73`                                                   |
| `kibana.alert.status`                   | `active`                                               |
| `kibana.alert.workflow_status`          | `open`                                                 |
| `kibana.alert.rule.uuid`                | `79255303-2630-41b4-8173-b3beb369dc1d`                 |
| `@timestamp`                            | `2026-08-11T05:32:23.341Z`                             |
| `process.executable` / `host.name`      | `/tmp/malware` / `linux-host` (original event)         |
| `egress_connections`                    | `16` (custom agg column from the ESQL rule)            |

**The actual rule CODE is in the alert.** The complete rule configuration (including the
full ESQL query language) is embedded under:

```
kibana.alert.rule.parameters.query
```

For our rule this resolves to the real detection query:

```
FROM logs-linux.security-default
| WHERE event.action == "connection_attempted"
| STATS egress_connections = COUNT(*) BY process.executable, process.name, host.name, source.ip
| WHERE egress_connections >= 10
| SORT egress_connections DESC
```

So an analyst can see the exact rule code with no extra API call. The whole
`kibana.alert.rule.parameters` object mirrors the rule definition (`query`, `type`,
`language`, `description`, `from`, `to`, `false_positives`, `threat`, ...), and much of
that is also surfaced as first-class `kibana.alert.rule.*` fields
(`severity`, `risk_score`, `interval`, `from`, `to`, `indices`, `tags`, ...).

> Note: the field `kibana.alert.rule.query` is NULL for ESQL rules - the query is NOT
> stored there. It lives in `kibana.alert.rule.parameters.query` instead.

---

## Step 2: Get the triggering rule details (Kibana API) - optional

Because the full rule (including its code) is already embedded in the alert at
`kibana.alert.rule.parameters.*`, this API call is **optional**. Use it when you want the
**live/canonical** definition from the rules store (for example, if the rule was updated
after the alert was created, or you want the rule's current `enabled`/`interval`/`revision`).

Method `GET` - `https://localhost:5601/api/detection_engine/rules?rule_id={rule_id}`
(standard HTTP Basic auth + header `kbn-xsrf: true`)

Response (verified) - the fields n8n uses for the analyst view:

| Field          | Example value                                                        |
| -------------- | -------------------------------------------------------------------- |
| `name`         | `[Sim] High Number of Egress Network Connections from Unusual Executable` |
| `description`  | `Simulation: high number of egress connections... (ref id 101)`       |
| `type`         | `esql`                                                                |
| `enabled`      | `true`                                                                |
| `interval`     | `5m`                                                                  |
| `severity`     | `high`                                                                |
| `risk_score`   | `73`                                                                  |
| `query`        | `FROM logs-linux.security-default | WHERE event.action == "connection_attempted" | STATS ...` |

Other useful rule endpoints:

- List / find all rules: `GET /api/detection_engine/rules/_find?per_page=100`
- Fetch by internal UUID (`kibana.alert.rule.uuid`): `GET /api/detection_engine/rules?id={uuid}`
  (the `?rule_id=` form matches the custom rule_id you set when creating the rule)

---

## Step 3: Triage - update the alert status (Elasticsearch)

To mark an alert acknowledged/closed (so it leaves the active queue), update the alert doc
field `kibana.alert.workflow_status`. The legacy Security endpoint
(`/api/detection_engine/signals/status`) is removed in 9.x (returns 400); use
`_update_by_query` directly - verified working.

Method `POST` - `https://localhost:9200/.alerts-security.alerts-default/_update_by_query?refresh=true`

```json
{
  "query": { "term": { "_id": { "value": "<the alert _id from Step 1>" } } },
  "script": {
    "source": "ctx._source['kibana.alert.workflow_status']='acknowledged'",
    "lang": "painless"
  }
}
```

Valid values for `kibana.alert.workflow_status`: `open`, `acknowledged`, `closed`.
Optional: also set `kibana.alert.workflow_reason` to store a triage note/comment.

Example to bulk-close everything from one rule after triaging:

```json
{
  "query": {
    "term": { "kibana.alert.rule.rule_id": "c2-frequent-egress-netcon-101" }
  },
  "script": {
    "source": "ctx._source['kibana.alert.workflow_status']='closed'",
    "lang": "painless"
  }
}
```

---

## n8n workflow - recommended node layout

```
[1] Trigger (Schedule: every 1-5 min)  OR  Elastic Security Webhook connector (push)
        |
        v
[2] Elasticsearch node - operation "Search"
        index  : .alerts-security.alerts-default
        body   : the Step 1 query above
        |   (search returns a LIST of alerts; n8n loops each downstream automatically)
        v
[3] HTTP Request node (OPTIONAL) - GET rule details for current item
        URL  : https://localhost:5601/api/detection_engine/rules?rule_id={{ $json["_source"]["kibana.alert.rule.rule_id"] }}
        Auth : Header Auth (Basic) -> elastic credential
        |   (skip this if you read the rule code from the alert itself)
        v
[4] Your analysis / enrichment / notify nodes
        e.g. build an analyst message combining the alert + the rule query
             (read the query from kibana.alert.rule.parameters.query, or from [3])
        (Slack / email / a notes app / risk scoring)
        v
[5] Elasticsearch node - Triage: mark acknowledged/closed (Step 3 update_by_query)
```

### Node-by-node notes

- **[2] Search** - use an Elasticsearch node, or an HTTP Request node with the exact
  JSON from Step 1. Base URL `https://localhost:9200`, Basic auth credential.
- **[3] Rule pivot (optional)** - the rule code is already at
  `kibana.alert.rule.parameters.query` on each alert item, so this call is only needed
  for the live rule state. If used, store the returned `query`/`severity`/`description`
  onto the item.
- **[5] Triage** - uses the current item's alert `_id`. After triaging, `workflow_status`
  changes to `acknowledged`/`closed` (status stays `active`). If you only want the open
  queue each run, add a filter to Step 1:

  ```json
  { "term": { "kibana.alert.workflow_status": "open" } }
  ```

### Credentials in n8n (do NOT store in files)

Create n8n Credentials once, referenced by the nodes:
- Elasticsearch credential -> host `localhost`, port `9200`, HTTPS, user `elastic`,
  password = the Elastic password.
- HTTP Header Auth (Basic) credential -> user `elastic`, same password (used by the
  Kibana rule-pivot).

These values are the same runtime credentials the rest of this repo resolves
automatically - never commit them.

---

## Gotchas / notes for the workflow developer

1. **The rule CODE is in the alert** - read `kibana.alert.rule.parameters.query` to get
   the exact ESQL query that fired. Do NOT look at `kibana.alert.rule.query` (it is null
   for ESQL rules).
2. **Rule API is optional** - the alert already carries the full rule config in
   `kibana.alert.rule.parameters.*`; call `/api/detection_engine/rules` only for the
   live/canonical rule.
3. **Triage API moved** - use ES `_update_by_query` (Step 3); the old
   `/api/detection_engine/signals/status` returns 400 on 9.x.
4. **Alerts carry context** - each hit has both `kibana.alert.*` metadata and the projected
   columns / original event, so read analyst context straight from the hit before any
   enrichment.
5. **Empty loop** - if a search returns no hits, n8n will not run [3]-[5]; add a branch on
   the item count if you want a "nothing to triage" notification.
6. **Rate / auth** - all calls are Basic auth to localhost via port-forward; keep them
   within n8n's default throttling.

---

## Dev checklist (to complete the n8n workflow)

- [ ] Store Elastic + Kibana credentials in n8n (never in files).
- [ ] Build trigger + Step 1 search (open alerts for `c2-frequent-egress-netcon-101`, or all).
- [ ] Read rule code per alert from `kibana.alert.rule.parameters.query`; optionally add
      the Step 2 rule API call for the live rule.
- [ ] Analyst output (Slack/email) with alert + rule context.
- [ ] Step 3 triage update_by_query -> `acknowledged`/`closed`.
- [ ] Test end-to-end by re-running the simulation (`./simulate_elastic_security.sh`).

