"""store logic. no mocks — real sqlite on tmp_path."""

from __future__ import annotations

import pytest

from dolater import store
from dolater.store import BadSlot, ListFull, SlotEmpty


def test_empty_list(conn):
    assert store.list_items(conn) == []
    assert store.count_items(conn) == 0


def test_add_one(conn):
    item = store.add_item(conn, "write tests")
    assert item.slot == 1
    assert item.text == "write tests"
    assert store.count_items(conn) == 1


def test_add_fills_lowest_slot(conn):
    store.add_item(conn, "a")
    store.add_item(conn, "b")
    store.add_item(conn, "c")
    items = store.list_items(conn)
    assert [i.slot for i in items] == [1, 2, 3]
    assert [i.text for i in items] == ["a", "b", "c"]


def test_fourth_add_blocked(conn):
    store.add_item(conn, "a")
    store.add_item(conn, "b")
    store.add_item(conn, "c")
    with pytest.raises(ListFull):
        store.add_item(conn, "d")


def test_done_frees_slot(conn):
    store.add_item(conn, "a")
    store.add_item(conn, "b")
    store.add_item(conn, "c")
    store.complete(conn, 2)
    slots = [i.slot for i in store.list_items(conn)]
    assert slots == [1, 3]
    # next add should land in slot 2
    store.add_item(conn, "d")
    by_slot = {i.slot: i.text for i in store.list_items(conn)}
    assert by_slot[2] == "d"


def test_drop_frees_slot_and_logs(conn):
    store.add_item(conn, "burn me")
    store.drop(conn, 1)
    assert store.list_items(conn) == []
    entries = store.log_entries(conn)
    assert len(entries) == 1
    assert entries[0].action == "dropped"
    assert entries[0].text == "burn me"


def test_log_records_done(conn):
    store.add_item(conn, "ship it")
    store.complete(conn, 1)
    entries = store.log_entries(conn)
    assert entries[0].action == "done"
    assert entries[0].text == "ship it"


def test_done_empty_slot_raises(conn):
    with pytest.raises(SlotEmpty):
        store.complete(conn, 2)


def test_bad_slot_numbers(conn):
    with pytest.raises(BadSlot):
        store.complete(conn, 0)
    with pytest.raises(BadSlot):
        store.drop(conn, 4)


def test_add_empty_text_rejected(conn):
    with pytest.raises(ValueError):
        store.add_item(conn, "   ")


def test_wipe_clears_everything(conn):
    store.add_item(conn, "a")
    store.complete(conn, 1)
    store.wipe(conn)
    assert store.list_items(conn) == []
    assert store.log_entries(conn) == []


def test_log_tail(conn):
    for t in ["a", "b", "c"]:
        store.add_item(conn, t)
        store.complete(conn, 1)
    entries = store.log_entries(conn, tail=2)
    assert len(entries) == 2
    # newest first
    assert entries[0].text == "c"
