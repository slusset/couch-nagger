import time

from dog_detector.app.monitor import CouchMonitorApp
from dog_detector.domain.model import DetectionResult


class FakeFrameSource:
    def __init__(self, frame="frame"):
        self.frame = frame
        self.calls = 0

    def get_frame(self):
        self.calls += 1
        return self.frame


class FakeDetector:
    def __init__(self, result: DetectionResult):
        self.result = result
        self.frames = []

    def detect(self, frame):
        self.frames.append(frame)
        return self.result


class FakeAlertSink:
    def __init__(self):
        self.alerts = []

    def alert(self, result):
        self.alerts.append(result)


def test_alert_triggers_when_dog_on_couch(monkeypatch):
    result = DetectionResult(dog_on_couch=True, confidence={}, boxes={})
    app = CouchMonitorApp(
        frame_source=FakeFrameSource(),
        detector=FakeDetector(result),
        alert_sink=FakeAlertSink(),
        check_interval=0.0,
        alert_cooldown=300.0,
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
        check_interval=0.0,
        alert_cooldown=300.0,
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
        check_interval=0.0,
        alert_cooldown=300.0,
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
        check_interval=0.0,
        alert_cooldown=300.0,
    )

    app.check_and_alert()

    assert len(app.alert_sink.alerts) == 0


def test_errors_in_check_cycle_do_not_raise():
    class BoomFrameSource:
        def get_frame(self):
            raise RuntimeError("camera failure")

    result = DetectionResult(dog_on_couch=True, confidence={}, boxes={})
    app = CouchMonitorApp(
        frame_source=BoomFrameSource(),
        detector=FakeDetector(result),
        alert_sink=FakeAlertSink(),
        check_interval=0.0,
        alert_cooldown=300.0,
    )

    app.check_and_alert()
