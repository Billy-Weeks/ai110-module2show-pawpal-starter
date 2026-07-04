# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
Today's Schedule for Sally Weeks:
----------------------------------------
  07:00  Dino            Breakfast
  07:30  Butterscotch    Breakfast
  08:00  Kiwi            Refill seeds
  09:00  Butterscotch    Morning walk
  12:00  Dino            Litter box
  13:00  Kiwi            Clean cage
  17:00  Dino            Play with feather toy
  18:00  Butterscotch    Evening walk
  19:30  Kiwi            Cover cage for night
  ```



## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `sort_by_time()`<br>`build_daily_schedule()` | `sort_by_time()` orders tasks by time. Scheduling places tasks in precedence order (non-skippable, then priority, then time) regardless of insertion order. |
| Filtering | `filter_tasks(completed=..., pet_name=...)` | Filter by completion status and/or pet name (combine with AND). Non-mutating. |
| Conflict handling | `find_conflicts()`<br>`add_task()`<br>`_earliest_free_slot()`<br>`Scheduler.conflicts` | `find_conflicts()` detects overlapping time slots across all pets (also used by the UI to warn at add time). During a build, the lower-priority task is nudged to the next free slot via a greedy sweep, or dropped if `skippable`. Tradeoff: priority over punctuality. |
| Recurring tasks | `Task.mark_complete()`<br>`Task.spawn_next_occurrence()` | `recurrence` of `daily`/`weekly` auto-creates the next occurrence on completion. Separate from `frequency` (repeats within one day). |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
