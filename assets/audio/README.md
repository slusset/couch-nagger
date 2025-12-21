# Audio Alert Files

This directory contains audio files used for couch detection alerts.

## Supported Formats
- `.wav` (recommended)
- `.mp3`
- `.ogg`

## Usage
Place your custom audio files here. The system will randomly select one file each time an alert is triggered.

## Recording Custom Audio
To record your own voice commands (e.g., "Fonzy, get down!"):
- **macOS**: Use QuickTime Player (File > New Audio Recording) or Voice Memos app
- **Linux/Pi**: Use `arecord -f cd -d 3 output.wav` (3 second recording)

Export/save as WAV format for best compatibility.
