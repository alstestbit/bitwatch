"""Unit tests for bitwatch.profile."""
import json
import pytest
from pathlib import Path
from bitwatch import profile as prof


@pytest.fixture
def pfile(tmp_path):
    return tmp_path / "profiles.json"


def test_load_profiles_missing(pfile):
    assert prof.load_profiles(pfile) == {}


def test_load_profiles_corrupt(pfile):
    pfile.write_text("not-json")
    assert prof.load_profiles(pfile) == {}


def test_load_profiles_wrong_type(pfile):
    pfile.write_text(json.dumps([1, 2, 3]))
    assert prof.load_profiles(pfile) == {}


def test_set_and_get_profile(pfile):
    prof.set_profile("dev", {"verbose": True, "config": "dev.json"}, pfile)
    result = prof.get_profile("dev", pfile)
    assert result == {"verbose": True, "config": "dev.json"}


def test_get_missing_profile(pfile):
    assert prof.get_profile("ghost", pfile) is None


def test_profile_names(pfile):
    prof.set_profile("a", {}, pfile)
    prof.set_profile("b", {}, pfile)
    assert set(prof.profile_names(pfile)) == {"a", "b"}


def test_delete_profile(pfile):
    prof.set_profile("tmp", {"x": 1}, pfile)
    assert prof.delete_profile("tmp", pfile) is True
    assert prof.get_profile("tmp", pfile) is None


def test_delete_missing_profile(pfile):
    assert prof.delete_profile("nope", pfile) is False


def test_overwrite_profile(pfile):
    prof.set_profile("p", {"v": 1}, pfile)
    prof.set_profile("p", {"v": 2}, pfile)
    assert prof.get_profile("p", pfile)["v"] == 2
