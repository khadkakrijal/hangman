import random
from wonderwords import RandomWord

_rw = RandomWord()

def random_word() -> str:
    """Return a random English word (3-10 letters)."""
    # Keep only alphabetic words to avoid rare unicode/compound surprises
    while True:
        w = _rw.word(word_min_length=3, word_max_length=10)
        if w and w.isalpha():
            return w.lower()

def random_phrase() -> str:
    """Return a phrase of 2-3 random words."""
    n = random.randint(2, 3)
    words = []
    for _ in range(n):
        words.append(random_word())
    return " ".join(words)
