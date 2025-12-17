#!/bin/bash
#
# Bootstrap script for Raspberry Pi OS dependencies
#
set -e

echo "=== Raspberry Pi Bootstrap ==="
echo "Updating apt package list..."
sudo apt update

echo "Installing system packages..."
# Core camera stack + build dependencies
# Note: rpicam-apps is the new name in Bookworm, but we include libcamera-apps as fallback/alias if needed, 
# though apt might complain if one is missing. We'll try to install the standard Bookworm set.

PACKAGES=(
    python3-picamera2
    python3-libcamera
    rpicam-apps
    python3-prctl
    libcap-dev
    python3-dev
    build-essential
    pkg-config
)

# Filter out packages that are already installed to keep output clean (optional, but apt handles it well)
sudo apt install -y "${PACKAGES[@]}"

echo "Bootstrap complete! System dependencies are installed."
