# Decision Intelligence System — Product Requirements Document

**Version:** 1.0
**Owner:** Solo developer (product + engineering)
**Status:** Approved for Phase 1 build
**Last updated:** 21 September 2026

---

## 1. Product Overview

The Decision Intelligence System (DIS) is a single-user command-line application that sits in the loop of everyday micro-decisions ("study, sleep, or play?"), recommends a choice using an explicit scoring model, records what the user *actually* did, and mines that history for behavioral patterns.

The product is not a to-do list and not a chatbot. Its unit of value is the **decision record**: a structured snapshot of the options available at a moment, the system's recommendation with a full explanation, and the user's real choice. Over weeks, those records make a behavior model — where the user reliably follows their own stated priorities, and where they don't.

**Core loop:**

```
INPUT → SCORE → RECOMMEND + EXPLAIN → USER CHOOSES → LOG
   ↑                                                    ↓
   └──────── IMPROVE ← INSIGHTS ← ANALYZE ──────────────┘
```

**What makes it different from asking an LLM:** an LLM gives you a fresh, stateless opinion. DIS gives you a *consistent* opinion (same inputs → same output), a *transparent* one (every point of the score is traceable), and an *accountable* one (it remembers that you said studying was a 9 and then played games anyway, eleven nights in a row).

---

## 2. Problem Statement

A student making 5–15 discretionary decisions a day has three distinct failures, and no tool addresses all three:

1. **Decision paralysis at the moment of choice.** Options are unranked and competing on different axes (importance vs effort vs mood). The user burns energy deciding instead of doing.
2. **No feedback loop.** The user has no record of what they chose, so mistakes never become data. Self-perception ("I'm pretty disciplined") drifts away from behavior with nothing to correct it.
3. **Generic advice.** Productivity apps and AI assistants give universal advice. They don't know that *this* user reliably collapses after 10pm, or specifically avoids anything scored above effort 7.

Existing tools fail because they track **tasks** (Todoist, Notion) or **time** (RescueTime) or give **stateless advice** (ChatGPT). None track *the decision itself* — the counterfactual of what was rejected — which is the only place where behavioral patterns are visible.

---

## 3. Goals and Non-Goals

### 3.1 Goals

| # | Goal | Success signal |
|---|---|---|
| G1 | Produce a ranked, explained recommendation from user-entered options in under 60 seconds of interaction | Median time-to-recommendation < 60s, measured from the tool's own timestamps |
| G2 | Capture the user's actual choice on ≥90% of decisions started | `outcome` field present on ≥90% of decision records |
| G3 | Surface at least 3 non-obvious, statistically gated behavioral insights within 30 days of use | 3+ insights fire with n ≥ their minimum sample size |
| G4 | Be architecturally clean enough to serve as a portfolio artifact | Storage layer swappable JSON → SQLite with zero changes to `core/` |
| G5 | Sustain daily use for 30 consecutive days | ≥1 decision + 1 reflection logged on ≥25 of 30 days |

### 3.2 Non-Goals (explicitly out of scope for v1)

- **Multi-user, accounts, auth, sync.** Single user, single machine, local files.
- **LLM/AI reasoning inside the engine.** The scoring model is deterministic arithmetic. An LLM may later *phrase* insights; it will never *generate* the score. Determinism is the product.
- **Mobile app.** Phase 4 is a local Flask page, not a responsive PWA.
- **Objective outcome measurement.** The system does not integrate with screen-time APIs, calendars, or trackers. All inputs are self-reported. The system measures *decisions*, not *results*.
- **Task management.** No due dates, no subtasks, no projects, no recurrence engine for tasks. Options are ephemeral, decision-time entities.
- **Prescriptive coaching or streaks/gamification.** v1 reports; it does not nag, shame, or reward.

---

## 4. Target User

**Primary persona — "the inconsistent optimizer."** Undergraduate CS/BCA student, comfortable in a terminal, high self-awareness and low follow-through. Owns a laptop that is their primary device. Motivated partly by the project itself (they are also the developer).

**Usage context:** short bursts at 3 fixed points in the day, typed at a terminal that is already open. Friction tolerance is very low — if a decision takes more than a minute to log, it will be skipped, and skipped decisions are the failure mode that kills the whole data set.

