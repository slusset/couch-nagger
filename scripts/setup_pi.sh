#!/bin/bash
#
# Raspberry Pi setup script
# This script should be run ON the Raspberry Pi
# It's also called by deploy.sh during initial setup
#

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_info "=== Raspberry Pi Setup ==="

# Navigate to project directory
cd "$(dirname "$0")/.."
PROJECT_DIR=$(pwd)

log_info "Project directory: ${PROJECT_DIR}"

# Install system dependencies
log_info "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y \
    python3-pip \
    python3-venv \
    python3-picamera2 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev

# Install uv if not present
if ! command -v uv &> /dev/null; then
    log_info "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Add to PATH for current session
    export PATH="$HOME/.local/bin:$PATH"
    
    # Add to .bashrc if not already there
    if ! grep -q '.local/bin' ~/.bashrc; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    fi
else
    log_info "uv is already installed"
fi

# Create virtual environment
log_info "Creating virtual environment with uv..."
if [ ! -d ".venv" ]; then
    uv venv --python 3.11 .venv
else
    log_warn "Virtual environment already exists"
fi

# Activate virtual environment
source .venv/bin/activate

# Install Python dependencies
log_info "Installing Python dependencies with uv..."
uv pip install -r requirements.txt

# Install package in editable mode
log_info "Installing couch-nagger package..."
uv pip install -e .

# Link system picamera2 to venv
log_info "Linking picamera2 to virtual environment..."
PYTHON_VERSION=$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
VENV_SITE_PACKAGES=".venv/lib/python${PYTHON_VERSION}/site-packages"
ln -sf /usr/lib/python3/dist-packages/picamera2 "${VENV_SITE_PACKAGES}/" 2>/dev/null || true
ln -sf /usr/lib/python3/dist-packages/libcamera "${VENV_SITE_PACKAGES}/" 2>/dev/null || true

# Download YOLOv8 nano model
log_info "Downloading YOLOv8 nano model..."
if [ ! -f "yolov8n.pt" ]; then
    wget -q --show-progress https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8n.pt
    log_info "Model downloaded: yolov8n.pt"
else
    log_warn "Model already exists: yolov8n.pt"
fi

# Test camera
log_info "Testing camera..."
if libcamera-hello --list-cameras &>/dev/null; then
    log_info "Camera is working!"
else
    log_warn "Camera test failed. Please check camera connection and enable camera in raspi-config"
fi

# Create config directory
mkdir -p config

# Test imports
log_info "Testing Python imports..."
python -c "from dog_detector import DogDetector; print('✓ dog_detector imported successfully')" || log_warn "Failed to import dog_detector"
python -c "import picamera2; print('✓ picamera2 imported successfully')" || log_warn "Failed to import picamera2"
python -c "from ultralytics import YOLO; print('✓ ultralytics imported successfully')" || log_warn "Failed to import ultralytics"

log_info "=== Setup Complete ==="
log_info ""
log_info "Next steps:"
log_info "  1. Create a monitoring script in src/monitor.py"
log_info "  2. Configure systemd service: sudo cp systemd/couch-nagger.service /etc/systemd/system/"
log_info "  3. Enable service: sudo systemctl enable couch-nagger.service"
log_info "  4. Start service: sudo systemctl start couch-nagger.service"
log_info ""
