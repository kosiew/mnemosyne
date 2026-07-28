import sys

import pytest

from mnemosyne.libmnemosyne.component_manager import _component_managers


class FakeComponentManager:
    def register(self, plugin):
        self.plugin = plugin


_component_managers["test"] = FakeComponentManager()
try:
    from mnemosyne.example_plugins.grade_button_interval_tooltips import (
        format_revision_interval,
        revision_interval_message,
    )
finally:
    _component_managers.pop("test", None)
    sys.modules.pop("mnemosyne.example_plugins.grade_button_interval_tooltips", None)


@pytest.mark.parametrize(
    ("seconds", "expected"),
    [
        (0, "today"),
        (24 * 60 * 60, "1 day"),
        (2 * 24 * 60 * 60, "2 days"),
        (31 * 24 * 60 * 60, "1 month"),
        (33 * 24 * 60 * 60, "1 month 2 days"),
        ((365 + 31 + 2) * 24 * 60 * 60, "1 year 1 month 2 days"),
    ],
)
def test_format_revision_interval(seconds, expected):
    assert format_revision_interval(seconds) == expected


@pytest.mark.parametrize(
    ("seconds", "expected"),
    [
        (0, "Next revision: today."),
        (33 * 24 * 60 * 60, "Next revision: in 1 month 2 days."),
    ],
)
def test_revision_interval_message(seconds, expected):
    assert revision_interval_message(seconds) == expected
