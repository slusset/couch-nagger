import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from dog_detector.adapters.audio_alert import AudioAlert
from dog_detector.domain.model import DetectionResult


@pytest.fixture
def mock_pygame():
    """Mock pygame to avoid audio initialization during tests."""
    with patch("dog_detector.adapters.audio_alert.pygame") as mock:
        mock.mixer = MagicMock()
        mock.time = MagicMock()
        yield mock


def test_audio_alert_initializes_with_defaults(mock_pygame):
    alert = AudioAlert()

    assert alert.sound_file == "/usr/share/sounds/alsa/Front_Center.wav"
    assert alert.sound_dir is None
    assert alert.volume == 1.0
    mock_pygame.mixer.init.assert_called_once()


def test_audio_alert_with_custom_volume(mock_pygame):
    alert = AudioAlert(volume=0.5)
    assert alert.volume == 0.5


def test_volume_clamped_to_valid_range(mock_pygame):
    alert_low = AudioAlert(volume=-0.5)
    assert alert_low.volume == 0.0

    alert_high = AudioAlert(volume=2.0)
    assert alert_high.volume == 1.0


def test_plays_default_sound_file(mock_pygame):
    mock_sound = MagicMock()
    mock_pygame.mixer.Sound.return_value = mock_sound
    mock_pygame.mixer.get_busy.side_effect = [True, False]

    alert = AudioAlert(sound_file="/tmp/test.wav")
    result = DetectionResult(dog_on_couch=True, confidence={}, boxes={})

    alert.alert(result)

    mock_pygame.mixer.Sound.assert_called_once_with("/tmp/test.wav")
    mock_sound.set_volume.assert_called_once_with(1.0)
    mock_sound.play.assert_called_once()


def test_picks_random_sound_from_directory(mock_pygame, tmp_path):
    # Create test sound files
    sound_dir = tmp_path / "sounds"
    sound_dir.mkdir()
    (sound_dir / "bark1.wav").touch()
    (sound_dir / "bark2.wav").touch()
    (sound_dir / "bark3.mp3").touch()

    mock_sound = MagicMock()
    mock_pygame.mixer.Sound.return_value = mock_sound
    mock_pygame.mixer.get_busy.return_value = False

    alert = AudioAlert(sound_dir=str(sound_dir))
    result = DetectionResult(dog_on_couch=True, confidence={}, boxes={})

    alert.alert(result)

    # Verify a sound was played
    assert mock_pygame.mixer.Sound.call_count == 1
    played_file = mock_pygame.mixer.Sound.call_args[0][0]
    assert played_file in [
        str(sound_dir / "bark1.wav"),
        str(sound_dir / "bark2.wav"),
        str(sound_dir / "bark3.mp3"),
    ]


def test_handles_missing_sound_directory(mock_pygame, caplog):
    alert = AudioAlert(sound_dir="/nonexistent/path")
    result = DetectionResult(dog_on_couch=True, confidence={}, boxes={})

    alert.alert(result)

    assert "Alert sound directory not found" in caplog.text
    mock_pygame.mixer.Sound.assert_not_called()


def test_handles_empty_sound_directory(mock_pygame, tmp_path, caplog):
    sound_dir = tmp_path / "empty"
    sound_dir.mkdir()

    alert = AudioAlert(sound_dir=str(sound_dir))
    result = DetectionResult(dog_on_couch=True, confidence={}, boxes={})

    alert.alert(result)

    assert "No alert sounds found" in caplog.text
    mock_pygame.mixer.Sound.assert_not_called()


def test_handles_playback_error(mock_pygame, caplog):
    mock_pygame.mixer.Sound.side_effect = Exception("Audio device error")

    alert = AudioAlert(sound_file="/tmp/test.wav")
    result = DetectionResult(dog_on_couch=True, confidence={}, boxes={})

    alert.alert(result)

    assert "Failed to play alert sound" in caplog.text


def test_waits_for_sound_to_finish(mock_pygame):
    mock_sound = MagicMock()
    mock_pygame.mixer.Sound.return_value = mock_sound
    # Simulate sound playing for 3 iterations
    mock_pygame.mixer.get_busy.side_effect = [True, True, True, False]

    alert = AudioAlert(sound_file="/tmp/test.wav")
    result = DetectionResult(dog_on_couch=True, confidence={}, boxes={})

    alert.alert(result)

    # get_busy should be called 4 times (3 True, 1 False)
    assert mock_pygame.mixer.get_busy.call_count == 4
    assert mock_pygame.time.wait.call_count == 3
