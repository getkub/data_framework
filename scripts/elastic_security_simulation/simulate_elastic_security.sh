#!/bin/bash
# =============================================================================
# simulate_elastic_security.sh - simulate Elastic Security data + ESQL rule
#
# Thin wrapper around simulate_esql.py.
#
# CREDENTIALS: no credentials are stored in any file. The Elastic password is
# resolved in this order:
#   1) $ELASTIC_PASSWORD environment variable (preferred - never commit it)
#   2) $ES_PASSWORD environment variable
#   3) fetched on-the-fly from the ECK k8s secret quickstart-es-elastic-user
#      (same mechanism as k8s_kubernetes/isolated/elastic/scripts/port-forward.sh)
#
# Usage:
#   # Default: re-simulate reference id 101 (C2 egress) incl. ESQL rule
#   ./simulate_elastic_security.sh
#
#   # Ingest any other reference NDJSON (no rule)
#   ./simulate_elastic_security.sh --ndjson ../<file>.ndjson --skip-rule
#
#   # Custom data stream + rule
#   ./simulate_elastic_security.sh \
#       --ndjson ../../data/sequence/security/linux/defense_evasion_base64_decoding_activity.ndjson \
#       --data-stream logs-linux.security-default \
#       --rule-id base64-decoding-102 --rule-name "[Sim] Base64 Decoding Activity" \
#       --query-file my_query.esql --severity medium --risk-score 47
#
# All remaining arguments are passed to simulate_esql.py (see --help there).
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# -----------------------------------------------------------------------------
# Resolve credentials (env first, k8s secret fallback - never persisted)
# -----------------------------------------------------------------------------
if [ -z "${ELASTIC_PASSWORD:-}" ] && [ -z "${ES_PASSWORD:-}" ]; then
    echo "[creds]   No ELASTIC_PASSWORD set - fetching from k8s secret (quickstart-es-elastic-user)..."
    PASSWORD="$(kubectl get secret quickstart-es-elastic-user -n elastic-system \
        -o go-template='{{.data.elastic | base64decode}}' 2>/dev/null || true)"
    if [ -n "$PASSWORD" ]; then
        export ELASTIC_PASSWORD="$PASSWORD"
        echo "[creds]   OK password resolved from k8s secret."
    fi
fi
if [ -z "${ELASTIC_PASSWORD:-}" ]; then
    echo "[creds]   ERROR: no Elastic password found." >&2
    echo "          Set it with:  export ELASTIC_PASSWORD='...'   (or ES_PASSWORD)" >&2
    echo "          or make sure 'kubectl' can read the quickstart-es-elastic-user secret." >&2
    exit 2
fi

# -----------------------------------------------------------------------------
# Default arguments (reference id 101 - C2 egress connections)
# -----------------------------------------------------------------------------
DEFAULT_NDJSON="${DATA_ROOT}/data/sequence/security/linux/command_and_control_frequent_egress_netcon_from_sus_executable.ndjson"
DEFAULT_DS="logs-linux.security-default"
DEFAULT_QUERY="${SCRIPT_DIR}/esql_c2_query.esql"

if [ "$#" -eq 0 ]; then
    set -- \
        --ndjson "${DEFAULT_NDJSON}" \
        --data-stream "${DEFAULT_DS}" \
        --rule-id c2-frequent-egress-netcon-101 \
        --rule-name "[Sim] High Number of Egress Network Connections from Unusual Executable" \
        --description "Simulation: high number of egress connections from unusual executable (ref id 101)." \
        --query-file "${DEFAULT_QUERY}" \
        --severity high --risk-score 73 --interval 5m
fi

# -----------------------------------------------------------------------------
# Run
# -----------------------------------------------------------------------------
echo "[run]     Executing: python3 ${SCRIPT_DIR}/simulate_esql.py $*"
python3 "${SCRIPT_DIR}/simulate_esql.py" "$@"