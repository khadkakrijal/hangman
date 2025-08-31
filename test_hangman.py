# test_hangman.py
import unittest
from hangman_engine import HangmanEngine, MASK_CHAR

class TestHangmanEngine(unittest.TestCase):
    def test_mask_and_win(self):
        eng = HangmanEngine("abc", lives=3)
        self.assertEqual(eng.masked, MASK_CHAR * 3)
        self.assertTrue(eng.guess('a'))
        self.assertTrue(eng.guess('b'))
        self.assertTrue(eng.guess('c'))
        self.assertTrue(eng.is_won())
        self.assertFalse(eng.is_lost())

    def test_wrong_guess_costs_life(self):
        eng = HangmanEngine("test", lives=2)
        self.assertFalse(eng.guess('x'))
        self.assertEqual(eng.lives, 1)
        self.assertFalse(eng.guess('y'))
        self.assertEqual(eng.lives, 0)
        self.assertTrue(eng.is_lost())

    def test_repeat_no_penalty(self):
        eng = HangmanEngine("banana", lives=3)
        self.assertTrue(eng.guess('a'))
        before = eng.lives
        self.assertTrue(eng.guess('a'))  # repeat
        self.assertEqual(eng.lives, before)

    def test_spaces_and_punct(self):
        eng = HangmanEngine("a-b a", lives=3)
        self.assertEqual(eng.masked, f"{MASK_CHAR}-{MASK_CHAR} {MASK_CHAR}")
        self.assertFalse(eng.guess('1'))  # ignored
        self.assertEqual(eng.lives, 3)
        eng.guess('a')
        self.assertIn('a', eng.masked)

    def test_timeout_penalty(self):
        eng = HangmanEngine("hi", lives=2)
        eng.timeout_penalty()
        self.assertEqual(eng.lives, 1)
        self.assertEqual(eng.timeouts, 1)

    def test_invalid_answer_raises(self):
        with self.assertRaises(ValueError):
            HangmanEngine("")
        with self.assertRaises(ValueError):
            HangmanEngine("   ")

    def test_hint_reveals_letter_and_costs_life(self):
        eng = HangmanEngine("test", lives=3)
        before = eng.lives
        revealed = eng.reveal_hint_letter()
        self.assertIsNotNone(revealed)
        self.assertIn(revealed, set("test"))
        self.assertEqual(eng.lives, before - 1)
        # Reveal remaining distinct letters (t, e, s)
        seen = {revealed}
        while True:
            r = eng.reveal_hint_letter()
            if r is None:
                break
            seen.add(r)
            if seen >= set("tes"):
                break
        # After all distinct letters are revealed, further hint should do nothing
        before2 = eng.lives
        r2 = eng.reveal_hint_letter()
        self.assertIsNone(r2)
        self.assertEqual(eng.lives, before2)

if __name__ == "__main__":
    unittest.main()
