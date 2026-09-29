# CONTRACT.md

This file is the agreement between the two of us about how our code fits together. Neither of us changes a function listed here without telling the other first — that's the entire point of it existing.

If you're implementing something and the real code ends up needing a different shape than what's written here, **stop and message the other person before you change it.** Update this file in the same commit as the code change, so it's never out of date.

---

## Shared data shapes

Both of us build around these. Get these right and the two halves click together automatically.

### A `factors` dict — describes one option's numbers
```python
{
    "importance": 9,   # int, 1-10
    "effort": 7        # int, 1-10
}
```

### An `option` dict — one thing being considered
```python
{
    "label": "Study for DSA test",   # str
    "factors": {"importance": 9, "effort": 7}
}
```

### A `scored_option` dict — an option after scoring (Person A adds these fields)
```python
{
    "label": "Study for DSA test",
    "factors": {"importance": 9, "effort": 7},
    "score": 11.0,
    "breakdown": {"importance_points": 18, "effort_points": -7}
}
```

### A `decision` dict — one full saved record
```python
{
    "options": [ <option dict>, <option dict>, ... ],
    "recommended_label": "Study for DSA test",
    "chosen_label": "Sleep",
    "timestamp": "2026-09-29T21:14:03"
}
```

---

## Person A owns: `scoring.py` — the thinking logic

No `input()`, no `print()`, no file reading/writing in this file. Pure functions only — numbers and dicts go in, numbers and dicts come out. That's what lets these get tested on their own and reused later without dragging the whole CLI along.

```python
def score_option(factors: dict) -> tuple[float, dict]:
    """
    Takes one option's factors dict.
    Returns (total_score, breakdown) where breakdown shows each
    factor's point contribution, e.g. {"importance_points": 18, "effort_points": -7}
    """

def pick_winner(options: list) -> dict:
    """
    Takes a list of option dicts (each with "label" and "factors").
    Scores every one using score_option, and returns the single
    winning option as a scored_option dict (see shape above) —
    original fields kept, plus "score" and "breakdown" added.
    """
```

---

## Person B owns: `storage.py` and `io_helpers.py` — talking to the user and the disk

```python
def ask_for_number(question: str) -> int:
    """
    Prints `question`, keeps re-asking until the user enters a
    valid whole number, then returns it. Never crashes on bad input.
    """

def collect_options() -> list:
    """
    Asks the user how many options, then asks for a label and
    factors for each one. Returns a list of option dicts, in
    exactly the shape score_option/pick_winner expect — see
    "Shared data shapes" above.
    """

def load_decisions() -> list:
    """
    Reads decisions.json and returns the list of saved decision
    dicts. Returns [] if the file doesn't exist yet — never crashes.
    """

def save_decisions(decisions: list) -> None:
    """
    Takes the full list of decision dicts and writes it to
    decisions.json, overwriting the old file. Caller is
    responsible for adding the new decision to the list first.
    """

def adherence_rate(decisions: list) -> float | None:
    """
    Takes the loaded list of decision dicts. Returns the percentage
    (0-100) where recommended_label == chosen_label.
    Returns None if the list is empty — caller must handle that
    case rather than assuming a number comes back.
    """
```

---

## Together: `main.py` — the only file that imports from both sides

This is where `collect_options()` (Person B) feeds into `pick_winner()` (Person A), the result gets shown to the user, and the outcome gets saved with `save_decisions()` (Person B). Neither of you owns this file alone — changes to it happen on a call or get reviewed by both before merging.

---

## How to propose a change to this contract

1. Message the other person: "I want to change `<function>` from `<old shape>` to `<new shape>`, because `<reason>`."
2. Agree before either of you touches the code.
3. Update this file and the code in the same commit, with a clear message like `"contract: change pick_winner to also return the runner-up"`.
4. Whoever doesn't own that function re-reads their own code afterward to check nothing broke.

---

## Change log

| Date | Change | Who |
|---|---|---|
| _fill in as you go_ | initial contract agreed | both |