---

## 5. Design Principles

1. **Friction is the enemy.** Every feature is judged against keystroke cost. Target: a repeat decision logged in ≤ 15 keystrokes via templates.
2. **The score is always explainable.** No black boxes. Every recommendation renders its arithmetic.
3. **Never assert a pattern you can't defend statistically.** Every insight has a minimum sample size and a labeled confidence. Insights from n=4 are noise and are actively harmful — they teach the user the system is dumb.
4. **Observe, don't moralize.** "You chose the lower-effort option 78% of the time after 10pm" is the voice. "You're being lazy" is not.
5. **Storage is an implementation detail.** Everything goes through a repository interface from day one.

---

## 6. Feature Specification

### F1 — Decision Input System

**Description:** The user starts a decision session, provides session context, then enters 2–6 options with four factors each.

**Session context** (captured once per session, not per option):
- `energy` (1–10) — physical/mental capacity right now
- `mood` (1–10) — affective state
- `available_minutes` (optional int) — time window

> **Design note:** the brief listed mood/energy as a per-option factor. It isn't one — energy is a property of the *user at time T*, identical across all options being compared, so as a per-option input it's redundant data entry that cancels out of the ranking. Instead, energy modulates the effort penalty globally (see F2). This cuts input cost and makes energy actually mean something.

**Per-option factors** (all 1–10 integers, required):
- `importance` — long-term consequence
- `urgency` — time pressure
- `effort` — cost to start and sustain
- `reward` — immediate satisfaction

**Option templates:** the system maintains `templates.json` of previously used options (label + tags + last-used factors). On input, the user can type `t` to pick from the 8 most recent templates and accept or adjust factors. This is the single most important friction feature in the product.

**Acceptance criteria:**
- Rejects sessions with < 2 or > 6 options.
- Rejects out-of-range or non-integer factor values with an inline retry, not a crash.
- Option labels are free text, ≤ 60 chars, with 0–3 tags from a user-extensible tag list (`study`, `rest`, `health`, `social`, `leisure`, `admin`, `career`).
- Partially entered sessions can be abandoned (`Ctrl-C`) without writing a corrupt record.

---

### F2 — Scoring and Recommendation Engine

**Base formula:**

```
raw = (importance × w_imp) + (urgency × w_urg) + (reward × w_rew) − (effort × w_eff_effective)
```

**Energy-modulated effort weight:**

```
w_eff_effective = w_eff × (1 + k × (10 − energy) / 9)
```

Where `k` is `energy_sensitivity` (0.0–1.5). At `energy = 10`, the effort penalty is unchanged; at `energy = 1`, it is amplified by up to `(1 + k)`. This is the mechanism by which "I'm exhausted" legitimately changes the ranking instead of being a rationalization the user applies manually.

**Normalization to a 0–100 display score:**

```
raw_max =  10 × (w_imp + w_urg + w_rew) −  1 × w_eff_effective
raw_min =   1 × (w_imp + w_urg + w_rew) − 10 × w_eff_effective
score   = 100 × (raw − raw_min) / (raw_max − raw_min)
```

Normalization matters because raw scores shift ranges between personality modes, which would make "72 today vs 58 yesterday" meaningless. Scores are rounded to 1 decimal place for display and stored at full precision.

**Ranking:** options sorted descending by score. Ties broken by (1) higher importance, (2) lower effort, (3) input order — deterministic, never random.

**Acceptance criteria:**
- Identical inputs always yield identical output (unit-tested with a fixed fixture set).
- Weights loaded from `config.json`, validated on startup, and never hardcoded in the engine.
- Scoring is a pure function: `score(option, context, policy) -> ScoreBreakdown`, no I/O, no global state.

---

### F3 — Explanation System

Every recommendation renders the per-factor point contribution, sorted by absolute magnitude, plus a comparison against the runner-up.

```
RECOMMENDED: DSA practice  —  score 74.2 / 100   (next best: Watch series, 62.8)

  Why:
    + importance  9  ×0.30  =  +2.70   (strongest driver)
    + urgency     6  ×0.30  =  +1.80
    + reward      8  ×0.20  =  +1.60
    − effort      7  ×0.24  =  −1.68   (effort penalty raised 20% — energy is 6/10)

  Versus "Watch series": you rated it 6 points lower on importance, which
  outweighs its 5-point advantage on effort under Balanced mode.
```

