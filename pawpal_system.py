"""PawPal+ system.

Class structure generated from the UML design in diagrams/uml_draft.mmd.

Design notes / resolved issues:
  * A Task carries a frequency (times per day); the Scheduler expands each
    task into that many concrete occurrences spread across the day, so the
    frequency field drives the schedule instead of contradicting the single
    scheduled_time.
  * Pet owns its Tasks (add/list/manage); Task.pet_assigned is set on add,
    so a Task can never reference a pet the owner does not have.
  * Scheduler manages tasks across ALL of an owner's pets, treating the
    schedule as the owner's single timeline (one person, one thing at a time).
  * Conflicts are detected by time-interval OVERLAP (using duration), not just
    exact start time.
  * Placed tasks are kept in a single start-time-sorted list, so conflict
    detection and finding a task's next free slot are each a single ordered
    pass (helped by bisect) instead of rescanning the whole schedule.
  * A displaced task is moved to the earliest free gap after the winner in one
    sweep (bounded by the owner's cutoff), instead of hopping past one task at
    a time and re-checking.
  * Dropped/unplaced tasks are logged (surfaced) instead of silently lost.
"""

from __future__ import annotations

import bisect
from dataclasses import dataclass, field, replace
from datetime import date, datetime, time, timedelta
from typing import Optional

# Reference date used only for time arithmetic (add_task never needs "today").
_REF_DATE = datetime.min.date()

# Higher number = higher priority. Unknown labels rank lowest (0).
PRIORITY_RANK = {"high": 3, "medium": 2, "low": 1}

# Recurrence intervals: completing one of these spawns the next occurrence.
# Anything not listed here (e.g. "none") is treated as non-recurring.
RECURRENCE_STEP = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}


def _as_dt(t: time) -> datetime:
    """Combine a time with the reference date so we can do arithmetic on it."""
    return datetime.combine(_REF_DATE, t)


@dataclass
class Task:
    """A single scheduled activity for a pet (feeding, walk, medicine, ...)."""

    description: str
    scheduled_time: time            # due time (of the first occurrence)
    duration: int = 0               # minutes
    frequency: int = 1              # times per day (Scheduler expands into occurrences)
    skippable: bool = False         # True if it can be dropped for the day (a walk)
    priority: str = "medium"        # high / medium / low
    recurrence: str = "none"        # none / daily / weekly (regenerates on completion)
    due_date: Optional[date] = None  # calendar day this occurrence is for (None = undated)
    completed: bool = False         # completion status
    pet_assigned: Optional["Pet"] = None  # set by Pet.add_task

    def mark_complete(self) -> Optional["Task"]:
        """Mark this task done.

        If it recurs (daily/weekly), spawn and return the next occurrence
        (attached to the same pet); otherwise return None. Note ``frequency``
        (times per day) and ``recurrence`` (which day it repeats on) are
        independent: frequency drives same-day occurrences, recurrence rolls the
        task forward to a future day.
        """
        self.completed = True
        return self.spawn_next_occurrence()

    def spawn_next_occurrence(self) -> Optional["Task"]:
        """Create the next occurrence of a recurring task, advancing its due
        date by one interval. Returns None for non-recurring tasks.

        The copy starts uncompleted and, if this task belongs to a pet, is added
        back to that pet automatically. An undated task anchors off today.
        """
        step = RECURRENCE_STEP.get(self.recurrence)
        if step is None:
            return None
        base = self.due_date if self.due_date is not None else date.today()
        nxt = replace(self, completed=False, due_date=base + step, pet_assigned=None)
        if self.pet_assigned is not None:
            self.pet_assigned.add_task(nxt)
        return nxt

    def change_description(self, description: str) -> None:
        """Rename the task."""
        self.description = description

    def update_duration(self, duration: int) -> None:
        """Change how long the task takes, in minutes."""
        self.duration = duration

    @property
    def rank(self) -> int:
        """Numeric priority (higher = more important); unknown labels -> 0."""
        return PRIORITY_RANK.get(self.priority, 0)


