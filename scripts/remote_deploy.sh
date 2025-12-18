#!/bin/bash
#
# Remote deployment wrapper
# Executes pi_deploy.sh on the Raspberry Pi from your local machine
#
set -e

# Configuration
REMOTE_HOST="${REMOTE_HOST:-couch-nagger.local}"
REMOTE_USER="${REMOTE_USER:-raspberry}"
MODEL_NAME="${MODEL_NAME:-yolov8m.pt}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_info "=== Remote Deployment to ${REMOTE_USER}@${REMOTE_HOST} ==="

# Check if script exists locally
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DEPLOY_SCRIPT="${SCRIPT_DIR}/pi_deploy.sh"

if [ ! -f "${DEPLOY_SCRIPT}" ]; then
    log_error "pi_deploy.sh not found at ${DEPLOY_SCRIPT}"
    exit 1
fi

# Test SSH connection
log_info "Testing SSH connection..."
if ! ssh -o ConnectTimeout=5 "${REMOTE_USER}@${REMOTE_HOST}" 'echo "Connection successful"' > /dev/null 2>&1; then
    log_error "Cannot connect to ${REMOTE_USER}@${REMOTE_HOST}"
    log_error "Please check:"
    log_error "  - Host is reachable"
    log_error "  - SSH keys are configured"
    log_error "  - Username is correct"
    exit 1
fi
log_info "SSH connection successful"

# Copy deployment script to remote host
log_info "Copying pi_deploy.sh to remote host..."
scp -q "${DEPLOY_SCRIPT}" "${REMOTE_USER}@${REMOTE_HOST}:/tmp/pi_deploy.sh"

# Execute deployment script on remote host
log_info "Executing deployment on remote host..."
log_info "Model: ${MODEL_NAME}"
echo ""

ssh -t "${REMOTE_USER}@${REMOTE_HOST}" "MODEL_NAME=${MODEL_NAME} bash /tmp/pi_deploy.sh"

# Capture exit code
DEPLOY_EXIT_CODE=$?

# Cleanup
log_info "Cleaning up temporary files..."
ssh "${REMOTE_USER}@${REMOTE_HOST}" 'rm -f /tmp/pi_deploy.sh'

if [ ${DEPLOY_EXIT_CODE} -eq 0 ]; then
    log_info "=== Remote Deployment Complete ==="
else
    log_error "Deployment failed with exit code ${DEPLOY_EXIT_CODE}"
    exit ${DEPLOY_EXIT_CODE}
fi