**Acceptance criteria:**
- Explanation is generated from the same `ScoreBreakdown` object used for ranking — it cannot drift from the actual math.
- Explicitly flags when the energy modifier changed the winner (i.e. the ranking would differ at `energy = 10`). This is high-value: it tells the user when their tiredness, not their priorities, made the call.

---

### F4 — Decision Logging

Two-stage write. Stage 1 (`pending`) is written the moment the recommendation is shown, so an abandoned session still counts as a data point. Stage 2 patches in the outcome.

**Captured on outcome:**
- `chosen_option_id`, `followed_recommendation` (derived, not asked)
- `decided_at`, `time_to_decide_seconds`
- `override_reason` — free text, only prompted when the recommendation was *not* followed, and always skippable with Enter
- `satisfaction` (1–5) — prompted at the next session or at reflection, never immediately (immediate self-rating is worthless)

**Acceptance criteria:**
- Writes are atomic: serialize to `decisions.json.tmp`, `fsync`, then `os.replace`. A crash mid-write must never corrupt the log.
- Every record carries `schema_version`.
- Records are append-only; outcome patching is the sole in-place mutation.
- The CLI surfaces any `pending` record older than 2 hours on next launch and offers to close it out.

---

### F5 — Behavioral Analysis Engine

Pure computation over the decision log. No insight text, no thresholds — just statistics, so it can be unit-tested against hand-built fixtures.

| Metric | Definition |
|---|---|
| `adherence_rate` | followed / completed decisions |
| `adherence_by_daypart` | same, bucketed: morning 05–12, afternoon 12–17, evening 17–22, night 22–05 |
| `adherence_by_tag` | same, bucketed by the *recommended* option's tags |
| `effort_delta` | mean(effort of chosen) − mean(effort of recommended), over overrides only |
| `effort_aversion_curve` | adherence rate bucketed by recommended option's effort (1–3, 4–6, 7–8, 9–10) |
| `importance_sacrifice` | mean(importance of recommended − importance of chosen) over overrides |
| `energy_adherence_corr` | Pearson r between session energy and adherence (binary) |
| `decision_velocity` | median `time_to_decide_seconds`, overall and by daypart |
| `conflict_override_rate` | adherence when `conflict = true` vs when false |
| `logging_consistency` | days with ≥1 decision / days since first record |

---

### F6 — Insight Generation

Insights are **declarative rules**, each with a condition, a minimum sample size, and a template. A rule that fails its sample gate is silent — it does not degrade to a hedged version.

| ID | Condition | Min n | Message template |
|---|---|---|---|
| I1 | `adherence_by_daypart["night"] < overall_adherence − 0.20` | 12 night decisions | "After 10pm you follow your own recommendation {x}% of the time, versus {y}% across the day." |
| I2 | `adherence(effort 7–10) < adherence(effort 1–3) − 0.25` | 10 in each bucket | "Effort is your breaking point: you follow through on {x}% of low-effort recommendations but only {y}% when effort is 7+." |
| I3 | `importance_sacrifice > 2.0` | 15 overrides | "When you override, you trade down an average of {d} points of importance." |
| I4 | `adherence_by_tag[t] < overall − 0.20` for any tag t | 10 in that tag | "'{tag}' is where recommendations break down — {x}% followed, versus {y}% overall." |
| I5 | `energy_adherence_corr > 0.4` | 20 decisions | "Your follow-through tracks your energy (r={r}). The lever is sleep, not willpower." |
| I6 | `conflict_override_rate` vs non-conflict gap > 0.2 | 8 conflict decisions | "When two options score close, you pick the lower-effort one {x}% of the time." |
| I7 | `adherence > 0.8` and `logging_consistency > 0.8` | 20 decisions, 14 days | "Follow-through is at {x}% over {n} days. Your weights are calibrated — consider raising your standards rather than your discipline." |

**Confidence labels:** `n < 2×min` → "early signal"; `n ≥ 2×min` → "consistent pattern"; `n ≥ 4×min` → "strong pattern". Displayed inline.

