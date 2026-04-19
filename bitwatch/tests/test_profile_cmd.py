"""Tests for bitwatch.commands.profile_cmd."""
import json
import pytest
from pathlib import Path
from types import SimpleNamespace
from bitwatch.commands import profile_cmd


@pytest.fixture
def pfile(tmp_path):
    return tmp_path / "profiles.json"


def _args(action, name=None, flags=None, pfile=None):
    return SimpleNamespace(
        profile_action=action,
        name=name,
        flags=flags,
        profiles_file=str(pfile) if pfile else None,
    )


def test_list_empty(capsys, pfile):
    rc = profile_cmd.run(_args("list", pfile=pfile))
    assert rc == 0
    assert "No profiles" in capsys.readouterr().out


def test_save_and_list(capsys, pfile):
    rc = profile_cmd.run(_args("save", name="ci", flags='{"verbose": true}', pfile=pfile))
    assert rc == 0
    capsys.readouterr()
    profile_cmd.run(_args("list", pfile=pfile))
    assert "ci" in capsys.readouterr().out


def test_save_invalid_flags(capsys, pfile):
    rc = profile_cmd.run(_args("save", name="bad", flags="not-json", pfile=pfile))
    assert rc == 1
    assert "JSON" in capsys.readouterr().out


def test_show_profile(capsys, pfile):
    profile_cmd.run(_args("save", name="dev", flags='{"config": "dev.json"}', pfile=pfile))
    capsys.readouterr()
    rc = profile_cmd.run(_args("show", name="dev", pfile=pfile))
    assert rc == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["config"] == "dev.json"


def test_show_missing_profile(capsys, pfile):
    rc = profile_cmd.run(_args("show", name="ghost", pfile=pfile))
    assert rc == 1
    assert "not found" in capsys.readouterr().out


def test_delete_profile(capsys, pfile):
    profile_cmd.run(_args("save", name="tmp", flags="{}", pfile=pfile))
    capsys.readouterr()
    rc = profile_cmd.run(_args("delete", name="tmp", pfile=pfile))
    assert rc == 0
    assert "deleted" in capsys.readouterr().out


def test_delete_missing_profile(capsys, pfile):
    rc = profile_cmd.run(_args("delete", name="nope", pfile=pfile))
    assert rc == 1


def test_no_action(capsys, pfile):
    rc = profile_cmd.run(_args(None, pfile=pfile))
    assert rc == 1
