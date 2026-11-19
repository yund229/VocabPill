"""Tkinter pop-up flashcard: a small always-on-top card that appears on a
timer, remembers your answers in the Leitner deck, and quietly disappears.

The window shows the word first; phonetic / meaning / example are revealed
by a button so you get a moment of active recall. 认识 / 不认识 schedule
the next appearance.
"""

from __future__ import annotations

import tkinter as tk

from vocabpill.core import Deck


class CardPopup:
    def __init__(self, deck: Deck, interval: int):
        self.deck = deck
        self.interval = interval * 1000  # seconds -> ms
        self.card = None
        self.root = tk.Tk()
        self.root.title("VocabPill")
        self.root.attributes("-topmost", True)
        self.root.geometry("+60+60")
        self.root.resizable(False, False)
        self._build()

    def _build(self):
        self.var_word = tk.StringVar()
        self.var_phon = tk.StringVar()
        self.var_mean = tk.StringVar()
        self.var_ex = tk.StringVar()
        f = ("Microsoft YaHei UI", 11)

        tk.Label(self.root, textvariable=self.var_word,
                 font=("Microsoft YaHei UI", 22, "bold"),
                 fg="#2b6cb0").pack(padx=24, pady=(18, 2))
        tk.Label(self.root, textvariable=self.var_phon, font=f,
                 fg="#718096").pack()
        tk.Label(self.root, textvariable=self.var_mean, font=f,
                 wraplength=300, justify="left").pack(padx=24, pady=(6, 0))
        tk.Label(self.root, textvariable=self.var_ex, font=f,
                 fg="#4a5568", wraplength=300, justify="left").pack(padx=24,
                                                                    pady=(4, 8))

        self.btn_show = tk.Button(self.root, text="显示答案", font=f,
                                  command=self._reveal)
        self.btn_show.pack(pady=(0, 8))
        self.frame_ans = tk.Frame(self.root)
        tk.Button(self.frame_ans, text="认识 ✔", font=f, width=10,
                  fg="#276749", command=lambda: self._answer(True)
                  ).pack(side="left", padx=8)
        tk.Button(self.frame_ans, text="不认识 ✘", font=f, width=10,
                  fg="#9b2c2c", command=lambda: self._answer(False)
                  ).pack(side="left", padx=8)
        self.root.protocol("WM_DELETE_WINDOW", self._quit)

    def _show(self):
        self.card = self.deck.pick_next()
        self.var_word.set(self.card["word"])
        self.var_phon.set(self.card.get("phonetic", ""))
        self.var_mean.set("")
        self.var_ex.set("")
        self.btn_show.pack()
        self.frame_ans.pack_forget()
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()

    def _reveal(self):
        self.var_mean.set(self.card["meaning"])
        self.var_ex.set(f"e.g. {self.card.get('example', '')}")
        self.btn_show.pack_forget()
        self.frame_ans.pack(pady=(0, 14))

    def _answer(self, known: bool):
        self.deck.mark(self.card["word"], known)
        self.deck.save()
        self.root.withdraw()
        self.root.after(self.interval, self._show)

    def _quit(self):
        self.root.destroy()

    def run(self):
        self.root.after(300, self._show)  # first card almost immediately
        self.root.mainloop()


def run_popup(deck: Deck, interval: int) -> None:
    CardPopup(deck, interval).run()
