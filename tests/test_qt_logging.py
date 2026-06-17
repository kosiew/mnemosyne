import os

from mnemosyne.pyqt_ui.qt_logging import suppress_spurious_qt_pointer_dispatch_logs


def test_suppresses_qt_pointer_dispatch_logs_when_no_rules(monkeypatch):
    monkeypatch.delenv("QT_LOGGING_RULES", raising=False)

    suppress_spurious_qt_pointer_dispatch_logs()

    assert os.environ["QT_LOGGING_RULES"] == "qt.pointer.dispatch=false"


def test_preserves_existing_qt_logging_rules(monkeypatch):
    monkeypatch.setenv("QT_LOGGING_RULES", "qt.network.ssl.warning=false")

    suppress_spurious_qt_pointer_dispatch_logs()

    assert os.environ["QT_LOGGING_RULES"] == (
        "qt.network.ssl.warning=false;qt.pointer.dispatch=false"
    )


def test_does_not_duplicate_existing_qt_pointer_dispatch_rule(monkeypatch):
    monkeypatch.setenv("QT_LOGGING_RULES", "qt.pointer.dispatch=true")

    suppress_spurious_qt_pointer_dispatch_logs()

    assert os.environ["QT_LOGGING_RULES"] == "qt.pointer.dispatch=true"
