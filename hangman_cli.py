# hangman_cli.py
# Console UI with a 15s timer. Supports: letter guesses, 'h' for hint, 'q' to quit.

import platform
import sys
import time
from typing import Optional

from hangman_engine import HangmanEngine
from words_loader import random_word, random_phrase

TIME_LIMIT = 15  # seconds

def choose_level() -> str:
    while True:
        print("Choose level: [1] Basic (single word)  [2] Intermediate (phrase)")
        choice = input("> ").strip()
        if choice in {"1","2"}:
            return choice
        print("Invalid choice. Enter 1 or 2.\n")

def choose_answer(level: str) -> str:
    return random_word() if level == "1" else random_phrase()

def timed_input(prompt: str, timeout: int) -> Optional[str]:
    """Windows: msvcrt keystroke loop with visible countdown.
       macOS/Linux: select() with timeout.
       Returns input string or None on timeout.
    """
    system = platform.system()
    print(prompt, end="", flush=True)
    if system == "Windows":
        import msvcrt
        buf = []
        start = time.time()
        shown = None
        while True:
            remaining = max(0, int(timeout - (time.time() - start)))
            if remaining != shown:
                print(f"\r{prompt}{''.join(buf)}  (⏳ {remaining}s) ", end="", flush=True)
                shown = remaining
            if msvcrt.kbhit():
                ch = msvcrt.getwch()
                if ch in ("\r", "\n"):
                    print()
                    return "".join(buf)
                elif ch == "\b":
                    if buf:
                        buf.pop()
                else:
                    buf.append(ch)
            if time.time() - start >= timeout:
                print()
                return None
            time.sleep(0.02)
    else:
        import select
        start = time.time()
        print(f"(⏳ {timeout}s) ", end="", flush=True)
        while True:
            remaining = timeout - (time.time() - start)
            if remaining <= 0:
                print()
                return None
            r, _, _ = select.select([sys.stdin], [], [], remaining)
            if r:
                return sys.stdin.readline().rstrip("\n")

def render(engine: HangmanEngine):
    print("\n" + "-"*48)
    print(f"Word: {engine.masked.replace(' ', '  ')}")
    guessed = ', '.join(sorted(engine.guessed)) or '-'
    print(f"Lives: {engine.lives}   Guessed: {guessed}   Timeouts: {engine.timeouts}")
    print("Type a letter, 'h' for hint (-1 life), 'q' to quit.")
    print("-"*48)

def info_hint(answer: str) -> str:
    letters = [ch for ch in answer if ch.isalpha()]
    length = len(letters)
    vowels = sum(ch in "aeiou" for ch in letters)
    words = len([p for p in answer.split(" ") if p != ""])
    # Non-revealing meta-hint
    return f"[Hint info] letters: {length}, vowels: {vowels}, words: {words}"

def main():
    print("=== Hangman (Random Generator + Hints) ===")
    level = choose_level()
    answer = choose_answer(level)
    engine = HangmanEngine(answer=answer, lives=6)
    print(info_hint(engine.answer))  # free non-revealing meta hint

    while not engine.is_won() and not engine.is_lost():
        render(engine)
        user = timed_input(f"Guess a letter within {TIME_LIMIT}s (h/q): ", TIME_LIMIT)
        if user is None or user.strip() == "":
            print("⏰ Time's up! -1 life.")
            engine.timeout_penalty()
            continue
        user = user.strip().lower()
        if user in {"q", "quit"}:
            print("You quit the game.")
            break
        if user in {"h", "hint"}:
            letter = engine.reveal_hint_letter()
            if letter is None:
                print("ℹ️ No hint available—all letters already revealed.")
            else:
                print(f"💡 Hint used: revealed '{letter}'. (-1 life)")
            continue

        guess = user[0]
        ok = engine.guess(guess)
        if ok:
            print(f"✅ '{guess}' is in the answer.")
        else:
            if guess.isalpha():
                print(f"❌ '{guess}' not in answer. -1 life.")
            else:
                print(f"⚠️ Non-letter ignored.")

    render(engine)
    if engine.is_won():
        print(f"🎉 You won! Answer: '{engine.answer}'.")
    elif engine.is_lost():
        print(f"💀 Game over. Answer: '{engine.answer}'.")
    else:
        print(f"👋 Goodbye! Answer was: '{engine.answer}'.")

if __name__ == "__main__":
    main()
