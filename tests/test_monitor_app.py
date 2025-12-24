import time
from typing import Any, Optional

from dog_detector.app.couch_monitor import CouchMonitorApp
from dog_detector.domain.model import DetectionResult, Frame
from dog_detector.ports.frame_source import FrameSourcePort
from dog_detector.ports.detector import DetectorPort
from dog_detector.ports.alert_sink import AlertSinkPort
from dog_detector.settings import (
    AppSettings,
    ModelSettings,
    DetectionSettings,
    CameraSettings,
    LoggingSettings,
    AudioSettings,
)


class FakeFrameSource(FrameSourcePort):
    def __init__(self, frame: Any = "frame"):
        self.frame = frame
        self.calls = 0

    def get_frame(self) -> tuple[Frame, Optional[str]]:
        self.calls += 1
        return self.frame, None  # type: ignore[return-value]


class FakeDetector(DetectorPort):
    def __init__(self, result: DetectionResult):
        self.result = result
        self.frames = []

    def detect(self, frame: Frame, image_filename: Optional[str] = None) -> DetectionResult:
        self.frames.append(frame)
        return self.result


class FakeAlertSink(AlertSinkPort):
    def __init__(self):
        self.alerts = []

    def alert(self, result):
        self.alerts.append(result)


def create_test_settings(
    check_interval: float = 0.0,
    alert_cooldown: float = 300.0,
    test_mode: bool = False,
) -> AppSettings:
    """Create AppSettings for testing with customizable parameters."""
    return AppSettings(
        model=ModelSettings(
            model_path="yolov8n.pt",
            confidence_threshold=0.20,
            person_confidence_threshold=0.25,
        ),
        detection=DetectionSettings(
            check_interval=check_interval,
            alert_cooldown=alert_cooldown,
            test_mode=test_mode,
        ),
        camera=CameraSettings(
            width=640,
            height=480,
        ),
        logging=LoggingSettings(
            level="INFO",
            file="logs/test.log",
        ),
        audio=AudioSettings(
            alsa_device="default",
            alert_sound="/tmp/test.wav",
            aplay_quiet=True,
        ),
    )


def test_alert_triggers_when_dog_on_couch(monkeypatch):
    result = DetectionResult(dog_on_couch=True, confidence={}, boxes={})
    app = CouchMonitorApp(
        frame_source=FakeFrameSource(),
        detector=FakeDetector(result),
        alert_sink=FakeAlertSink(),
        settings=create_test_settings(),
    )

    monkeypatch.setattr(time, "time", lambda: 1000.0)
    app.check_and_alert()

    assert len(app.alert_sink.alerts) == 1


def test_cooldown_prevents_repeat_alert(monkeypatch):
    result = DetectionResult(dog_on_couch=True, confidence={}, boxes={})
    app = CouchMonitorApp(
        frame_source=FakeFrameSource(),
        detector=FakeDetector(result),
        alert_sink=FakeAlertSink(),
        settings=create_test_settings(check_interval=0.0, alert_cooldown=300.0),
    )

    monkeypatch.setattr(time, "time", lambda: 1000.0)
    app.check_and_alert()

    monkeypatch.setattr(time, "time", lambda: 1100.0)
    app.check_and_alert()

    assert len(app.alert_sink.alerts) == 1


def test_alert_after_cooldown_expires(monkeypatch):
    result = DetectionResult(dog_on_couch=True, confidence={}, boxes={})
    app = CouchMonitorApp(
        frame_source=FakeFrameSource(),
        detector=FakeDetector(result),
        alert_sink=FakeAlertSink(),
        settings=create_test_settings(check_interval=0.0, alert_cooldown=300.0),
    )

    monkeypatch.setattr(time, "time", lambda: 1000.0)
    app.check_and_alert()

    monkeypatch.setattr(time, "time", lambda: 1401.0)
    app.check_and_alert()

    assert len(app.alert_sink.alerts) == 2


def test_no_alert_when_no_dog_on_couch():
    result = DetectionResult(dog_on_couch=False, confidence={}, boxes={})
    app = CouchMonitorApp(
        frame_source=FakeFrameSource(),
        detector=FakeDetector(result),
        alert_sink=FakeAlertSink(),
        settings=create_test_settings(check_interval=0.0, alert_cooldown=300.0),
    )

    app.check_and_alert()

    assert len(app.alert_sink.alerts) == 0


def test_errors_in_check_cycle_do_not_raise():
    class BoomFrameSource(FrameSourcePort):
        def get_frame(self) -> tuple[Frame, Optional[str]]:
            raise RuntimeError("camera failure")

    result = DetectionResult(dog_on_couch=True, confidence={}, boxes={})
    app = CouchMonitorApp(
        frame_source=BoomFrameSource(),
        detector=FakeDetector(result),
        alert_sink=FakeAlertSink(),
        settings=create_test_settings(check_interval=0.0, alert_cooldown=300.0),
    )

    app.check_and_alert()
