"""Tests for bitwatch.filter."""

from __future__ import annotations

import pytest
from bitwatch.filter import EventFilter, build_filter


# ---------------------------------------------------------------------------
# EventFilter.matches
# ---------------------------------------------------------------------------

def test_no_patterns_accepts_all():
    f = EventFilter()
    assert f.matches("some/path/file.txt", "modified") is True


def test_include_pattern_match():
    f = EventFilter(include_patterns=["*.py"])
    assert f.matches("/src/main.py", "created") is True


def test_include_pattern_no_match():
    f = EventFilter(include_patterns=["*.py"])
    assert f.matches("/src/main.txt", "created") is False


def test_exclude_pattern_blocks():
    f = EventFilter(exclude_patterns=["*.log"])
    assert f.matches("/var/app.log", "modified") is False


def test_exclude_does_not_block_unmatched():
    f = EventFilter(exclude_patterns=["*.log"])
    assert f.matches("/var/app.py", "modified") is True


def test_event_type_filter_pass():
    f = EventFilter(event_types=["created", "deleted"])
    assert f.matches("file.txt", "created") is True


def test_event_type_filter_block():
    f = EventFilter(event_types=["created"])
    assert f.matches("file.txt", "modified") is False


def test_combined_include_and_event_type():
    f = EventFilter(include_patterns=["*.py"], event_types=["modified"])
    assert f.matches("app.py", "modified") is True
    assert f.matches("app.py", "deleted") is False
    assert f.matches("app.txt", "modified") is False


# ---------------------------------------------------------------------------
# build_filter
# ---------------------------------------------------------------------------

class _FakeTarget:
    def __init__(self, include=None, exclude=None, event_types=None):
        self.include_patterns = include
        self.exclude_patterns = exclude
        self.event_types = event_types


def test_build_filter_defaults():
    ef = build_filter(_FakeTarget())
    assert ef.include_patterns == []
    assert ef.exclude_patterns == []
    assert ef.event_types is None


def test_build_filter_values():
    ef = build_filter(_FakeTarget(include=["*.py"], exclude=["test_*"], event_types=["created"]))
    assert ef.include_patterns == ["*.py"]
    assert ef.exclude_patterns == ["test_*"]
    assert ef.event_types == ["created"]