**Acceptance criteria:**
- Rules live in a registry; adding one requires no change to the engine.
- Maximum 3 insights shown at once, ranked by effect size × sample size.
- Empty state is explicit and honest: "Not enough data yet — 14 of the 20 decisions needed for the first pattern check."

---

### F7 — Prompt System

Three scheduled touchpoints, all configurable in `config.json`:

| Slot | Default time | Prompt |
|---|---|---|
| Morning plan | 08:30 | Full decision session for the day's first block. |
| Mid-day check | 14:00 | Close out any pending decision; optional new session. |
| Night reflection | 22:00 | **Mandatory core feature** (see below). |

**Delivery:** Phase 3 uses `cron` (Linux/macOS) or Task Scheduler (Windows) to run `dis prompt --slot=morning`, which fires a desktop notification (`plyer`) and writes a pending prompt marker. Because a laptop may be asleep at the scheduled time, every CLI launch checks for *missed* prompts from the current day and offers them — **catch-up is the real delivery mechanism; the notification is a convenience.**

**End-of-day reflection** (5 fields, target 90 seconds):
1. Auto-shown summary: decisions logged, adherence today, any unclosed pendings.
2. `self_rating` (1–10): how the day went.
3. `note`: free text, skippable.
4. `tomorrow_intent`: one line, seeds tomorrow's morning templates.
5. Retroactive `satisfaction` ratings for today's choices.

Reflection is "mandatory" in the sense that the system treats a missing reflection as a tracked gap — it appears in the consistency metric and is offered on next launch. It is never enforced by blocking other commands.

---

### F8 — Personality Modes

Weight presets, switchable per session (`--mode=hustle`) with a configured default.

| Mode | w_imp | w_urg | w_rew | w_eff | k (energy sensitivity) |
|---|---|---|---|---|---|
| **Balanced** | 0.30 | 0.30 | 0.20 | 0.20 | 0.5 |
| **Hustle** | 0.35 | 0.35 | 0.10 | 0.10 | 0.2 |
| **Recovery** ("lazy") | 0.20 | 0.20 | 0.35 | 0.45 | 1.0 |
| **Custom** | user-defined | | | | |

Mode is stored on every decision record, so analysis can segment by it — and can detect mode-gaming ("you switch to Recovery mode 4× more often at night").

**Acceptance criteria:** weights need not sum to 1; the normalization step handles any positive values. Negative weights are rejected at config load.

---

### F9 — Conflict Detection

If `score(top1) − score(top2) < conflict_threshold` (default **5.0** on the 0–100 scale), the session enters conflict mode instead of asserting a winner:

```
CLOSE CALL — two options are within 3.1 points.

  DSA practice     71.4    stronger on: importance (+3), urgency (+2)
  Gym              68.3    stronger on: effort (−4), reward (+1)

  The tie-breaker isn't in the numbers. Deciding factor to consider:
  DSA is reversible (you can do it tomorrow at the same cost).
  Gym at 9pm is not — the slot closes.

  Pick one — both are defensible.
```

Conflict sessions set `conflict: true` on the record, enabling metric I6. The system deliberately does **not** force a winner here; a 3-point margin on self-reported 1–10 inputs is inside the noise floor, and pretending otherwise would be false precision.

---

### F10 — Future Impact Simulation *(Phase 4, defined now)*

A deliberately simple, clearly-labeled projection. It is **illustrative, not predictive**, and the UI says so.

**Method:**
1. Define `daily_alignment = Σ(importance of chosen) / Σ(importance of recommended)` per day, over the last 30 days.
2. Fit trailing 7-day and 30-day means.
3. Project 30 days forward under three scenarios: current trajectory (trailing-7 mean held flat), +10pp adherence, −10pp adherence.
4. Report the cumulative gap in importance-weighted units and translate to a plain sentence.

```
At your current 54% adherence, over the next 30 days you'd forgo about
81 importance-points of recommended action — roughly 9 study sessions
at your typical ratings.

At 64% adherence: 66 points. At 44%: 96 points.
(Projection assumes today's behavior continues. It is arithmetic, not prophecy.)
```