@dataclass
class Pet:
    """A single pet: identifying info plus its own collection of tasks."""

    name: str
    pet_type: str                   # cat / dog / fish ...
    breed: str
    age: int
    diet: str
    energy_level: str               # high / medium / low
    medicines: list[str] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)

    # activity history (populated by the log_* methods)
    meal_log: list[str] = field(default_factory=list)
    exercise_log: list[str] = field(default_factory=list)
    medicine_log: list[str] = field(default_factory=list)

    # --- task collection management -------------------------------------
    def add_task(self, task: Task) -> None:
        """Attach a task to this pet (also stamps task.pet_assigned)."""
        task.pet_assigned = self
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Detach a task from this pet."""
        try:
            self.tasks.remove(task)
        except ValueError:
            return
        task.pet_assigned = None

    def list_tasks(self) -> list[Task]:
        """Return this pet's tasks sorted by due time."""
        return sorted(self.tasks, key=lambda t: t.scheduled_time)

    def pending_tasks(self) -> list[Task]:
        """Return this pet's not-yet-completed tasks, sorted by due time."""
        pending = (t for t in self.tasks if not t.completed)
        return sorted(pending, key=lambda t: t.scheduled_time)

    # --- activity logging ------------------------------------------------
    def log_meal(self, note: str = "") -> None:
        """Record that the pet was fed."""
        self.meal_log.append(note or "meal")

    def log_exercise(self, note: str = "") -> None:
        """Record an exercise / playtime session."""
        self.exercise_log.append(note or "exercise")

    def log_medicine(self, note: str = "") -> None:
        """Record that medicine was administered."""
        self.medicine_log.append(note or "medicine")

    # --- attribute updates ----------------------------------------------
    def update_name(self, name: str) -> None:
        """Rename the pet."""
        self.name = name

    def add_medicine(self, medicine: str) -> None:
        """Add a medicine to the pet's list."""
        self.medicines.append(medicine)

    def remove_medicine(self, medicine: str) -> None:
        """Remove a medicine from the pet's list."""
        try:
            self.medicines.remove(medicine)
        except ValueError:
            pass

    def update_diet(self, diet: str) -> None:
        """Change the pet's diet."""
        self.diet = diet

    def update_energy_level(self, level: str) -> None:
        """Update the pet's energy level (high / medium / low)."""
        self.energy_level = level


class Owner:
    """A pet owner: identifying info, their pets, and an end-of-day cutoff."""

    def __init__(self, first: str, last: str, end_of_day: time) -> None:
        """Create an owner with a name and an end-of-day scheduling cutoff."""
        self.first = first
        self.last = last
        self.end_of_day = end_of_day        # no task may be scheduled past this time
        self.pet_list: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list."""
        self.pet_list.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet from this owner's list."""
        try:
            self.pet_list.remove(pet)
        except ValueError:
            pass

    def update_first(self, first: str) -> None:
        """Update the owner's first name."""
        self.first = first

    def update_last(self, last: str) -> None:
        """Update the owner's last name."""
        self.last = last

    def all_tasks(self) -> list[Task]:
        """Every task across every pet this owner has."""
        return [task for pet in self.pet_list for task in pet.tasks]


