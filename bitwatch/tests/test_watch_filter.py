"""Tests for bitwatch.watch_filter module."""
import json
import pytest
from bitwatch.watch_filter import load_filters, event_allowed, targets_for_event


@pytest.fixture
def filter_file(tmp_path):
    p = tmp_path / "filters.json"
    return p


def test_load_filters_missing(filter_file):
    result = load_filters(filter_file)
    assert result == {}


def test_load_filters_corrupt(filter_file):
    filter_file.write_text("not json")
    assert load_filters(filter_file) == {}


def test_load_filters_valid(filter_file):
    data = {"src": ["created", "modified"], "logs": ["deleted"]}
    filter_file.write_text(json.dumps(data))
    result = load_filters(filter_file)
    assert result["src"] == ["created", "modified"]
    assert result["logs"] == ["deleted"]


def test_event_allowed_no_filter():
    assert event_allowed({}, "any_target", "created") is True


def test_event_allowed_matching():
    filters = {"src": ["created", "modified"]}
    assert event_allowed(filters, "src", "created") is True


def test_event_allowed_blocked():
    filters = {"src": ["created"]}
    assert event_allowed(filters, "src", "deleted") is False


def test_event_allowed_unknown_target():
    filters = {"src": ["created"]}
    assert event_allowed(filters, "other", "deleted") is True


def test_targets_for_event():
    filters = {"src": ["created", "modified"], "logs": ["deleted"]}
    result = targets_for_event(filters, "created")
    assert "src" in result
    assert "logs" not in result