**Explicitly not doing:** "productivity drops by X%" claims about real-world outcomes. The system has no productivity measurement and must not invent one.

---

## 7. User Flows

### 7.1 Morning decision session (primary flow)

```
$ dis decide

  Energy (1-10): 6
  Mood (1-10):   7
  Minutes available [enter to skip]: 120
  Mode [balanced]: ⏎

  Option 1 — label (or 't' for templates): t
    [1] DSA practice    imp9 urg6 eff7 rew8   (used 14× )
    [2] Sleep           imp7 urg4 eff1 rew9   (used 11×)
    [3] Valorant        imp2 urg1 eff2 rew9   (used 22×)
  > 1
    Use saved factors? [Y/n]: y
  Option 2 — label (or 't'): t → 3
  Option 3 — label (or 't', enter to finish): ⏎

  [recommendation + explanation rendered]

  What did you actually choose? [1] DSA practice  [2] Valorant : 2
  Why the override? [enter to skip]: low energy, wanted a break

  Logged. Adherence this week: 61% (11/18).
```

### 7.2 Night reflection

```
$ dis reflect

  Today: 3 decisions, 2 followed (67%). 1 still open from 14:02.
  → Close it: "Read chapter 4" vs "Nap" — what did you do? nap

  How did today go (1-10)? 6
  Anything worth noting? crashed after lunch again
  One intent for tomorrow? gym before 9am

  Rate how these felt in hindsight (1-5):
    Valorant over DSA practice: 2
    Nap over Read chapter 4:    4

  Saved. Streak: 11 days.
```

### 7.3 Insight review

```
$ dis insights

  CONSISTENT PATTERN (n=31)
  Effort is your breaking point: you follow through on 89% of low-effort
  recommendations but only 34% when effort is 7+.
  → Consider: split high-effort options into a 20-minute starter version.

  EARLY SIGNAL (n=14)
  After 10pm you follow your own recommendation 31% of the time,
  versus 68% across the day.

  Adherence, last 30 days: 58%  (▁▃▅▄▆▇▅ by week)
```

### 7.4 Weight recalibration (the "IMPROVE" step)

Monthly, or on demand via `dis calibrate`. The system reports where stated weights and revealed behavior disagree and offers — never imposes — an adjustment:

```
Over 42 decisions, your choices are better predicted by:
   importance 0.22  urgency 0.28  reward 0.34  effort 0.38
than by your configured Balanced weights.

This is your revealed preference, not your stated one. Two honest readings:
  (a) your real priorities are more reward-driven than you admit — adopt these
  (b) this is exactly the gap you built the system to close — keep current weights

Adopt revealed weights? [y/N]
```

Implementation: grid search over weight vectors maximizing agreement between predicted rank-1 and actual choice. Requires n ≥ 30. This closes the core loop and is the single most interesting feature for portfolio purposes.

---

## 8. Technical Architecture

### 8.1 Stack

- Python 3.11+, standard library first
- `rich` (CLI formatting), `plyer` (notifications, Phase 3), `Flask` + `Chart.js` (Phase 4)
- `pytest` for tests; `dataclasses` for models; `typing.Protocol` for interfaces
- No ORM, no external services, no network calls

### 8.2 Package layout

```
dis/
├── cli/
│   ├── main.py            # argparse dispatch: decide|reflect|insights|calibrate|prompt
│   ├── prompts.py         # input capture + validation, no business logic
│   └── render.py          # rich-based output, explanation rendering
├── core/
│   ├── models.py          # Option, Factors, Context, Decision, Outcome (dataclasses)
│   ├── scoring.py         # ScoringPolicy, score(), normalize() — pure functions
│   ├── engine.py          # DecisionEngine: rank, explain, detect_conflict
│   └── config.py          # load/validate config.json, mode presets
├── storage/
│   ├── repository.py      # DecisionRepository / TemplateRepository Protocols
│   ├── json_store.py      # atomic JSON implementation
│   └── migrations.py      # schema_version upgrades
├── analysis/
│   ├── analyzer.py        # Analyzer: all F5 statistics
│   ├── insights.py        # InsightRule registry, InsightEngine
│   ├── calibrate.py       # revealed-preference weight search
│   └── simulate.py        # Phase 4 projection
├── scheduler/
│   ├── cron_setup.py      # install/remove crontab entries
│   └── catchup.py         # missed-prompt detection
└── web/                   # Phase 4 Flask app
```

