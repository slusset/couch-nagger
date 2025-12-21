# Configuration Guide

## Running Locally (macOS)

1. Copy `local.env` to `.env` or set environment variable:
   ```bash
   export COUCH_NAGGER_ENV_FILE=config/local.env
   ```

2. Run from project root:
   ```bash
   cd /path/to/couch-nagger
   couch-monitor
   ```

## Deploying to Raspberry Pi

### Setup systemd service:

1. Copy and edit production config:
   ```bash
   cd /opt/couch-nagger/current
   cp config/production.env.example config/production.env
   # Edit config/production.env with your settings
   ```

2. Install systemd service:
   ```bash
   sudo cp config/couch-nagger.service.example /etc/systemd/system/couch-nagger.service
   sudo systemctl daemon-reload
   sudo systemctl enable couch-nagger
   sudo systemctl start couch-nagger
   ```

3. Check status:
   ```bash
   sudo systemctl status couch-nagger
   sudo journalctl -u couch-nagger -f  # Follow logs
   ```

### Directory Structure on Pi:
```
/opt/couch-nagger/
├── current/          # Symlink to active release (e.g., releases/v1.2.3)
│   ├── assets/
│   │   └── audio/   # Custom alert sounds
│   ├── config/
│   │   └── production.env
│   └── ...
├── shared/          # Persists across deployments
│   ├── models/      # YOLO model files
│   ├── captures/    # Detection images
│   └── logs/        # Application logs
└── venv/           # Python virtual environment
```

## Key Settings

### Working Directory
The app must be run with working directory set to project root. All paths in `.env` files are relative to this directory.

### Audio Configuration
- `ALERT_SOUND_DIR=assets/audio` - Directory containing custom alert sounds
- `ALERT_VOLUME=0.5` - Volume (0.0 to 1.0)
- `ALSA_DEVICE=plughw:3,0` - ALSA device on Pi (use `aplay -L` to list)

### Camera Adapter
The bootstrap automatically detects the platform:
- **Pi with Picamera2**: Uses hardware camera
- **Mac or Pi without camera**: Falls back to FileFrameSource (reads from IMAGE_DIR)
