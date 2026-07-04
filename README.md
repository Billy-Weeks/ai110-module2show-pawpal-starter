# PawPal+

## 📝 Description of App
**PawPal+** is a pet-care planning assistant. An owner registers one or more pets, gives each pet care tasks (feeding, walks, medicine, cage cleaning, play time, etc.,) and the app builds a **conflict-free daily schedule** across *all* of the owner's pets on a single timeline.
The core idea: the day is treated as **the owner's own single timeline**. One person can only do one thing at a time so two tasks conflict even if they belong to *different* pets. The scheduler decides who keeps a slot, who gets nudged to a later time, and who gets dropped, all based on priority and whether a task is skippable.

App may be run one of two ways:
```bash
# An interactive Streamlit web UI
streamlit run app.py
```
OR
```bash
# a scripted console demo showing the same backend from start to finish in the CLI
 python main.py
```
## 📸 Demo Walkthrough

### Features: Scheduler
* **Sorting by time:** Any task list can be ordered chronologically by scheduled time, independent of the order tasks were entered.
* **Priority-based placement:** Tasks are placed and conflicts are addressed based on Priority and whether the task may be skipped for the day.
* **Interval-overlap conflict detection:** Conflicts are detected by comparing full time intervals (start time + duration), not just identical start times, so partial overlaps are caught.
* **Conflict warnings:** Every overlap the scheduler resolves is reported in plain language (e.g., *"'Morning walk' @ 08:00 overlaps 'Breakfast' @ 08:00 → moved to 08:20"*).
* **Displacement/nudging:** A non-skippable task that loses its slot is slid forward to the earliest free gap after its requested time.
* **Skippable drops:** A task marked *skippable* is dropped for the day (not nudged) when it conflicts. The drop is recorded, not silently lost.
* **End-of-day cutoff:** Nothing is scheduled past the owner's end-of-day time; anything that can't fit before it is reported as "unplaced."
* **Free-time suggestions:** When a new task clashes, the app suggests the earliest conflict-free start time.
* **Frequency expansion:** A task set to happen N times/day is expanded into N occurrences spread evenly from its start time to end-of-day.
* **Daily/weekly recurrence:** Completing a recurring task automatically spawns the next occurrence on the next day/week.

***
### Features: Main UI Features and User Actions

A user can:

* **Edit the owner profile:** Set first name, last name, and the end-of-day cutoff (the hard limit past which nothing is scheduled).
* **Add pets:** Enter name, species, breed, age, diet, and energy level; a running list of current pets is displayed.
* **Add tasks to a pet:** Choose the pet, then set: title, time, duration (minutes), times-per-day (frequency), priority (low/medium/high), repeats (none/daily/weekly), and a skippable checkbox.
* **Get conflict handling at add-time:**
  * No clash → task is added immediately.
  * Skippable clash → task is added but flagged that it will be skipped on conflicting days.
  * Non-skippable clash with a skippable task → task is added and the skippable one is flagged for skipping.
  * Non-skippable clash with another non-skippable task → the app **holds the task** and offers a **suggested free time** with **Use/Cancel** buttons (or a Dismiss option if no slot exists before end of day).
* **View all tasks in a table:** (Pet, Task, Time, Duration, Times/day, Priority, Repeats, Skippable, Done), with **filters** by pet and by status (all / pending / completed) and automatic chronological sorting.
* **Generate the daily schedule:** Runs the scheduler across all pets and shows the resolved timeline, plus separate call-outs for **conflicts resolved, skipped tasks,** and **tasks that couldn't fit.**

### Example Workflow

1. Launch the app: `streamlit run app.py `
2. In **Owner profile** set the name and set end-of-day (*default is 20:00*)
3. In **Add a pet**, add one or more pets. "Current pets" list will update as you add.
4. In **Add a task** add the various tasks you'd like to keep track of throughout your day/week.
5. Use the **Filter by pet** or **Filter by status** dropdowns to either see *just* one pet's info or to see certain *status*.
6. Click **Generate schedule** to see what your day/week will look like


