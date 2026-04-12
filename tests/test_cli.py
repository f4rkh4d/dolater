"""cli smoke tests with click's runner. uses DOLATER_HOME env var for isolation."""

from __future__ import annotations

from click.testing import CliRunner

from dolater.cli import main


def _run(args, env_home):
    runner = CliRunner()
    return runner.invoke(main, args, env={"DOLATER_HOME": str(env_home)})


def test_ls_on_empty(isolated_home):
    r = _run(["ls"], isolated_home)
    assert r.exit_code == 0
    assert "empty" in r.output


def test_add_then_ls(isolated_home):
    r = _run(["add", "ship the repo"], isolated_home)
    assert r.exit_code == 0
    r2 = _run(["ls"], isolated_home)
    assert "ship the repo" in r2.output


def test_fourth_add_exits_one(isolated_home):
    for t in ["a", "b", "c"]:
        assert _run(["add", t], isolated_home).exit_code == 0
    r = _run(["add", "d"], isolated_home)
    assert r.exit_code == 1
    assert "blocked" in r.output


def test_done_removes_item(isolated_home):
    _run(["add", "a"], isolated_home)
    r = _run(["done", "1"], isolated_home)
    assert r.exit_code == 0
    assert "done" in r.output
    r2 = _run(["ls"], isolated_home)
    assert "empty" in r2.output or "a" not in r2.output


def test_drop_records_in_log(isolated_home):
    _run(["add", "kill this"], isolated_home)
    _run(["drop", "1"], isolated_home)
    r = _run(["log"], isolated_home)
    assert "dropped" in r.output
    assert "kill this" in r.output


def test_done_empty_slot_errors(isolated_home):
    r = _run(["done", "2"], isolated_home)
    assert r.exit_code == 1
    assert "empty" in r.output


def test_bad_slot_errors(isolated_home):
    r = _run(["done", "9"], isolated_home)
    assert r.exit_code == 1


def test_clear_with_yes(isolated_home):
    _run(["add", "a"], isolated_home)
    r = _run(["clear", "--yes"], isolated_home)
    assert r.exit_code == 0
    r2 = _run(["ls"], isolated_home)
    assert "empty" in r2.output


def test_version_flag(isolated_home):
    r = _run(["--version"], isolated_home)
    assert r.exit_code == 0
    assert "0.2.1" in r.output
