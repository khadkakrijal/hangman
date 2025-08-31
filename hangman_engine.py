# hangman_engine.py
# Pure game logic (easy to unit test). Includes a hint method that reveals one letter.

import random
from dataclasses import dataclass, field
from typing import List, Set

MASK_CHAR = "_"

@dataclass
class HangmanEngine:
    answer: str
    lives: int = 6
    guessed: Set[str] = field(default_factory=set)
    timeouts: int = 0  # track count of timeouts

    def __post_init__(self):
        if not isinstance(self.answer, str) or not self.answer.strip():
            raise ValueError("Answer must be a non-empty string.")
        self.answer = self.answer.lower()

    @property
    def masked(self) -> str:
        out: List[str] = []
        for ch in self.answer:
            if ch == " ":
                out.append(" ")
            elif ch.isalpha():
                out.append(ch if ch in self.guessed else MASK_CHAR)
            else:
                out.append(ch)  # reveal punctuation by default
        return "".join(out)

    def is_won(self) -> bool:
        return all((not ch.isalpha()) or (ch in self.guessed) for ch in self.answer)

    def is_lost(self) -> bool:
        return self.lives <= 0 and not self.is_won()

    def guess(self, ch: str) -> bool:
        if self.is_won() or self.is_lost():
            return False
        if not ch or len(ch) != 1:
            return False
        ch = ch.lower()
        if not ch.isalpha():
            return False  # ignore non-letters; no penalty
        if ch in self.guessed:
            return ch in self.answer  # no penalty on repeat
        self.guessed.add(ch)
        if ch in self.answer:
            return True
        self.lives -= 1
        return False

    def timeout_penalty(self):
        if self.is_won() or self.is_lost():
            return
        self.timeouts += 1
        self.lives -= 1

    # --- Hint: reveal one random unrevealed letter (-1 life) ---
    def reveal_hint_letter(self) -> str | None:
        """
        Reveal one random unrevealed letter from the answer.
        Costs 1 life only if a new letter is actually revealed.
        Returns the revealed letter, or None if nothing to reveal.
        """
        if self.is_won() or self.is_lost():
            return None
        remaining = sorted({ch for ch in self.answer if ch.isalpha()} - self.guessed)
        if not remaining:
            return None
        letter = random.choice(remaining)
        self.guessed.add(letter)
        self.lives -= 1
        return letter