**Dependency rule (enforced by review, testable by import inspection):** `core/` imports nothing from `storage/`, `cli/`, or `analysis/`. `analysis/` imports `core/` models only. All I/O lives in `storage/` and `cli/`. This is what makes G4 (portfolio quality) real rather than aspirational.

### 8.3 Key interfaces

```python
@dataclass(frozen=True)
class Factors:
    importance: int; urgency: int; effort: int; reward: int

@dataclass(frozen=True)
class Context:
    energy: int; mood: int; available_minutes: int | None = None

@dataclass
class Option:
    option_id: str; label: str; tags: list[str]; factors: Factors

@dataclass(frozen=True)
class ScoringPolicy:
    w_imp: float; w_urg: float; w_rew: float; w_eff: float
    energy_sensitivity: float; mode_name: str

@dataclass(frozen=True)
class ScoreBreakdown:
    option_id: str; raw: float; score: float
    contributions: dict[str, float]      # factor -> signed points
    effort_weight_applied: float

class DecisionEngine:
    def __init__(self, policy: ScoringPolicy, conflict_threshold: float = 5.0): ...
    def rank(self, options: list[Option], ctx: Context) -> list[ScoreBreakdown]: ...
    def explain(self, ranked: list[ScoreBreakdown]) -> Explanation: ...
    def detect_conflict(self, ranked: list[ScoreBreakdown]) -> bool: ...

class DecisionRepository(Protocol):
    def save_pending(self, d: Decision) -> str: ...
    def patch_outcome(self, decision_id: str, o: Outcome) -> None: ...
    def list(self, since: date | None = None) -> list[Decision]: ...
    def list_pending(self) -> list[Decision]: ...
```

### 8.4 Data flow

```
  CLI input ──► validation ──► Option[] + Context
                                    │
                                    ▼
                         ScoringPolicy (config.json)
                                    │
                                    ▼
                    DecisionEngine.rank() ──► ScoreBreakdown[]
                                    │
                        ┌───────────┴───────────┐
                        ▼                       ▼
                  explain()               detect_conflict()
                        │                       │
                        └───────────┬───────────┘
                                    ▼
                          render to terminal
                                    │
                                    ▼
                    repo.save_pending()  ──► decisions.json
                                    │
                            user chooses
                                    ▼
                    repo.patch_outcome() ──► decisions.json
                                    │
                                    ▼  (on `dis insights`)
                    repo.list() ──► Analyzer ──► Stats
                                                   │
                                                   ▼
                                    InsightEngine(rules) ──► Insight[]
                                                   │
                                                   ▼
                                            render to terminal
                                                   │
                                                   ▼
                                    calibrate ──► suggested weights ──► config.json
```

### 8.5 File layout on disk

`~/.dis/` — `config.json`, `decisions.json`, `templates.json`, `reflections.json`, `backups/decisions-YYYY-MM-DD.json` (daily, keep 14).

---

## 9. Data Models

### 9.1 `decisions.json` — array of records

```json
{
  "schema_version": 1,
  "decision_id": "d_20260921T081403_a4f9",
  "created_at": "2026-09-21T08:14:03+05:30",
  "day_part": "morning",
  "mode": "balanced",
  "status": "closed",
  "context": { "energy": 6, "mood": 7, "available_minutes": 120 },
  "policy_snapshot": {
    "w_imp": 0.30, "w_urg": 0.30, "w_rew": 0.20,
    "w_eff": 0.20, "energy_sensitivity": 0.5
  },
  "options": [
    {
      "option_id": "o1",
      "label": "DSA practice",
      "tags": ["study", "career"],
      "factors": { "importance": 9, "urgency": 6, "effort": 7, "reward": 8 },
      "raw_score": 4.42,
      "score": 74.2,
      "rank": 1
    },
    {
      "option_id": "o2",
      "label": "Valorant",
      "tags": ["leisure"],
      "factors": { "importance": 2, "urgency": 1, "effort": 2, "reward": 9 },
      "raw_score": 2.22,
      "score": 62.8,
      "rank": 2
    }
  ],
  "recommendation": {
    "option_id": "o1",
    "score": 74.2,
    "margin": 11.4,
    "conflict": false,
    "energy_flipped_winner": false,
    "contributions": {
      "importance": 2.70, "urgency": 1.80,
      "reward": 1.60, "effort": -1.68
    }
  },
  "outcome": {
    "chosen_option_id": "o2",
    "followed_recommendation": false,
    "decided_at": "2026-09-21T08:15:41+05:30",
    "time_to_decide_seconds": 98,
    "override_reason": "low energy, wanted a break",
    "satisfaction": 2
  }
}
```

