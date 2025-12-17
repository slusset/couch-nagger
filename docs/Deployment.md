# Deployment Guide

Complete guide for deploying couch-nagger to Raspberry Pi.

## Prerequisites

### On Your Laptop

- SSH access to Raspberry Pi
- rsync installed
- Git repository cloned

### On Raspberry Pi

- Raspberry Pi 3, 4, or 5 with Raspberry Pi OS
- Pi Camera Module connected and enabled
- SSH enabled
- Internet connection
- At least 2GB free disk space

## Quick Start

### 1. Set Up SSH Key

From your laptop, copy your SSH key to the Pi:

```bash
ssh-copy-id pi@raspberrypi.local
```

Test connection:

```bash
ssh pi@raspberrypi.local
```

### 2. Initial Deployment

From your laptop, in the project directory:

```bash
chmod +x deploy.sh
./deploy.sh setup raspberrypi.local
```

This will:
- Sync code to Pi
- Install `uv` package manager
- Create Python virtual environment
- Install all dependencies
- Download YOLOv8 nano model
- Install and start systemd service

### 3. Verify Deployment

Check service status:

```bash
./deploy.sh status raspberrypi.local
```

View logs:

```bash
./deploy.sh logs raspberrypi.local
```

## Deployment Commands

### Setup (First Time)

```bash
./deploy.sh setup [pi_hostname]
```

Performs complete initial setup including service installation.

### Update (After Code Changes)

```bash
./deploy.sh update [pi_hostname]
```

Syncs code changes and restarts service.

### Check Status

```bash
./deploy.sh status [pi_hostname]
```

Shows systemd service status.

### View Logs

```bash
./deploy.sh logs [pi_hostname]
```

Shows recent log entries.

### Restart Service

```bash
./deploy.sh restart [pi_hostname]
```

Restarts the monitoring service.

## Configuration

### Environment Variables

Create `/home/pi/couch-nagger/config/production.env`:

```bash
# Copy example file
ssh pi@raspberrypi.local
cd couch-nagger
cp config/production.env.example config/production.env
nano config/production.env
```

Edit values:

```bash
MODEL_PATH=yolov8n.pt
CONFIDENCE_THRESHOLD=0.20
CHECK_INTERVAL=10
ALERT_COOLDOWN=300
LOG_LEVEL=INFO
```

Restart service after changes:

```bash
sudo systemctl restart couch-nagger.service
```

### Notification Setup

Add notification credentials to `production.env`:

#### Pushover

```bash
PUSHOVER_TOKEN=your_app_token
PUSHOVER_USER=your_user_key
```

#### Slack

```bash
SLACK_TOKEN=xoxb-your-bot-token
SLACK_CHANNEL=#alerts
```

#### Email

```bash
EMAIL_SENDER=your_email@gmail.com
EMAIL_RECIPIENT=alert_recipient@gmail.com
EMAIL_PASSWORD=your_app_password
```

