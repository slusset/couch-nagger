#!/bin/bash
#
# Deployment script for Raspberry Pi
# Creates a timestamped release, clones the repo, and sets up the environment
#
set -euo pipefail

# Configuration
MODEL_NAME="${MODEL_NAME:-yolov8m.pt}"
SHARED_MODELS_DIR="/opt/couch-nagger/shared/models"

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

# Create release directory
CURRENT_DATETIME=$(date +%Y%m%d_%H%M%S)
RELEASE_DIR="/opt/couch-nagger/releases/${CURRENT_DATETIME}"
APP_DIR="${RELEASE_DIR}/app"

log_info "=== Couch Nagger Deployment ==="
log_info "Release directory: ${RELEASE_DIR}"

# Create release directory
log_info "Creating release directory..."
sudo mkdir -p "${RELEASE_DIR}"
sudo chown $USER:$USER "${RELEASE_DIR}"

# Clone repository
log_info "Cloning repository..."
git clone git@github.com:slusset/couch-nagger.git "${APP_DIR}"

echo "Changing to ${APP_DIR}"
# Navigate to app directory
cd "${APP_DIR}"

# Make sure lock exists in the fresh repo
# Temporary branch switch
git switch hex-app-entrypoint
[ -f uv.lock ] || { log_error "uv.lock not found. Commit uv.lock to the repo."; exit 1; }

# Add uv to PATH (it's installed in ~/.local/bin by default)
export PATH="$HOME/.local/bin:$PATH"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    log_error "uv is not installed. Please run setup_pi.sh or install uv first."
    exit 1
fi

# Create virtual environment with system site packages access
log_info "Creating virtual environment (system python + system site packages)..."
rm -rf .venv
uv venv --python /usr/bin/python3 --system-site-packages

# Install Python dependencies
log_info "Installing Python dependencies from uv.lock..."
uv sync --frozen --extra raspberrypi

# Ensure shared models directory exists
log_info "Checking for YOLOv8 model: ${MODEL_NAME}"
sudo mkdir -p "${SHARED_MODELS_DIR}"
sudo chown $USER:$USER "${SHARED_MODELS_DIR}"

MODEL_PATH="${SHARED_MODELS_DIR}/${MODEL_NAME}"
if [ ! -f "${MODEL_PATH}" ]; then
    log_info "Downloading ${MODEL_NAME}..."
    # Extract version from model name (e.g., yolov8m -> 8, n -> n, etc.)
    MODEL_VERSION=$(echo "${MODEL_NAME}" | sed -n 's/yolov8\(.\)\.pt/\1/p')
    wget -q --show-progress -O "${MODEL_PATH}" "https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8${MODEL_VERSION}.pt"
    log_info "Model downloaded: ${MODEL_PATH}"
else
    log_info "Model already exists: ${MODEL_PATH}"
fi

# Test imports
log_info "Testing Python imports..."
.venv/bin/python -c "import libcamera; print('✓ libcamera')"
.venv/bin/python -c "from picamera2 import Picamera2; print('✓ picamera2')"
.venv/bin/python -c "import torch; print('✓ torch', torch.__version__)"
.venv/bin/python -c "from ultralytics import YOLO; print('✓ ultralytics')"

# Create symlink to current release
log_info "Creating 'current' symlink..."
sudo rm -f /opt/couch-nagger/current
sudo ln -s "${APP_DIR}" /opt/couch-nagger/current

log_info "=== Deployment Complete ==="
log_info ""
log_info "Release deployed to: ${RELEASE_DIR}"
log_info "Current symlink points to: /opt/couch-nagger/current"
log_info ""
log_info "Next steps:"
log_info "  1. Update systemd service to use: /opt/couch-nagger/current"
log_info "  2. Restart service: sudo systemctl restart couch-nagger.service"
log_info ""