### 🖥️ Sample CLI Output


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


Out-of-order demo for Sally:
========================================

As entered (insertion order):
  19:30  Bedtime snack
  07:00  Breakfast
  15:00  Afternoon play
  06:00  Sunrise medicine
  12:00  Lunch

After Scheduler.sort_by_time():
  06:00  Sunrise medicine
  07:00  Breakfast
  12:00  Lunch
  15:00  Afternoon play
  19:30  Bedtime snack
[conflict] 'Breakfast' @ 07:00 overlaps 'Breakfast' @ 07:00 -> moved to 07:10
[conflict] 'Lunch' @ 12:00 overlaps 'Litter box' @ 12:00 -> moved to 12:15
[conflict] 'Bedtime snack' @ 19:30 overlaps 'Cover cage for night' @ 19:30 -> moved to 19:35

Rebuilt daily schedule (Gizmo's tasks in place):
----------------------------------------
  06:00  Sunrise medicine
  07:10  Breakfast
  12:15  Lunch
  15:00  Afternoon play
  19:35  Bedtime snack


Same-time conflict demo:
========================================

Both tasks requested for 08:00:
  08:00  Breakfast (high)
  08:00  Morning walk (low)

Building schedule (watch the [conflict] warning):
[conflict] 'Morning walk' @ 08:00 overlaps 'Breakfast' @ 08:00 -> moved to 08:20

Resolved schedule:
----------------------------------------
  08:00  Breakfast (high)
  08:20  Morning walk (low)

Conflicts reported:
  - 'Morning walk' @ 08:00 overlaps 'Breakfast' @ 08:00 -> moved to 08:20
```

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 🧪 Testing PawPal+

### Description of tests:
Tests are designed to test several functions to ensure the "Happy Path" as well as for edge cases are still handled correctly. Specifically they cover: completion (tasks that are completed are marked as so), task-to-pet linkage (tasks added to a pet increase the task list links accordingly), sorting (task sorting handled accordingly), recurrence (after recurring tasks completes, the next occurrence is automatically added to the schedule), conflict detection and the empty-owner (Owner but no pet attached yet) edge case.

```bash
# Run the full test suite:
python -m pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
===================================================================== test session starts ======================================================================
platform linux -- Python 3.12.3, pytest-9.1.1, pluggy-1.6.0
rootdir: /mnt/c/CodePath-AI/ai110-module2show-pawpal-starter
plugins: anyio-4.14.1
collected 11 items                                                                                                                                             

tests/test_pawpal.py ...........                                                                                                                         [100%]

====================================================================== 11 passed in 0.46s ======================================================================
```

### Confidence level (1 - 5 stars)
🌟🌟🌟🌟🌟 

Edge cases and features implemented are tested for and all tests pass. 5 stars!

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `sort_by_time()`<br>`build_daily_schedule()` | `sort_by_time()` orders tasks by time. Scheduling places tasks in precedence order (non-skippable, then priority, then time) regardless of insertion order. |
| Filtering | `filter_tasks(completed=..., pet_name=...)` | Filter by completion status and/or pet name (combine with AND). Non-mutating. |
| Conflict handling | `find_conflicts()`<br>`add_task()`<br>`_earliest_free_slot()`<br>`Scheduler.conflicts` | `find_conflicts()` detects overlapping time slots across all pets (also used by the UI to warn at add time). During a build, the lower-priority task is nudged to the next free slot via a greedy sweep, or dropped if `skippable`. Tradeoff: priority over punctuality. |
| Recurring tasks | `Task.mark_complete()`<br>`Task.spawn_next_occurrence()` | `recurrence` of `daily`/`weekly` auto-creates the next occurrence on completion. Separate from `frequency` (repeats within one day). |


**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