**Note on `policy_snapshot`:** weights are copied onto every record. Without this, changing weights in config retroactively invalidates all historical analysis — a silent, unrecoverable data-integrity bug. This field is not optional.

### 9.2 `config.json`

```json
{
  "schema_version": 1,
  "default_mode": "balanced",
  "conflict_threshold": 5.0,
  "modes": {
    "balanced": { "w_imp": 0.30, "w_urg": 0.30, "w_rew": 0.20, "w_eff": 0.20, "energy_sensitivity": 0.5 },
    "hustle":   { "w_imp": 0.35, "w_urg": 0.35, "w_rew": 0.10, "w_eff": 0.10, "energy_sensitivity": 0.2 },
    "recovery": { "w_imp": 0.20, "w_urg": 0.20, "w_rew": 0.35, "w_eff": 0.45, "energy_sensitivity": 1.0 }
  },
  "schedule": { "morning": "08:30", "midday": "14:00", "reflection": "22:00" },
  "dayparts": { "morning": [5, 12], "afternoon": [12, 17], "evening": [17, 22], "night": [22, 5] },
  "tags": ["study", "rest", "health", "social", "leisure", "admin", "career"],
  "insights": { "max_shown": 3, "enabled_rules": ["I1","I2","I3","I4","I5","I6","I7"] }
}
```

### 9.3 `reflections.json`

```json
{
  "date": "2026-09-21",
  "completed_at": "2026-09-21T22:12:55+05:30",
  "decisions_logged": 3,
  "adherence": 0.67,
  "self_rating": 6,
  "note": "crashed after lunch again",
  "tomorrow_intent": "gym before 9am"
}
```

### 9.4 `templates.json`

```json
{
  "template_id": "t_dsa",
  "label": "DSA practice",
  "tags": ["study", "career"],
  "last_factors": { "importance": 9, "urgency": 6, "effort": 7, "reward": 8 },
  "use_count": 14,
  "last_used": "2026-09-21"
}
```

---

## 10. Milestones

| Phase | Scope | Exit criteria | Est. effort |
|---|---|---|---|
| **P0 — Skeleton** | Repo, package layout, `config.json` loader with validation, pytest harness, CI lint | `pytest` runs green on an empty suite; config loads and rejects bad weights | 1 weekend |
| **P1 — Core CLI** | F1, F2, F3, F4. `dis decide` end to end. Atomic JSON writes. Templates. | 20 real decisions logged by the developer, zero crashes, zero corrupted records | 2 weeks |
| **P2 — OOP hardening** | Repository Protocol + JSON impl, full dataclass models, `policy_snapshot`, migrations module, ≥80% coverage on `core/` and `storage/` | Storage swap to a stub in-memory repo requires no `core/` change; test suite proves it | 1 week |
| **P3 — Analysis** | F5 Analyzer, F6 insight rules, `dis insights`, F8 modes, F9 conflict detection | All 7 rules unit-tested against synthetic fixtures; ≥2 insights fire on real data | 2 weeks |
| **P4 — Prompts & reflection** | F7 scheduling, catch-up detection, `dis reflect`, streak/consistency tracking | 14 consecutive days of reflections logged without manual reminders | 1 week |
| **P5 — Calibration** | `dis calibrate` revealed-preference search | Produces a stable weight vector on n≥30; documented in README | 1 week |
| **P6 — Web (optional)** | Flask read-only dashboard, Chart.js adherence trend + effort-aversion curve, F10 simulation | Dashboard renders from the same repository layer; no duplicated analysis code | 2 weeks |

