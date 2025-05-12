#!/usr/bin/env bash

set -e

# -----------------------------------------------------------------------------
# Usage and command-line argument parsing
# -----------------------------------------------------------------------------
function usage() {
    echo "Usage: $0 [--disable-webserver] [--disable-taskexecutor] [--consumer-no-beg=<num>] [--consumer-no-end=<num>] [--workers=<num>] [--host-id=<string>]"
    echo
    echo "  --disable-webserver             Disables the web server (nginx + ragflow_server)."
    echo "  --disable-taskexecutor          Disables task executor workers."
    echo "  --enable-mcpserver              Enables the MCP server."
    echo "  --consumer-no-beg=<num>         Start range for consumers (if using range-based)."
    echo "  --consumer-no-end=<num>         End range for consumers (if using range-based)."
    echo "  --workers=<num>                 Number of task executors to run (if range is not used)."
    echo "  --host-id=<string>              Unique ID for the host (defaults to \`hostname\`)."
    echo
    echo "Environment variables:"
    echo "  RAGFLOW_ENABLE_WEBSERVER        Set to 0 to disable webserver (default: 1)"
    echo "  RAGFLOW_ENABLE_TASKEXECUTOR     Set to 0 to disable task executor (default: 1)"
    echo "  RAGFLOW_ENABLE_MCP_SERVER       Set to 1 to enable MCP server (default: 0)"
    echo "  RAGFLOW_CONSUMER_NO_BEG         Start range for consumers (default: 0)"
    echo "  RAGFLOW_CONSUMER_NO_END         End range for consumers (default: 0)"
    echo "  RAGFLOW_WORKERS                 Number of task executors (default: 1)"
    echo "  RAGFLOW_HOST_ID                 Unique ID for the host (defaults to hostname)"
    echo "  RAGFLOW_MCP_HOST                MCP server host (default: 127.0.0.1)"
    echo "  RAGFLOW_MCP_PORT                MCP server port (default: 9382)"
    echo "  RAGFLOW_MCP_BASE_URL            MCP base URL (default: http://127.0.0.1:9380)"
    echo "  RAGFLOW_MCP_MODE                MCP mode (default: self-host)"
    echo "  RAGFLOW_MCP_HOST_API_KEY        MCP host API key"
    echo
    echo "Examples:"
    echo "  $0 --disable-taskexecutor"
    echo "  $0 --disable-webserver --consumer-no-beg=0 --consumer-no-end=5"
    echo "  $0 --disable-webserver --workers=2 --host-id=myhost123"
    echo "  $0 --enable-mcpserver"
    exit 1
}

# Load from environment variables first (with defaults)
ENABLE_WEBSERVER=${RAGFLOW_ENABLE_WEBSERVER:-1}
ENABLE_TASKEXECUTOR=${RAGFLOW_ENABLE_TASKEXECUTOR:-1}
ENABLE_MCP_SERVER=${RAGFLOW_ENABLE_MCP_SERVER:-0}
CONSUMER_NO_BEG=${RAGFLOW_CONSUMER_NO_BEG:-0}
CONSUMER_NO_END=${RAGFLOW_CONSUMER_NO_END:-0}
WORKERS=${RAGFLOW_WORKERS:-1}

MCP_HOST=${RAGFLOW_MCP_HOST:-"127.0.0.1"}
MCP_PORT=${RAGFLOW_MCP_PORT:-9382}
MCP_BASE_URL=${RAGFLOW_MCP_BASE_URL:-"http://127.0.0.1:9380"}
MCP_SCRIPT_PATH=${RAGFLOW_MCP_SCRIPT_PATH:-"/ragflow/mcp/server/server.py"}
MCP_MODE=${RAGFLOW_MCP_MODE:-"self-host"}
MCP_HOST_API_KEY=${RAGFLOW_MCP_HOST_API_KEY:-""}

