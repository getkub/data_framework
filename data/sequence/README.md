````markdown
# Sequences – Analytic Stories Built from Event Samples

## Overview

The `sequences/` directory contains **analytic stories** that model attacks, misuse cases, or complex security behaviors as a **sequence of related events**.

⚠️ **Important:**  
Sequences do **not** define raw events themselves.

Instead, a sequence is a **mix-and-match composition of existing event samples** from the `samples/` directory, arranged in a meaningful order to simulate a real-world attack or investigation flow.

> **Samples = atomic events**  
> **Sequences = ordered narratives built from those events**

This strict dependency ensures:
- Reuse of event samples
- Consistency across simulations
- Separation of concerns between data and behavior

---

## Relationship to `samples/`

- The `samples/` directory contains **individual, vendor-specific event datasets**
- The `sequences/` directory references those datasets
- A sequence **cannot function without samples**
- The same sample may be reused across many sequences

Sequences **never redefine event payloads** — they only reference them.

---

## Directory Structure

To allow future growth while avoiding deep nesting, sequences use **a single level of hierarchy** based on **domain or use case**.

```text
sequences/
├── README.md
├── security/
│   ├── suspicious_local_llm_frameworks.yml
│   ├── credential_access_lateral_movement.yml
│   └── ransomware_pre_execution.yml
├── cloud/
│   └── cloud_persistence_iam_abuse.yml
└── network/
    └── lateral_movement_internal.yml
````

### Design Rationale

* One level of hierarchy only
* Categories are **conceptual**, not vendor-based
* Easy to extend without refactoring
* Clear separation of domains (security, cloud, network, etc.)

---

## File Naming Convention

```text
<attack_or_story_name>.yml
```

### Rules

* Lowercase only
* Underscore (`_`) separated
* Describes the **behavior or attack**
* Avoid vendor, product, or log-source names

Examples:

* `suspicious_local_llm_frameworks.yml`
* `credential_access_lateral_movement.yml`
* `cloud_persistence_iam_abuse.yml`

---

## What a Sequence Represents

A sequence represents:

* A **story** (attack, misuse, investigation)
* A set of **logical stages**
* Each stage is satisfied by **one or more event samples**
* Correlation across **vendors, platforms, and telemetry**

---

## Standard Sequence YAML Structure

Each sequence file is **self-contained** and consists of:

1. Story metadata
2. Narrative context
3. Ordered stages
4. Event sample references
5. Detection intent

---

## Story Metadata

```yaml
version: 1.0
id: 0b4396a1-aeff-412e-b39e-4e26457c780d
name: Suspicious Local LLM Frameworks
date: 2025-11-12
author: Rod Soto
category: shadow_ai
severity: medium
```

---

## Description & Rationale

```yaml
description: >
  Detect and investigate unauthorized local LLM frameworks
  running within enterprise environments.

why_it_matters: >
  Shadow AI deployments bypass governance controls, introduce
  data exposure risks, and create monitoring blind spots.
```

These sections are **analyst-facing** and intentionally verbose.

---

## Threat Context

```yaml
threat:
  tactics:
    - Discovery
    - Execution
  techniques:
    - Create or Modify System Process
    - Gather Victim Network Information
```

---

## Sequence Definition (Sample-Driven)

The **core of a sequence** is an ordered list of **stages**.
Each stage references **one or more event samples** from `samples/`.

```yaml
sequence:
  - name: Local LLM Framework Execution
    description: Execution of an unauthorized local LLM framework
    events:
      - sourcetype: windows:security
        sourcefile: samples/windows/eventcode_4688.yml

      - sourcetype: sysmon
        sourcefile: samples/windows/sysmon_event_1.yml

  - name: Model File Creation
    description: Local LLM model files written to disk
    events:
      - sourcetype: sysmon
        sourcefile: samples/windows/sysmon_event_11.yml

  - name: DNS Query to Model Repository
    description: Endpoint resolves external model repository domains
    events:
      - sourcetype: windows:dns
        sourcefile: samples/windows/dns_query.yml

      - sourcetype: cisco_asa
        sourcefile: samples/cisco/dns_request.yml
```

---

## Event Reference Model

Each `events` entry is a **reference**, not a definition.

```yaml
events:
  - sourcetype: <logical_sourcetype>
    sourcefile: <relative_path_to_samples>
```

### Rules

* `sourcefile` must point to `samples/`
* Paths are relative to the repository root
* Multiple samples can satisfy the same stage
* Stages are ordered by list position

---

## Ordering & Correlation

* Sequence order defines **attack progression**
* Correlation is explicit through stage grouping
* Timing is implied and may be inferred by simulators
* Engines may replay:

  * All events per stage
  * One representative event per stage

---

## Detections & Expectations

```yaml
detections:
  - name: Unauthorized Local LLM Execution
    expected: true

  - name: Suspicious Model File Creation
    expected: true
```

This defines **what analytics should trigger** when the sequence is executed.

---

## Simulation Intent

```yaml
simulation:
  objective: Detect shadow AI deployments
  expected_outcome: Analyst investigation initiated
  noise_level: low
```

---

## Design Philosophy

* **Samples provide data**
* **Sequences provide meaning**
* Behavior-first, vendor-agnostic
* Reusable, composable, and scalable
* Designed for detection validation and storytelling

---

## Goals of the Sequences Framework

* Model real-world attack behavior
* Enable cross-source correlation testing
* Validate analytic stories end-to-end
* Support SOC training and purple-team exercises
* Scale cleanly as sample coverage grows

---

## Future Enhancements

* Required vs optional stages
* Conditional and branching paths
* Campaigns (multiple sequences chained)
* MITRE ATT&CK ID mapping
* Sequence validation and linting
* Automated timeline generation

```

If you want next, I can:
- Produce a **complete real sequence YAML**
- Define a **formal sequence schema**
- Add **branching / optional stage logic**
- Design a **runner that resolves samples → timelines**

This structure clearly enforces that **sequences are built on top of samples**, while still giving you room to grow long-term.
```
