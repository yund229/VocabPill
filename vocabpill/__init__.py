"""VocabPill — desktop flashcard pop-ups for CET-4 / CET-6 words."""

__version__ = "1.0.0"

from vocabpill.core import Deck, format_card, load_bank, parse_interval

__all__ = ["Deck", "load_bank", "parse_interval", "format_card", "__version__"]
