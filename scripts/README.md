# Scripts Directory

This directory contains utility scripts for setting up and managing the Couch Nagger application on a Raspberry Pi.

## Setup Workflows

### 1. Fresh Raspberry Pi Image (Initial Setup)

For a brand new Raspberry Pi OS installation, follow these steps in order:

1. **Bootstrap system dependencies:**
   ```bash
   ./scripts/pi_bootstrap.sh
   ```
   Installs core system packages (picamera2, libcamera, rpicam-apps, build tools)

2. **Setup project environment:**
   ```bash
   ./scripts/setup_pi.sh
   ```
   Creates venv, installs Python dependencies, downloads YOLOv8 model

3. **Verify installation:**
   ```bash
   ./scripts/pi_health_check.sh
   ```
   Validates environment and dependencies

4. **Test camera:**
   ```bash
   python scripts/cam_test.py
   ```
   Confirms camera hardware is working

### 2. Updating the Application (System Libraries Already Installed)

After initial setup, use these scripts to deploy updates:

**On the Raspberry Pi:**
```bash
./scripts/pi_deploy.sh
```
Creates a timestamped release, clones the repo, sets up venv, and symlinks to `/opt/couch-nagger/current`

**From your laptop (remote deployment):**
```bash
./scripts/remote_deploy.sh
```
Executes `pi_deploy.sh` on the Pi via SSH (default: `raspberry@couch-nagger.local`)

**Custom deployment:**
```bash
# Use different model
MODEL_NAME=yolov8n.pt ./scripts/remote_deploy.sh

# Use different host/user
REMOTE_HOST=192.168.1.100 REMOTE_USER=pi ./scripts/remote_deploy.sh
```

---

## Script Reference

### pi_bootstrap.sh
Bootstrap script for installing core Raspberry Pi OS dependencies.

**Purpose:** Installs system-level packages required for camera functionality and Python development.

**Installs:**
- `python3-picamera2` - Python interface for the camera
- `python3-libcamera` - Camera stack library
- `rpicam-apps` - Raspberry Pi camera applications
- `python3-prctl` - Process control capabilities
- `libcap-dev`, `python3-dev`, `build-essential`, `pkg-config` - Build dependencies

**Usage:**
```bash
./scripts/pi_bootstrap.sh
```

**When to use:** Run this first on a fresh Raspberry Pi OS installation before setting up the project.

---

### setup_pi.sh
Complete setup script for the Couch Nagger project on Raspberry Pi.

**Purpose:** Sets up the entire development environment including virtual environment, dependencies, and models.

**What it does:**
1. Installs system dependencies (Python, picamera2, OpenCV libraries)
2. Installs `uv` package manager if not present
3. Creates Python 3.11 virtual environment
4. Installs Python dependencies from `requirements.txt`
5. Installs the couch-nagger package in editable mode
6. Links system picamera2 packages to the virtual environment
7. Downloads the YOLOv8 nano model (`yolov8n.pt`)
8. Tests camera functionality
9. Verifies Python imports

**Usage:**
```bash
./scripts/setup_pi.sh
```

**When to use:** Run after `pi_bootstrap.sh` to complete the full project setup. Can also be called by `deploy.sh` during initial deployment.

---

### pi_health_check.sh
Health check script to verify the Raspberry Pi environment is properly configured.

**Purpose:** Validates that all required dependencies and camera functionality are working.

**Checks:**
- System architecture and Python version
- `rpicam-still` command availability
- Python `libcamera` import
- Python `picamera2` import

**Usage:**
```bash
./scripts/pi_health_check.sh
```

**Exit codes:**
- `0` - All checks passed
- `1` - One or more checks failed

**When to use:** Run after setup or deployment to verify everything is working correctly.

---

### cam_test.py
Simple camera test script to verify the Picamera2 module is functioning.

**Purpose:** Captures a test image using the Raspberry Pi camera.

**What it does:**
1. Initializes Picamera2 with 640x480 resolution
2. Starts the camera
3. Captures an image to `/tmp/picam2.jpg`
4. Prints confirmation and stops the camera

**Usage:**
```bash
python scripts/cam_test.py
```

**When to use:** Quick test to verify camera hardware and picamera2 library are working properly.

---

### pi_deploy.sh
Production deployment script for creating timestamped releases.

**Purpose:** Clones the repository into a release directory, sets up the environment, and creates a symlink to the current release.

**What it does:**
1. Creates timestamped release directory: `/opt/couch-nagger/releases/YYYYMMDD_HHMMSS/app`
2. Clones repository from `git@github.com:slusset/couch-nagger.git`
3. Creates Python virtual environment with `--system-site-packages`
4. Installs dependencies using `uv pip install`
5. Downloads YOLOv8 model to `/opt/couch-nagger/shared/models/` if missing
6. Tests Python imports
7. Creates symlink: `/opt/couch-nagger/current` → release app directory

**Usage:**
```bash
./scripts/pi_deploy.sh
MODEL_NAME=yolov8n.pt ./scripts/pi_deploy.sh  # Use different model
```

**When to use:** Run on the Pi to deploy updates after initial system setup is complete.

---

### remote_deploy.sh
Remote deployment wrapper that executes `pi_deploy.sh` on the Raspberry Pi from your laptop.

**Purpose:** Deploy updates to the Pi without SSH'ing in manually.

**What it does:**
1. Tests SSH connectivity to the Pi
2. Copies `pi_deploy.sh` to the remote Pi
3. Executes it remotely with real-time output
4. Passes environment variables (MODEL_NAME, etc.)
5. Cleans up temporary files

**Configuration:**
- `REMOTE_HOST` - Default: `couch-nagger.local`
- `REMOTE_USER` - Default: `raspberry`
- `MODEL_NAME` - Default: `yolov8m.pt`

**Usage:**
```bash
./scripts/remote_deploy.sh
MODEL_NAME=yolov8n.pt ./scripts/remote_deploy.sh
REMOTE_HOST=192.168.1.100 ./scripts/remote_deploy.sh
```

**When to use:** Run from your laptop to deploy updates to the Pi remotely.

---