class Scheduler:
    """Organizes tasks across ALL of an owner's pets onto one daily timeline.

    The schedule represents the owner's own time, so two tasks overlap (and
    conflict) even if they belong to different pets -- one person can only do
    one thing at once.
    """

    def __init__(self, owner: Owner) -> None:
        """Create a scheduler bound to one owner (and all their pets)."""
        self.owner = owner
        # Placed tasks, kept sorted by start time and always non-overlapping.
        self.placed: list[Task] = []
        self.skipped: list[Task] = []                # skippable tasks dropped
        self.unplaced: list[Task] = []               # tasks that couldn't fit
        self.conflicts: list[str] = []               # human-readable conflict warnings

    # --- public entry point ---------------------------------------------
    def build_daily_schedule(self) -> list[Task]:
        """Gather tasks from every pet and place them, highest priority first.

        Returns the resulting timeline as a start-time-sorted list of tasks.
        """
        self.placed.clear()
        self.skipped.clear()
        self.unplaced.clear()
        self.conflicts.clear()

        # Expand each task into its per-day occurrences, then place them in
        # precedence order (see _precedence). Because the strongest task always
        # reaches a slot first, whoever holds a slot already outranks any later
        # arrival -- so add_task never has to evict a task it already placed.
        occurrences: list[Task] = []
        for task in self.owner.all_tasks():
            occurrences.extend(self._expand_occurrences(task, self.owner.end_of_day))
        occurrences.sort(key=self._precedence)
        for occ in occurrences:
            self.add_task(occ, self.owner.end_of_day)
        return self.get_schedule()

    def get_schedule(self) -> list[Task]:
        """The organized timeline: tasks by start time (already sorted)."""
        return list(self.placed)

    def tasks_for_pet(self, pet: Pet) -> list[Task]:
        """Scheduled tasks belonging to one pet (organizing the shared timeline)."""
        return [t for t in self.placed if t.pet_assigned is pet]

    # --- sorting & filtering utilities ----------------------------------
    def sort_by_time(self, tasks: Optional[list[Task]] = None) -> list[Task]:
        """Return tasks sorted by their ``scheduled_time`` (ascending).

        Defaults to every task across the owner's pets; pass a list to sort a
        specific subset (e.g. the current schedule or a filtered view).
        """
        tasks = self.owner.all_tasks() if tasks is None else list(tasks)
        return sorted(tasks, key=lambda t: t.scheduled_time)

    def filter_tasks(
        self,
        tasks: Optional[list[Task]] = None,
        *,
        completed: Optional[bool] = None,
        pet_name: Optional[str] = None,
    ) -> list[Task]:
        """Return tasks filtered by completion status and/or pet name.

        Both filters are optional and combine with AND; leaving one as ``None``
        skips it. Defaults to every task across the owner's pets. Non-mutating.
        """
        tasks = self.owner.all_tasks() if tasks is None else list(tasks)
        result = tasks
        if completed is not None:
            result = [t for t in result if t.completed == completed]
        if pet_name is not None:
            result = [
                t for t in result
                if t.pet_assigned is not None and t.pet_assigned.name == pet_name
            ]
        return result

    # --- core scheduling logic ------------------------------------------
    #
    # Placement is a plain greedy pass: build_daily_schedule sorts every
    # occurrence by _precedence and adds them one at a time. Precedence puts the
    # strongest task first, so whoever reaches a slot keeps it and add_task only
    # has to place the *new* task -- fit it as-is, drop it (skippable), or nudge
    # it to the next free time. No eviction or re-placement to reason about.

    @staticmethod
    def _precedence(task: Task) -> tuple[bool, int, time]:
        """Placement order (ascending): the task placed first wins its slot.

        Non-skippable before skippable, then higher priority, then earlier
        requested time. Placing in this order is the whole conflict policy --
        it makes a later arrival always the one that yields.
        """
        return (task.skippable, -task.rank, task.scheduled_time)

    def find_conflicts(
        self, task: Task, among: Optional[list[Task]] = None
    ) -> list[Task]:
        """Every task in ``among`` whose time interval overlaps ``task``'s.

        ``among`` defaults to the tasks already placed on the schedule (used
        while building it). Pass a list -- e.g. ``owner.all_tasks()`` -- to
        check a task against existing tasks *before* scheduling, which is how
        the UI warns about a clash at add time. ``task`` itself is never
        counted, so it is safe to call before or after adding it.
        """
        among = self.placed if among is None else among
        start = _as_dt(task.scheduled_time)
        end = start + timedelta(minutes=max(task.duration, 0))
        hits = []
        for other in among:
            if other is task:
                continue
            o_start = _as_dt(other.scheduled_time)
            o_end = o_start + timedelta(minutes=max(other.duration, 0))
            if o_start < end and start < o_end:      # intervals overlap
                hits.append(other)
        return hits

    def add_task(self, task: Task, end_of_day: time) -> bool:
        """Place ``task`` on the timeline.

        Returns True if it landed on the schedule (at its requested time or
        nudged later), False if it was dropped (skippable) or could not fit
        before ``end_of_day``.
        """
        if task.scheduled_time > end_of_day:
            self._record_unplaced(task, "past end_of_day")
            return False

        # Requested slot is free -> place it as-is.
        conflicts = self.find_conflicts(task)
        if not conflicts:
            self._insert(task)
            return True

        # Conflict: a later arrival always yields (precedence placed the
        # stronger task first). Skippable tasks are dropped outright.
        if task.skippable:
            self._record_conflict(task, conflicts, "dropped (skippable)")
            self._record_skipped(task)
            return False

        # Otherwise slide it to the earliest free slot at/after its time.
        slot = self._earliest_free_slot(
            _as_dt(task.scheduled_time), task.duration, end_of_day
        )
        if slot is None:
            self._record_unplaced(task, "no free slot before end_of_day")
            return False
        self._record_conflict(task, conflicts, f"moved to {slot.strftime('%H:%M')}")
        task.scheduled_time = slot
        self._insert(task)
        return True

    # --- helpers ---------------------------------------------------------
    def _earliest_free_slot(
        self, not_before: datetime, duration: int, end_of_day: time
    ) -> Optional[time]:
        """Earliest start >= ``not_before`` where a ``duration``-minute task
        fits with no overlap and starts at/before ``end_of_day``.

        One left-to-right sweep over the sorted ``placed`` intervals. Returns a
        ``time``, or None if no gap exists before the cutoff (or it would cross
        midnight).
        """
        dur = timedelta(minutes=max(duration, 0))
        cutoff = _as_dt(end_of_day)
        candidate = not_before
        for placed in self.placed:
            p_start = _as_dt(placed.scheduled_time)
            p_end = p_start + timedelta(minutes=max(placed.duration, 0))
            if p_end <= candidate:
                continue                    # sits entirely before the gap
            if p_start - candidate >= dur:
                break                       # room before this task -> done
            candidate = p_end               # push past the blocker
        if candidate > cutoff or candidate.date() != _REF_DATE:
            return None
        return candidate.time()

    # --- sorted-list bookkeeping ----------------------------------------
    def _insert(self, task: Task) -> None:
        """Insert ``task`` into ``placed`` at its start time, keeping the list
        sorted (binary-search insertion).

        The sort order is what lets ``_earliest_free_slot`` sweep the timeline
        in a single left-to-right pass, so this invariant is load-bearing.
        """
        i = bisect.bisect_left(
            self.placed, task.scheduled_time, key=lambda t: t.scheduled_time
        )
        self.placed.insert(i, task)

    def _expand_occurrences(self, task: Task, end_of_day: time) -> list[Task]:
        """Turn one task into ``frequency`` concrete occurrences for the day.

        Occurrences are copies (the pet keeps the original as its declared
        intent), spread evenly across the window from the task's start time to
        end_of_day -- the first at the start time, the last at end_of_day. A
        frequency of 1 (or no room to spread) yields a single copy at the
        original time.
        """
        freq = max(task.frequency, 1)
        if freq == 1:
            return [replace(task)]

        start = _as_dt(task.scheduled_time)
        window_minutes = (_as_dt(end_of_day) - start).total_seconds() / 60.0
        if window_minutes <= 0:
            return [replace(task)]

        step = window_minutes / (freq - 1)
        occurrences = []
        for i in range(freq):
            slot = (start + timedelta(minutes=step * i)).time()
            occurrences.append(replace(
                task,
                scheduled_time=slot,
                frequency=1,
                description=f"{task.description} ({i + 1}/{freq})",
            ))
        return occurrences

    def _record_conflict(
        self, task: Task, conflicts: list[Task], outcome: str
    ) -> None:
        """Warn that ``task`` overlapped already-scheduled task(s), and note the
        outcome (``task`` always yields -- it is moved or dropped).
        """
        others = ", ".join(
            f"'{c.description}' @ {c.scheduled_time.strftime('%H:%M')}"
            for c in conflicts
        )
        msg = (
            f"'{task.description}' @ {task.scheduled_time.strftime('%H:%M')} "
            f"overlaps {others} -> {outcome}"
        )
        self.conflicts.append(msg)
        print(f"[conflict] {msg}")

    def _record_skipped(self, task: Task) -> None:
        """Log a skippable task that was dropped because it lost its slot."""
        self.skipped.append(task)
        print(f"[skipped] '{task.description}' for "
              f"{task.pet_assigned.name if task.pet_assigned else '?'} "
              f"(skippable, lost its slot)")

    def _record_unplaced(self, task: Task, reason: str) -> None:
        """Log a task that could not be scheduled at all."""
        self.unplaced.append(task)
        print(f"[UNPLACED] '{task.description}' for "
              f"{task.pet_assigned.name if task.pet_assigned else '?'} ({reason})")


