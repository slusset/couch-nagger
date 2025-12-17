#!/bin/bash
#
# Deployment script for couch-nagger to Raspberry Pi
# Usage: ./deploy.sh [setup|update] [pi_hostname]
#

set -e

# Configuration
PI_USER="pi"
PI_HOST="${2:-raspberrypi.local}"  # Default to raspberrypi.local
PI_DIR="/home/pi/couch-nagger"
DEPLOY_MODE="${1:-update}"  # Default to update

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if rsync is installed
    if ! command -v rsync &> /dev/null; then
        log_error "rsync is not installed. Please install it first."
        exit 1
    fi
    
    # Check SSH connectivity
    log_info "Testing SSH connection to ${PI_USER}@${PI_HOST}..."
    if ! ssh -o ConnectTimeout=5 -o BatchMode=yes "${PI_USER}@${PI_HOST}" exit 2>/dev/null; then
        log_error "Cannot connect to ${PI_USER}@${PI_HOST}"
        log_error "Please ensure:"
        log_error "  1. Raspberry Pi is powered on and connected to network"
        log_error "  2. SSH is enabled on the Pi"
        log_error "  3. SSH key is set up (run: ssh-copy-id ${PI_USER}@${PI_HOST})"
        exit 1
    fi
    
    log_info "SSH connection successful!"
}

# Sync code to Pi
sync_code() {
    log_info "Syncing code to ${PI_HOST}..."
    
    rsync -avz --delete \
        --exclude '.git' \
        --exclude '.pytest_cache' \
        --exclude '__pycache__' \
        --exclude '*.pyc' \
        --exclude '.venv' \
        --exclude 'venv' \
        --exclude '*.egg-info' \
        --exclude 'yolov8*.pt' \
        --exclude 'images/*.jpg' \
        --exclude 'result.jpg' \
        ./ "${PI_USER}@${PI_HOST}:${PI_DIR}/"
    
    log_info "Code sync complete!"
}

# Run setup on Pi
setup_pi() {
    log_info "Running setup on Raspberry Pi..."
    
    ssh "${PI_USER}@${PI_HOST}" bash -s << 'ENDSSH'
set -e

log_info() {
    echo -e "\033[0;32m[PI-INFO]\033[0m $1"
}

log_info "Starting Pi setup..."

# Create directory if it doesn't exist
if [ ! -d "/home/pi/couch-nagger" ]; then
    log_info "Creating couch-nagger directory..."
    mkdir -p /home/pi/couch-nagger
fi

cd /home/pi/couch-nagger

# Make scripts executable
chmod +x scripts/*.sh

# Run bootstrap for system dependencies
log_info "Running system bootstrap..."
./scripts/pi_bootstrap.sh

# Install uv if not present
if ! command -v uv &> /dev/null; then
    log_info "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

# Create virtual environment with uv (using system python + site packages)
log_info "Setting up Python environment with uv..."
# We force recreation to ensure flags are correct
rm -rf .venv
uv venv .venv --python /usr/bin/python3 --system-site-packages

source .venv/bin/activate

# Install package in editable mode with Pi extras
log_info "Installing couch-nagger package..."
uv pip install -e ".[raspberrypi]"

# Download lightweight model
log_info "Downloading YOLOv8 nano model..."
if [ ! -f "yolov8n.pt" ]; then
    wget -q https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8n.pt
    log_info "Model downloaded successfully"
else
    log_info "Model already exists"
fi

log_info "Running health check..."
./scripts/pi_health_check.sh

log_info "Pi setup complete!"
ENDSSH
    
    log_info "Pi setup script completed!"
}

# Install systemd service
install_service() {
    log_info "Installing systemd service..."
    
    ssh "${PI_USER}@${PI_HOST}" bash -s << 'ENDSSH'
set -e

log_info() {
    echo -e "\033[0;32m[PI-INFO]\033[0m $1"
}

# Copy service file
log_info "Installing service file..."
sudo cp /home/pi/couch-nagger/systemd/couch-nagger.service /etc/systemd/system/

# Reload systemd
log_info "Reloading systemd..."
sudo systemctl daemon-reload

# Enable service
log_info "Enabling service..."
sudo systemctl enable couch-nagger.service

# Start service
log_info "Starting service..."
sudo systemctl start couch-nagger.service

log_info "Service installed and started!"
ENDSSH
    
    log_info "Service installation complete!"
}

# Restart service
restart_service() {
    log_info "Restarting couch-nagger service..."
    
    ssh "${PI_USER}@${PI_HOST}" bash -s << 'ENDSSH'
set -e

log_info() {
    echo -e "\033[0;32m[PI-INFO]\033[0m $1"
}

if systemctl is-active --quiet couch-nagger.service; then
    log_info "Restarting service..."
    sudo systemctl restart couch-nagger.service
    log_info "Service restarted!"
else
    log_info "Service not running, starting it..."
    sudo systemctl start couch-nagger.service
    log_info "Service started!"
fi
ENDSSH
}

# Show service status
show_status() {
    log_info "Checking service status..."
    ssh "${PI_USER}@${PI_HOST}" "sudo systemctl status couch-nagger.service --no-pager -l" || true
}

# Show logs
show_logs() {
    log_info "Showing recent logs..."
    ssh "${PI_USER}@${PI_HOST}" "sudo journalctl -u couch-nagger.service -n 50 --no-pager"
}

# Main deployment logic
main() {
    echo ""
    log_info "=== Couch Nagger Deployment ==="
    log_info "Mode: ${DEPLOY_MODE}"
    log_info "Target: ${PI_USER}@${PI_HOST}"
    echo ""
    
    check_prerequisites
    
    if [ "${DEPLOY_MODE}" = "setup" ]; then
        log_info "Performing initial setup..."
        sync_code
        setup_pi
        install_service
        show_status
        echo ""
        log_info "Setup complete! Service is now running."
        log_info "To view logs: ./deploy.sh logs ${PI_HOST}"
        log_info "To check status: ./deploy.sh status ${PI_HOST}"
        
    elif [ "${DEPLOY_MODE}" = "update" ]; then
        log_info "Performing update..."
        sync_code
        # Update dependencies
        ssh "${PI_USER}@${PI_HOST}" "cd ${PI_DIR} && source .venv/bin/activate && uv pip install -e \".[raspberrypi]\""
        restart_service
        show_status
        echo ""
        log_info "Update complete! Service has been restarted."
        
    elif [ "${DEPLOY_MODE}" = "status" ]; then
        show_status
        
    elif [ "${DEPLOY_MODE}" = "logs" ]; then
        show_logs
        
    elif [ "${DEPLOY_MODE}" = "restart" ]; then
        restart_service
        show_status
        
    else
        log_error "Unknown mode: ${DEPLOY_MODE}"
        echo ""
        echo "Usage: ./deploy.sh [mode] [pi_hostname]"
        echo ""
        echo "Modes:"
        echo "  setup   - Initial setup (install everything)"
        echo "  update  - Update code and restart service (default)"
        echo "  status  - Show service status"
        echo "  logs    - Show recent logs"
        echo "  restart - Restart the service"
        echo ""
        echo "Examples:"
        echo "  ./deploy.sh setup raspberrypi.local"
        echo "  ./deploy.sh update 192.168.1.100"
        echo "  ./deploy.sh logs"
        exit 1
    fi
    
    echo ""
    log_info "=== Deployment Complete ==="
    echo ""
}

main
