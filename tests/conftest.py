"""shared fixtures. every test gets an isolated sqlite file."""

from __future__ import annotations

import os
import pytest

from dolater import store


@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "state.db"


@pytest.fixture
def conn(db_path):
    c = store.connect(db_path)
    yield c
    c.close()


@pytest.fixture
def isolated_home(tmp_path, monkeypatch):
    """point DOLATER_HOME at a tmp dir so the cli doesn't touch ~/.dolater."""
    home = tmp_path / "dolhome"
    monkeypatch.setenv("DOLATER_HOME", str(home))
    return home
