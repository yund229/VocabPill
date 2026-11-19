"""Tests for banks, scheduler, persistence and CLI."""

from __future__ import annotations

import random

import pytest

from vocabpill.cli import build_parser, main, run_once, run_stats
from vocabpill.core import (
    MAX_BOX,
    Deck,
    IntervalError,
    LevelError,
    format_card,
    load_bank,
    parse_interval,
)

# ---------------- banks ----------------

def test_cet4_bank_is_large():
    assert len(load_bank("cet4")) >= 700


def test_cet6_bank_is_reasonable():
    assert 200 <= len(load_bank("cet6")) <= 1000


def test_every_entry_has_all_fields():
    for level in ("cet4", "cet6"):
        for w in load_bank(level):
            assert w["word"] and w["meaning"]
            assert isinstance(w["phonetic"], str)
            assert isinstance(w["example"], str)


def test_no_duplicate_words_within_a_bank():
    for level in ("cet4", "cet6"):
        words = [w["word"] for w in load_bank(level)]
        assert len(words) == len(set(words)), f"duplicates in {level}"


def test_cet6_has_no_words_duplicated_from_cet4():
    cet4 = {w["word"] for w in load_bank("cet4")}
    cet6 = {w["word"] for w in load_bank("cet6")}
    overlap = cet4 & cet6
    assert not overlap, f"shared words: {sorted(overlap)[:10]}"


def test_unknown_level_raises():
    with pytest.raises(LevelError):
        load_bank("gre")


# ---------------- interval parsing ----------------

@pytest.mark.parametrize("text, seconds", [
    ("45s", 45), ("45S", 45), ("30m", 1800), ("2h", 7200),
    ("10", 10), (" 30 m ", 1800),
])
def test_parse_interval_valid(text, seconds):
    assert parse_interval(text) == seconds


@pytest.mark.parametrize("text", ["abc", "m30", "30x", "", "-5s", "0m", "4s"])
def test_parse_interval_invalid(text):
    with pytest.raises(IntervalError):
        parse_interval(text)


# ---------------- deck scheduling ----------------

@pytest.fixture()
def deck(tmp_path):
    rng = random.Random(42)
    return Deck("cet6", state_path=tmp_path / "state.json", rng=rng)


def test_pick_next_returns_a_bank_word(deck):
    assert deck.pick_next() in deck.index.values()


def test_same_seed_same_pick(tmp_path):
    d1 = Deck("cet6", state_path=tmp_path / "a.json", rng=random.Random(9))
    d2 = Deck("cet6", state_path=tmp_path / "b.json", rng=random.Random(9))
    assert d1.pick_next()["word"] == d2.pick_next()["word"]


def test_mark_known_promotes_box(deck):
    card = deck.pick_next()
    rec = deck.mark(card["word"], known=True)
    assert rec["box"] == 1 and rec["seen"] == 1 and rec["ok"] == 1


def test_mark_unknown_resets_box(deck):
    word = deck.words[0]["word"]
    deck.mark(word, True)
    deck.mark(word, True)
    deck.mark(word, True)
    rec = deck.mark(word, False)
    assert rec["box"] == 0


def test_box_capped_at_max(deck):
    word = deck.words[0]["word"]
    for _ in range(10):
        deck.mark(word, True)
    assert deck.state["boxes"][word]["box"] == MAX_BOX


def test_lowest_box_words_come_first(deck):
    # promote every word except the first to a high box
    promoted = deck.words[1:5]
    for w in promoted:
        for _ in range(MAX_BOX):
            deck.mark(w["word"], True)
    picked = {deck.pick_next()["word"] for _ in range(20)}
    # everything picked must be unseen (box 0): first word or beyond the slice
    unseen = {w["word"] for w in deck.words} - {w["word"] for w in promoted}
    assert picked <= unseen


def test_mark_unknown_word_raises(deck):
    with pytest.raises(KeyError):
        deck.mark("nonexistentword", True)


def test_mark_logs_today(deck):
    card = deck.pick_next()
    deck.mark(card["word"], True)
    assert deck.stats()["today"] == 1


# ---------------- persistence ----------------

def test_state_round_trip(tmp_path):
    p = tmp_path / "state.json"
    d1 = Deck("cet6", state_path=p, rng=random.Random(1))
    word = d1.words[0]["word"]
    d1.mark(word, True)
    d1.save()
    d2 = Deck("cet6", state_path=p, rng=random.Random(1))
    assert d2.state["boxes"][word]["box"] == 1


def test_corrupt_state_starts_fresh(tmp_path):
    p = tmp_path / "state.json"
    p.write_text("{not json", encoding="utf-8")
    d = Deck("cet6", state_path=p, rng=random.Random(1))
    assert d.state == {"boxes": {}, "log": {}}


def test_reset_clears_state(tmp_path):
    p = tmp_path / "state.json"
    d = Deck("cet6", state_path=p, rng=random.Random(1))
    d.mark(d.words[0]["word"], True)
    d.save()
    d.reset()
    assert not p.exists()
    assert d.stats()["seen"] == 0


# ---------------- stats ----------------

def test_stats_shape(deck):
    s = deck.stats()
    assert set(s) == {"today", "seen", "mastered", "total"}
    assert s["total"] == len(deck.words)
    assert s["today"] == s["seen"] == s["mastered"] == 0


def test_mastered_counts_high_boxes(deck):
    for _ in range(MAX_BOX):
        deck.mark(deck.words[0]["word"], True)
    assert deck.stats()["mastered"] == 1


# ---------------- card formatting ----------------

def test_format_card_contains_all_parts():
    entry = {"word": "abide", "phonetic": "/əˈbaɪd/",
             "meaning": "v. 遵守", "example": "Abide by the rules."}
    card = format_card(entry)
    assert "abide" in card and "/əˈbaɪd/" in card
    assert "v. 遵守" in card and "e.g. Abide by the rules." in card


def test_format_card_omits_missing_example():
    entry = {"word": "x", "phonetic": "", "meaning": "n. 某物", "example": ""}
    card = format_card(entry)
    assert card.splitlines() == ["x", "n. 某物"]


# ---------------- CLI ----------------

def test_parser_defaults():
    args = build_parser().parse_args([])
    assert args.level == "cet4" and args.interval == "30m"


def test_parser_rejects_bad_level():
    with pytest.raises(SystemExit):
        build_parser().parse_args(["--level", "toefl"])


def test_cli_once_prints_a_card(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    rc = main(["--once", "--level", "cet6"])
    out = capsys.readouterr().out
    assert rc == 0 and out.strip()


def test_cli_stats_line(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    rc = main(["--stats", "--level", "cet4"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "cet4" in out and "0" in out


def test_cli_reset(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    assert main(["--once", "--level", "cet4"]) == 0  # creates nothing until marked
    assert main(["--reset", "--level", "cet4"]) == 0
    assert "wiped" in capsys.readouterr().out


def test_cli_bad_interval_exit_code(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    rc = main(["--once", "--interval", "nope"])
    assert rc == 2
    assert "error" in capsys.readouterr().err


def test_run_once_does_not_change_schedule(tmp_path):
    d = Deck("cet6", state_path=tmp_path / "s.json", rng=random.Random(7))
    before = d.stats()["seen"]
    run_once(d)
    assert d.stats()["seen"] == before


def test_run_stats_format(tmp_path):
    d = Deck("cet4", state_path=tmp_path / "s.json", rng=random.Random(7))
    line = run_stats(d)
    assert "cet4" in line and "mastered" in line
