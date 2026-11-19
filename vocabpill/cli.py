"""Command line interface.

    vocabpill --level cet4 --interval 30m   # pop a card every 30 minutes
    vocabpill --once --level cet6           # print one card, exit
    vocabpill --stats --level cet4          # today / seen / mastered
    vocabpill --reset --level cet4          # wipe progress
"""

from __future__ import annotations

import argparse
import sys

from vocabpill import __version__
from vocabpill.core import (
    LEVELS,
    Deck,
    IntervalError,
    LevelError,
    format_card,
    parse_interval,
)

DEFAULT_INTERVAL = "30m"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="vocabpill",
        description="Desktop flashcard pop-ups: CET-4 / CET-6 words, a pill at a time.",
    )
    p.add_argument("--level", choices=LEVELS, default="cet4",
                   help="word bank (default: cet4)")
    p.add_argument("--interval", default=DEFAULT_INTERVAL, metavar="30m",
                   help="pop-up period: 45s / 30m / 2h (default: 30m)")
    p.add_argument("--once", action="store_true",
                   help="print one card in the terminal and exit (no GUI)")
    p.add_argument("--stats", action="store_true",
                   help="show progress stats and exit")
    p.add_argument("--reset", action="store_true",
                   help="wipe progress for --level and exit")
    p.add_argument("--version", action="version", version=f"vocabpill {__version__}")
    return p


def run_once(deck: Deck) -> str:
    """Show one card in the terminal. The card stays unseen until answered,
    so a pure peek does not disturb the schedule."""
    card = deck.pick_next()
    return format_card(card)


def run_stats(deck: Deck) -> str:
    s = deck.stats()
    return (f"{deck.level}: today {s['today']} words | "
            f"seen {s['seen']}/{s['total']} | mastered {s['mastered']}")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        interval = parse_interval(args.interval)
    except IntervalError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    try:
        deck = Deck(args.level)
    except LevelError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    if args.reset:
        deck.reset()
        print(f"progress for {args.level} wiped")
        return 0
    if args.stats:
        print(run_stats(deck))
        return 0
    if args.once:
        print(run_once(deck))
        return 0

    # GUI mode: import tkinter only here, so headless machines can still
    # use --once / --stats.
    try:
        from vocabpill.popup import run_popup
    except ImportError:
        print("error: tkinter is not available in this Python build", file=sys.stderr)
        return 2
    run_popup(deck, interval)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
