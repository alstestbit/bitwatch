"""Tests for mirror.py and mirror_cmd.py."""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from bitwatch import mirror as _mirror
from bitwatch.commands import mirror_cmd


@pytest.fixture()
def mfile(tmp_path: Path) -> Path:
    return tmp_path / "mirrors.json"


def _args(tmp_path, **kw):
    cfg = tmp_path / "bitwatch.json"
    defaults = dict(
        action="list",
        target=None,
        dest=None,
        mirrors_file=str(tmp_path / "mirrors.json"),
        config=str(cfg),
        func=mirror_cmd.run,
    )
    defaults.update(kw)
    return SimpleNamespace(**defaults)


def test_load_mirrors_missing(mfile):
    assert _mirror.load_mirrors(mfile) == {}


def test_load_mirrors_corrupt(mfile):
    mfile.write_text("not json")
    assert _mirror.load_mirrors(mfile) == {}


def test_save_and_load_roundtrip(mfile):
    data = {"logs": "/tmp/backup"}
    _mirror.save_mirrors(data, mfile)
    assert _mirror.load_mirrors(mfile) == data


def test_mirror_path_found():
    mirrors = {"logs": "/tmp/bak"}
    assert _mirror.mirror_path("logs", mirrors) == "/tmp/bak"


def test_mirror_path_missing():
    assert _mirror.mirror_path("x", {}) is None


def test_perform_mirror_file(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    f = src / "a.txt"
    f.write_text("hello")
    dest = tmp_path / "dest"
    copied = _mirror.perform_mirror(str(f), str(dest))
    assert len(copied) == 1
    assert Path(copied[0]).read_text() == "hello"


def test_perform_mirror_missing_src(tmp_path):
    copied = _mirror.perform_mirror(str(tmp_path / "nope"), str(tmp_path / "dest"))
    assert copied == []


def test_cmd_list_empty(tmp_path, capsys):
    rc = mirror_cmd.run(_args(tmp_path, action="list"))
    assert rc == 0
    assert "No mirrors" in capsys.readouterr().out


def test_cmd_set_and_list(tmp_path, capsys):
    a = _args(tmp_path, action="set", target="logs", dest="/bak")
    mirror_cmd.run(a)
    a2 = _args(tmp_path, action="list", mirrors_file=a.mirrors_file)
    mirror_cmd.run(a2)
    out = capsys.readouterr().out
    assert "logs" in out and "/bak" in out


def test_cmd_set_missing_args(tmp_path, capsys):
    rc = mirror_cmd.run(_args(tmp_path, action="set"))
    assert rc == 1


def test_cmd_remove(tmp_path, capsys):
    mf = str(tmp_path / "mirrors.json")
    _mirror.save_mirrors({"x": "/d"}, Path(mf))
    rc = mirror_cmd.run(_args(tmp_path, action="remove", target="x", mirrors_file=mf))
    assert rc == 0
    assert _mirror.load_mirrors(Path(mf)) == {}