See [Examples](Examples.md#notification-integration) for implementation details.

## Manual Setup

If you prefer manual setup or the deployment script doesn't work:

### On Raspberry Pi

```bash
# 1. Clone repository
cd ~
git clone https://github.com/slusset/couch-nagger.git
cd couch-nagger

# 2. Run setup script
chmod +x scripts/setup_pi.sh
./scripts/setup_pi.sh

# 3. Install systemd service
sudo cp systemd/couch-nagger.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable couch-nagger.service
sudo systemctl start couch-nagger.service

# 4. Check status
sudo systemctl status couch-nagger.service
```

## Service Management

### View Status

```bash
sudo systemctl status couch-nagger.service
```

### Start Service

```bash
sudo systemctl start couch-nagger.service
```

### Stop Service

```bash
sudo systemctl stop couch-nagger.service
```

### Restart Service

```bash
sudo systemctl restart couch-nagger.service
```

### View Logs

```bash
# Recent logs
sudo journalctl -u couch-nagger.service -n 50

# Follow logs in real-time
sudo journalctl -u couch-nagger.service -f

# Today's logs
sudo journalctl -u couch-nagger.service --since today
```

### Disable Auto-start

```bash
sudo systemctl disable couch-nagger.service
```

### Enable Auto-start

```bash
sudo systemctl enable couch-nagger.service
```

## Testing

### Test Camera

```bash
ssh pi@raspberrypi.local
libcamera-hello --list-cameras
```

### Test Detection

```bash
ssh pi@raspberrypi.local
cd couch-nagger
source .venv/bin/activate

# Test with example image
python -c "
from dog_detector import DogDetector
detector = DogDetector('yolov8n.pt')
result = detector.check_image('images/test_dog_on_couch.jpg', 0.20)
print(f'Result: {result}')
"
```

### Test Monitor Script

Run manually to test:

```bash
ssh pi@raspberrypi.local
cd couch-nagger
source .venv/bin/activate
python src/monitor.py
```

Press Ctrl+C to stop.

## Troubleshooting

### Service Won't Start

```bash
# Check for errors
sudo journalctl -u couch-nagger.service -n 100

# Check service file
sudo systemctl cat couch-nagger.service

# Test manually
ssh pi@raspberrypi.local
cd couch-nagger
source .venv/bin/activate
python src/monitor.py
```

### Camera Not Working

```bash
# Enable camera
sudo raspi-config
# Interface Options -> Camera -> Enable

# Test camera
libcamera-hello --list-cameras
libcamera-still -o test.jpg
```

### Model Not Found

```bash
ssh pi@raspberrypi.local
cd couch-nagger

# Download manually
wget https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8n.pt
```

### Permission Issues

```bash
# Fix ownership
ssh pi@raspberrypi.local
sudo chown -R pi:pi /home/pi/couch-nagger

# Fix service permissions
sudo chmod 644 /etc/systemd/system/couch-nagger.service
sudo systemctl daemon-reload
```

### High CPU Usage

Adjust check interval in `production.env`:

```bash
CHECK_INTERVAL=15  # Check every 15 seconds instead of 10
```

## Performance Optimization

### Reduce Model Size

If inference is too slow, the nano model (yolov8n.pt) is already the smallest. Consider:

1. **Increase check interval**:
   ```bash
   CHECK_INTERVAL=15
   ```

2. **Reduce image resolution**:
   ```bash
   CAMERA_RESOLUTION_WIDTH=480
   CAMERA_RESOLUTION_HEIGHT=360
   ```

3. **Add motion detection** - only run YOLO when motion detected

### Monitor Resource Usage

```bash
# CPU and memory
ssh pi@raspberrypi.local htop

# Service resources
systemctl status couch-nagger.service
```

## Updating

### Update Code

From laptop:

```bash
./deploy.sh update raspberrypi.local
```

### Update Dependencies

```bash
ssh pi@raspberrypi.local
cd couch-nagger
source .venv/bin/activate
uv pip install -r requirements.txt --upgrade
sudo systemctl restart couch-nagger.service
```

### Update Model

```bash
ssh pi@raspberrypi.local
cd couch-nagger
rm yolov8n.pt
wget https://github.com/ultralytics/assets/releases/download/v8.3.0/yolov8n.pt
sudo systemctl restart couch-nagger.service
```

## Multiple Raspberry Pis

To deploy to multiple Pis:

```bash
# Create host list
PIS=("raspberrypi1.local" "raspberrypi2.local" "raspberrypi3.local")

# Deploy to all
for pi in "${PIS[@]}"; do
    echo "Deploying to $pi..."
    ./deploy.sh update "$pi"
done
```

## Backup and Restore

### Backup Configuration

```bash
# From laptop
scp pi@raspberrypi.local:/home/pi/couch-nagger/config/production.env ./backup/
```

### Restore Configuration

```bash
# From laptop
scp ./backup/production.env pi@raspberrypi.local:/home/pi/couch-nagger/config/
ssh pi@raspberrypi.local "sudo systemctl restart couch-nagger.service"
```

## Security Considerations

1. **Never commit production.env** - it contains secrets
2. **Use SSH keys** instead of passwords
3. **Restrict SSH access** - consider key-only authentication
4. **Keep Pi updated**:
   ```bash
   sudo apt update && sudo apt upgrade
   ```
5. **Monitor logs** for unusual activity

## Best Practices

1. **Test locally first** before deploying to Pi
2. **Use version control** - commit changes before deploying
3. **Monitor service health** regularly
4. **Keep logs** for debugging
5. **Document configuration changes**
6. **Test after updates** to ensure service still works

## Related Documentation

- [Installation](Installation.md) - Manual installation guide
- [Configuration](Configuration.md) - Configuration options
- [Examples](Examples.md) - Usage examples
- [Troubleshooting](Troubleshooting.md) - Common issues

## Getting Help

If deployment fails:

1. Check logs: `./deploy.sh logs raspberrypi.local`
2. Test SSH: `ssh pi@raspberrypi.local`
3. Check disk space: `ssh pi@raspberrypi.local df -h`
4. Review service status: `./deploy.sh status raspberrypi.local`
5. Create an issue on GitHub with error logs
