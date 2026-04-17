"""Tests for bitwatch.alert module."""
import json
import pytest
from pathlib import Path
from bitwatch.alert import load_rules, matching_rules, urls_for_event


@pytest.fixture
def rules():
    return [
        {"target": "/tmp/watch", "url": "http://hook1", "events": ["created", "modified"]},
        {"target": "/tmp/other", "url": "http://hook2", "events": ["deleted"]},
    ]


def test_load_rules_missing_file(tmp_path):
    result = load_rules(tmp_path / "nonexistent.json")
    assert result == []


def test_load_rules_corrupt_file(tmp_path):
    f = tmp_path / "alerts.json"
    f.write_text("not json")
    assert load_rules(f) == []


def test_load_rules_valid(tmp_path):
    data = [{"target": "/a", "url": "http://x", "events": ["created"]}]
    f = tmp_path / "alerts.json"
    f.write_text(json.dumps(data))
    assert load_rules(f) == data


def test_matching_rules_hit(rules):
    result = matching_rules("created", "/tmp/watch", rules)
    assert len(result) == 1
    assert result[0]["url"] == "http://hook1"


def test_matching_rules_wrong_event(rules):
    result = matching_rules("deleted", "/tmp/watch", rules)
    assert result == []


def test_matching_rules_no_target_match(rules):
    result = matching_rules("created", "/tmp/unrelated", rules)
    assert result == []


def test_urls_for_event(tmp_path, rules):
    f = tmp_path / "alerts.json"
    f.write_text(json.dumps(rules))
    urls = urls_for_event("modified", "/tmp/watch", alerts_file=f)
    assert urls == ["http://hook1"]


def test_urls_for_event_passes_rules(rules):
    urls = urls_for_event("deleted", "/tmp/other", rules=rules)
    assert urls == ["http://hook2"]
