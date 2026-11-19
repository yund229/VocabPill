# VocabPill 💊

**English** | [中文](README_EN.md)

**A word a pill keeps forgetting away: desktop pop-up flashcards for CET-4 / CET-6.** Zero dependencies, fully offline, 1,150+ built-in words.

[![CI](https://github.com/yund229/VocabPill/actions/workflows/ci.yml/badge.svg)](https://github.com/yund229/VocabPill/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Dependencies](https://img.shields.io/badge/dependencies-0-brightgreen)

![demo](https://cdn.jsdelivr.net/gh/yund229/VocabPill@main/assets/demo.gif)

## Why

Vocabulary apps want your attention, your account, and your streak anxiety. VocabPill just quietly pops a card every N minutes while you study or work — word → phonetic → meaning → example, one tap on 认识 / 不认识, and the card goes away. Spaced repetition does the rest.

## Install

```bash
pip install git+https://github.com/yund229/VocabPill.git
```

Windows without Python: grab `vocabpill.exe` from [Releases](https://github.com/yund229/VocabPill/releases).

## Quick start

```bash
vocabpill --level cet4 --interval 30m   # pop a CET-4 card every 30 minutes
vocabpill --level cet6 --interval 1h    # CET-6, hourly
vocabpill --once --level cet4           # print one card in the terminal
vocabpill --stats --level cet4          # today 12 words | seen 58/790 | mastered 9
vocabpill --reset --level cet4          # wipe progress
```

## How the scheduling works

- **Leitner boxes 0–5** — every word starts in box 0; 认识 promotes it, 不认识 resets it to 0
- **Lowest box first** — the popper always draws from the least-mastered group, so new and forgotten words come back sooner
- **Progress persists** — state lives in `~/.vocabpill/state_<level>.json`; no account, no cloud
- **Peeking is free** — `--once` prints a card without touching the schedule

## Built-in word banks

| Bank | Words | Content |
|------|-------|---------|
| `cet4` | 790 | word / IPA / meaning / example sentence |
| `cet6` | 366 | same format, deduplicated against CET-4 |

Both ship as plain JSON in `vocabpill/data/` — edit or replace them freely.

## Design notes

- **Zero dependencies** — the GUI is tkinter, which ships with Python; nothing to install
- **42 tests, no mocks** — the scheduler, persistence, and CLI are exercised against real temp files
- **Headless-friendly** — `--once` / `--stats` / `--reset` never import tkinter, so they work over SSH

## Comparison

| | VocabPill | Vocabulary apps | Anki |
|---|-----------|-----------------|------|
| Offline | ✅ | mostly ❌ | ✅ |
| Setup | none | account + import | decks + import |
| Popup interrupts | ✅ | ❌ | ❌ |
| Dependencies | 0 | app | heavy |

## More tools from me

- [DeskPet](https://github.com/yund229/DeskPet) — Java desktop pet
- [SnapOCR](https://github.com/yund229/SnapOCR) — hotkey screenshot → offline OCR text
- [DirTidy](https://github.com/yund229/DirTidy) — auto-organize your Downloads folder, with undo
- [RectGif](https://github.com/yund229/RectGif) — drag a rectangle on screen, get an animated GIF
- [PdfLoft](https://github.com/yund229/PdfLoft) — every PDF chore in one CLI

## License

MIT
