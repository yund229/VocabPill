"""VocabPill core: word banks, Leitner-box scheduler, persistent progress.

Pure standard library, GUI-free — everything here is unit-testable.
"""

from __future__ import annotations

import datetime as dt
import json
import random
import re
from importlib import resources
from pathlib import Path

__all__ = [
    "LEVELS",
    "LevelError",
    "IntervalError",
    "load_bank",
    "parse_interval",
    "format_card",
    "Deck",
]

LEVELS = ("cet4", "cet6")

MAX_BOX = 5  # Leitner boxes 0..5


class LevelError(ValueError):
    """Raised for an unknown vocabulary level."""


class IntervalError(ValueError):
    """Raised for an unparseable interval string."""


def _data_dir():
    root = resources.files("vocabpill")
    return root / "data"


def load_bank(level: str) -> list[dict]:
    """Return the word list for *level* ('cet4' or 'cet6').

    Each entry is a dict with keys: word, phonetic, meaning, example.
    """
    if level not in LEVELS:
        raise LevelError(f"unknown level {level!r}; choose from {', '.join(LEVELS)}")
    raw = (_data_dir() / f"{level}.json").read_text(encoding="utf-8")
    words = json.loads(raw)["words"]
    if not words:
        raise LevelError(f"bank for {level!r} is empty")
    return words


def parse_interval(text: str) -> int:
    """Parse '45s' / '30m' / '2h' (or bare seconds) into seconds."""
    m = re.fullmatch(r"\s*(\d+)\s*([smh]?)\s*", text, re.IGNORECASE)
    if not m:
        raise IntervalError(f"bad interval {text!r}; use e.g. 45s, 30m, 2h")
    n, unit = int(m.group(1)), m.group(2).lower()
    factor = {"": 1, "s": 1, "m": 60, "h": 3600}[unit]
    seconds = n * factor
    if seconds < 5:
        raise IntervalError("interval must be at least 5 seconds")
    return seconds


def format_card(entry: dict) -> str:
    """Render one word entry as a plain-text card (CLI / --once mode)."""
    lines = [entry["word"]]
    if entry.get("phonetic"):
        lines.append(entry["phonetic"])
    lines.append(entry["meaning"])
    if entry.get("example"):
        lines.append(f"e.g. {entry['example']}")
    return "\n".join(lines)


def default_state_path(level: str) -> Path:
    home = Path.home() / ".vocabpill"
    home.mkdir(exist_ok=True)
    return home / f"state_{level}.json"


class Deck:
    """A Leitner-box deck over one level's word bank, with daily stats.

    State layout (JSON):
        {"boxes": {"word": {"box": int, "seen": int, "ok": int}},
         "log": {"YYYY-MM-DD": int}}
    """

    def __init__(self, level: str, state_path: Path | None = None,
                 rng: random.Random | None = None):
        self.level = level
        self.words = load_bank(level)
        self.index = {w["word"]: w for w in self.words}
        self.state_path = Path(state_path) if state_path else default_state_path(level)
        self.rng = rng or random.Random()
        self.state = self._load()

    # ---------- persistence ----------

    def _load(self) -> dict:
        if self.state_path.exists():
            try:
                data = json.loads(self.state_path.read_text(encoding="utf-8"))
                if isinstance(data, dict) and "boxes" in data:
                    return data
            except (json.JSONDecodeError, OSError):
                pass
        return {"boxes": {}, "log": {}}

    def save(self) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(
            json.dumps(self.state, ensure_ascii=False, indent=1), encoding="utf-8")

    # ---------- scheduling ----------

    def _record(self, word: str) -> dict:
        boxes = self.state.setdefault("boxes", {})
        if word not in boxes:
            boxes[word] = {"box": 0, "seen": 0, "ok": 0}
        return boxes[word]

    def pick_next(self) -> dict:
        """Pick the next word: always from the lowest box, random inside it.

        Unseen words sit in box 0, so brand-new words come first and
        mastered ones (box 5) are reviewed last.
        """
        boxes = self.state.setdefault("boxes", {})
        groups: dict[int, list[str]] = {}
        for w in self.index:
            rec = boxes.get(w) or {"box": 0}
            groups.setdefault(rec["box"], []).append(w)
        lowest = min(groups)
        word = self.rng.choice(groups[lowest])
        return self.index[word]

    def mark(self, word: str, known: bool) -> dict:
        """Record an answer. Known -> box up (capped), unknown -> box reset."""
        if word not in self.index:
            raise KeyError(f"word {word!r} is not in the {self.level} bank")
        rec = self._record(word)
        rec["seen"] += 1
        if known:
            rec["ok"] += 1
            rec["box"] = min(MAX_BOX, rec["box"] + 1)
        else:
            rec["box"] = 0
        today = dt.date.today().isoformat()
        log = self.state.setdefault("log", {})
        log[today] = log.get(today, 0) + 1
        return rec

    # ---------- stats ----------

    def stats(self) -> dict:
        """Return {'today', 'seen', 'mastered', 'total'} for this level."""
        boxes = self.state.get("boxes", {})
        today = dt.date.today().isoformat()
        return {
            "today": self.state.get("log", {}).get(today, 0),
            "seen": len(boxes),
            "mastered": sum(1 for r in boxes.values() if r["box"] >= MAX_BOX),
            "total": len(self.words),
        }

    def reset(self) -> None:
        """Wipe all progress for this level."""
        self.state = {"boxes": {}, "log": {}}
        if self.state_path.exists():
            self.state_path.unlink()
