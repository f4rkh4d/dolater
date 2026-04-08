"""rich output. orange #ff4500 for accents, red for blocks, dim for times."""

from __future__ import annotations

from rich.console import Console
from rich.text import Text

from .store import Item, LogEntry

ORANGE = "#ff4500"
console = Console()


def _fmt_ts(ts: str) -> str:
    # iso is fine for humans enough. trim the timezone suffix to keep it tidy.
    return ts.replace("T", " ").replace("+00:00", "Z")


def show_items(items: list[Item]) -> None:
    if not items:
        console.print(Text("(empty — no slots used)", style="dim"))
        return
    by_slot = {i.slot: i for i in items}
    for n in range(1, 4):
        it = by_slot.get(n)
        line = Text()
        line.append(f" {n} ", style=f"bold {ORANGE}")
        line.append("· ", style="dim")
        if it is None:
            line.append("—", style="dim")
        else:
            line.append(it.text)
        console.print(line)


def show_added(item: Item) -> None:
    t = Text()
    t.append("+ ", style=f"bold {ORANGE}")
    t.append("added ", style=f"{ORANGE}")
    t.append(f"slot {item.slot}", style="bold")
    t.append(" · ")
    t.append(item.text)
    console.print(t)


def show_done(item: Item) -> None:
    t = Text()
    t.append("done: ", style="bold green")
    t.append(item.text)
    console.print(t)


def show_dropped(item: Item) -> None:
    t = Text()
    t.append("dropped: ", style="bold yellow")
    t.append(item.text, style="dim")
    console.print(t)


def show_blocked() -> None:
    console.print(Text("! blocked — list is full", style="bold red"))


def show_error(msg: str) -> None:
    console.print(Text(f"! {msg}", style="bold red"))


def show_log(entries: list[LogEntry]) -> None:
    if not entries:
        console.print(Text("(no history yet)", style="dim"))
        return
    for e in entries:
        t = Text()
        t.append(_fmt_ts(e.timestamp), style="dim")
        t.append("  ")
        if e.action == "done":
            t.append("done   ", style="green")
        else:
            t.append("dropped", style="yellow")
        t.append("  ")
        t.append(e.text)
        console.print(t)


def show_cleared() -> None:
    console.print(Text("wiped. start over.", style=f"bold {ORANGE}"))