if __name__ == "__main__":
    # Small demo: one owner, two pets, overlapping morning tasks across pets.
    owner = Owner("Bri", "Weeks", end_of_day=time(20, 0))

    rex = Pet("Rex", "dog", "Corgi", 3, "kibble", "high")
    milo = Pet("Milo", "cat", "Tabby", 5, "wet food", "low")
    owner.add_pet(rex)
    owner.add_pet(milo)

    # Feed Rex twice a day -> Scheduler spreads the two occurrences out.
    rex.add_task(Task("Feeding", time(7, 0), duration=15, frequency=2, priority="high"))
    # Milo also wants breakfast at 07:00 -> cross-pet conflict, gets nudged.
    milo.add_task(Task("Breakfast", time(7, 0), duration=10, priority="high"))
    # A walk also wants 07:00 but is skippable -> it loses and is dropped.
    rex.add_task(Task("Morning walk", time(7, 0), duration=30,
                      skippable=True, priority="low"))
    # A non-conflicting evening med.
    milo.add_task(Task("Evening medicine", time(18, 0), duration=5, priority="high"))

    scheduler = Scheduler(owner)
    scheduler.build_daily_schedule()

    print("\nDaily schedule (across all pets):")
    for task in scheduler.get_schedule():
        pet = task.pet_assigned.name if task.pet_assigned else "?"
        print(f"  {task.scheduled_time.strftime('%H:%M')}  {pet:5} {task.description} "
              f"({task.duration}m, {task.priority})")
