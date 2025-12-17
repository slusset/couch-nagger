#!/bin/bash
#
# Health check script for Raspberry Pi environment
#
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo "=== Pi Health Check ==="
echo -n "Architecture: "; uname -m
echo -n "Python System: "; python3 --version

# 1. Check Camera Apps
echo -n "Checking rpicam-still... "
if command -v rpicam-still &> /dev/null; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}MISSING${NC}"
    echo "  (Please run scripts/pi_bootstrap.sh)"
    exit 1
fi

# 2. Check Python Imports (System or Active Venv)
echo -n "Checking python import libcamera... "
if python3 -c "import libcamera; print('OK')" &> /dev/null; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED${NC}"
    echo "  (Ensure you are in a venv with --system-site-packages or using system python)"
    exit 1
fi

echo -n "Checking python import picamera2... "
if python3 -c "from picamera2 import Picamera2; print('OK')" &> /dev/null; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED${NC}"
    exit 1
fi

echo "=== Health Check Passed ==="