# -----------------------------------------------------------------------------
# Host ID logic:
#   1. By default, use the system hostname if length <= 32
#   2. Otherwise, use the full MD5 hash of the hostname (32 hex chars)
# -----------------------------------------------------------------------------
CURRENT_HOSTNAME="$(hostname)"
if [ ${#CURRENT_HOSTNAME} -le 32 ]; then
    DEFAULT_HOST_ID="$CURRENT_HOSTNAME"
else
    DEFAULT_HOST_ID="$(echo -n "$CURRENT_HOSTNAME" | md5sum | cut -d ' ' -f 1)"
fi

HOST_ID=${RAGFLOW_HOST_ID:-"$DEFAULT_HOST_ID"}

# Parse arguments (override environment variables)
for arg in "$@"; do
    case $arg in
    --disable-webserver)
        ENABLE_WEBSERVER=0
        shift
        ;;
    --disable-taskexecutor)
        ENABLE_TASKEXECUTOR=0
        shift
        ;;
    --enable-mcpserver)
        ENABLE_MCP_SERVER=1
        shift
        ;;
    --mcp-host=*)
        MCP_HOST="${arg#*=}"
        shift
        ;;
    --mcp-port=*)
        MCP_PORT="${arg#*=}"
        shift
        ;;
    --mcp-base-url=*)
        MCP_BASE_URL="${arg#*=}"
        shift
        ;;
    --mcp-mode=*)
        MCP_MODE="${arg#*=}"
        shift
        ;;
    --mcp-host-api-key=*)
        MCP_HOST_API_KEY="${arg#*=}"
        shift
        ;;
    --mcp-script-path=*)
        MCP_SCRIPT_PATH="${arg#*=}"
        shift
        ;;
    --consumer-no-beg=*)
        CONSUMER_NO_BEG="${arg#*=}"
        shift
        ;;
    --consumer-no-end=*)
        CONSUMER_NO_END="${arg#*=}"
        shift
        ;;
    --workers=*)
        WORKERS="${arg#*=}"
        shift
        ;;
    --host-id=*)
        HOST_ID="${arg#*=}"
        shift
        ;;
    *)
        usage
        ;;
    esac
done

# Debug configuration (uncomment if needed)
# echo "Configuration:"
# echo "  ENABLE_WEBSERVER=$ENABLE_WEBSERVER"
# echo "  ENABLE_TASKEXECUTOR=$ENABLE_TASKEXECUTOR"
# echo "  ENABLE_MCP_SERVER=$ENABLE_MCP_SERVER"
# echo "  CONSUMER_NO_BEG=$CONSUMER_NO_BEG"
# echo "  CONSUMER_NO_END=$CONSUMER_NO_END"
# echo "  WORKERS=$WORKERS"
# echo "  HOST_ID=$HOST_ID"
# echo "  MCP_HOST=$MCP_HOST"
# echo "  MCP_PORT=$MCP_PORT"
# echo "  MCP_BASE_URL=$MCP_BASE_URL"

# -----------------------------------------------------------------------------
# Replace env variables in the service_conf.yaml file
# -----------------------------------------------------------------------------
CONF_DIR="/ragflow/conf"
TEMPLATE_FILE="${CONF_DIR}/service_conf.yaml.template"
CONF_FILE="${CONF_DIR}/service_conf.yaml"

rm -f "${CONF_FILE}"
while IFS= read -r line || [[ -n "$line" ]]; do
    eval "echo \"$line\"" >>"${CONF_FILE}"
done <"${TEMPLATE_FILE}"

export LD_LIBRARY_PATH="/usr/lib/x86_64-linux-gnu/"
PY=python3

# -----------------------------------------------------------------------------
# Function(s)
# -----------------------------------------------------------------------------

function task_exe() {
    local consumer_id="$1"
    local host_id="$2"

    JEMALLOC_PATH="$(pkg-config --variable=libdir jemalloc)/libjemalloc.so"
    while true; do
        LD_PRELOAD="$JEMALLOC_PATH" \
            "$PY" rag/svr/task_executor.py "${host_id}_${consumer_id}"
    done
}

function start_mcp_server() {
    echo "Starting MCP Server on ${MCP_HOST}:${MCP_PORT} with base URL ${MCP_BASE_URL}..."
    "$PY" "${MCP_SCRIPT_PATH}" \
        --host="${MCP_HOST}" \
        --port="${MCP_PORT}" \
        --base_url="${MCP_BASE_URL}" \
        --mode="${MCP_MODE}" \
        --api_key="${MCP_HOST_API_KEY}" &
}

# -----------------------------------------------------------------------------
# Start components based on flags
# -----------------------------------------------------------------------------

if [[ "${ENABLE_WEBSERVER}" -eq 1 ]]; then
    echo "Starting nginx..."
    /usr/sbin/nginx

    echo "Starting ragflow_server..."
    while true; do
        "$PY" api/ragflow_server.py
    done &
fi

if [[ "${ENABLE_MCP_SERVER}" -eq 1 ]]; then
    start_mcp_server
fi

if [[ "${ENABLE_TASKEXECUTOR}" -eq 1 ]]; then
    if [[ "${CONSUMER_NO_END}" -gt "${CONSUMER_NO_BEG}" ]]; then
        echo "Starting task executors on host '${HOST_ID}' for IDs in [${CONSUMER_NO_BEG}, ${CONSUMER_NO_END})..."
        for ((i = CONSUMER_NO_BEG; i < CONSUMER_NO_END; i++)); do
            task_exe "${i}" "${HOST_ID}" &
        done
    else
        # Otherwise, start a fixed number of workers
        echo "Starting ${WORKERS} task executor(s) on host '${HOST_ID}'..."
        for ((i = 0; i < WORKERS; i++)); do
            task_exe "${i}" "${HOST_ID}" &
        done
    fi
fi

wait
