"""click commands. thin layer — store does the real work."""

from __future__ import annotations

import sys

import click

from . import __version__, render, store


def _conn():
    return store.connect(store.default_db_path())


@click.group(help="dolater — three slots. finish or drop.")
@click.version_option(__version__, prog_name="dolater")
def main() -> None:
    pass


@main.command("add", help="add an item. fails if 3 already exist.")
@click.argument("text")
def add_cmd(text: str) -> None:
    conn = _conn()
    try:
        item = store.add_item(conn, text)
    except store.ListFull:
        render.show_blocked()
        sys.exit(1)
    except ValueError:
        render.show_error("text can't be empty")
        sys.exit(1)
    render.show_added(item)
    render.show_items(store.list_items(conn))


@main.command("ls", help="show the three slots.")
def ls_cmd() -> None:
    conn = _conn()
    render.show_items(store.list_items(conn))


@main.command("done", help="mark a slot complete.")
@click.argument("n", type=int)
def done_cmd(n: int) -> None:
    conn = _conn()
    try:
        item = store.complete(conn, n)
    except store.BadSlot:
        render.show_error(f"slot {n} doesn't exist. pick 1, 2, or 3.")
        sys.exit(1)
    except store.SlotEmpty:
        render.show_error(f"slot {n} is empty.")
        sys.exit(1)
    render.show_done(item)
    render.show_items(store.list_items(conn))


@main.command("drop", help="drop a slot without completing it.")
@click.argument("n", type=int)
def drop_cmd(n: int) -> None:
    conn = _conn()
    try:
        item = store.drop(conn, n)
    except store.BadSlot:
        render.show_error(f"slot {n} doesn't exist. pick 1, 2, or 3.")
        sys.exit(1)
    except store.SlotEmpty:
        render.show_error(f"slot {n} is empty.")
        sys.exit(1)
    render.show_dropped(item)
    render.show_items(store.list_items(conn))


@main.command("log", help="history of done/dropped items.")
@click.option("--tail", type=int, default=None, help="show only the last N.")
def log_cmd(tail: int | None) -> None:
    conn = _conn()
    render.show_log(store.log_entries(conn, tail=tail))


@main.command("clear", help="wipe everything. asks first.")
@click.confirmation_option(prompt="wipe all items and history?")
def clear_cmd() -> None:
    conn = _conn()
    store.wipe(conn)
    render.show_cleared()


if __name__ == "__main__":
    main()