**Critical ordering constraint:** P1 must ship and be *used daily* before P3 starts. Analysis code written before there is real data to analyze will be built against imagined data and will be wrong. The 2–3 week gap where the tool is "just" a scoring CLI is a feature of the plan, not a delay in it.

---

## 11. Metrics of Success

| Metric | Target (30 days post-P4) | Source |
|---|---|---|
| Days with ≥1 decision logged | ≥25 / 30 | `logging_consistency` |
| Outcome completion rate | ≥90% | records with `status = closed` |
| Median time-to-recommendation | <60s | timestamp delta |
| Median time-to-decide | <90s | `time_to_decide_seconds` |
| Reflections completed | ≥20 / 30 | `reflections.json` |
| Insights fired with n ≥ min | ≥3 distinct rules | insight log |
| Insight usefulness | ≥2 of 3 rated "told me something I didn't know" in a manual self-survey at day 30 | manual |
| Template usage share | ≥60% of options entered via template | input telemetry |

**The leading indicator to watch is outcome completion rate.** If it drops below 80%, the product is failing regardless of every other number — decisions without outcomes are the one data type the system cannot use.

---

## 12. Risks and Tradeoffs

| Risk | Impact | Mitigation |
|---|---|---|
| **Abandonment after 2 weeks** — the single most likely failure | Fatal; no data, no insights | Templates (F1), catch-up prompts (F7), hard friction budget, no feature ships if it adds >10s to the decide flow |
| **Self-reported factors are anchored/gamed** — user rates gaming importance=7 to justify it | Corrupts the entire data set | Log factor ratings per template over time; flag drift ("you've rated Valorant's importance up 3 points over 6 weeks"). Accept as an inherent limit and state it in the README |
| **Insights from tiny samples** | Destroys trust immediately | Hard minimum-n gates, confidence labels, silence over hedging |
| **Scope creep into "AI"** | Kills the deterministic, explainable core that is the actual differentiator | Non-goal §3.2 is binding. Any LLM use is post-v1 and restricted to phrasing existing insights |
| **JSON file corruption / loss** | Total data loss | Atomic write-replace, daily rotating backups, `schema_version` + migrations from day one |
| **Scheduled prompts don't fire (laptop asleep)** | Prompt system silently useless | Catch-up on launch is the primary mechanism; notifications are best-effort |
| **Over-engineering P2 before P1 is used** | Months of architecture, zero data | Milestone ordering constraint in §10 |
| **The system tells the user things they'd rather not hear, and they stop using it** | Silent abandonment | Principle 5 (observe, don't moralize), no streak-shaming, `calibrate` frames revealed preference as a legitimate reading rather than a failure |

### Accepted tradeoffs

- **Linear weighted scoring over anything fancier.** It's explainable, it's debuggable, and with 1–10 self-reported inputs the noise floor swamps any accuracy gain from a more complex model. Explainability is the feature.
- **Local files over a database.** Single user, hundreds of records, zero concurrency. SQLite is one repository implementation away if the log exceeds ~5,000 records.
- **CLI over GUI.** Terminal is lower friction for the target user and keeps 100% of effort on the engine, which is where the portfolio value sits.
- **No objective outcome measurement.** Integrating screen-time or calendar data would make insights far stronger, and would also triple the scope and add platform-specific fragility. v1 measures decisions, and says so plainly.

---

## 13. Open Questions

1. Should overridden recommendations that turn out *well* (satisfaction 5) be treated as engine errors and fed into calibration? Leaning yes — that's the honest reading — but it needs n ≥ 40 before it's worth implementing.
2. Is `satisfaction` at reflection time reliable, or does end-of-day mood contaminate it? Test by comparing same-day vs next-day ratings on a 20-decision sample.
3. Should the engine ever refuse to recommend (e.g. energy ≤ 2, all options effort ≥ 7) and suggest rest instead? Risk: becomes a moralizing feature. Defer to post-P5.
4. Do dayparts need to be personalized (a 2am-sleeper's "night" is not 22:00)? Likely yes; make them config-driven now (already done in §9.2) and revisit after 30 days of data.
