"""PawPal+ system.

Class structure generated from the UML design in diagrams/uml_draft.mmd.

Design notes / resolved issues:
  * A Task is a single occurrence with one due time (frequency removed);
    recurring activities are modeled as multiple Task instances.
  * Pet owns its Tasks (add/list/manage); Task.pet_assigned is set on add,
    so a Task can never reference a pet the owner does not have.
  * Scheduler manages tasks across ALL of an owner's pets, treating the
    schedule as the owner's single timeline (one person, one thing at a time).
  * Conflicts are detected by time-interval OVERLAP (using duration), not just
    exact start time.
  * Times use datetime math with a midnight/end-of-day guard so the recursive
    nudge cannot push a task past the owner's cutoff or roll past midnight.
  * Dropped/unplaced tasks are logged (surfaced) instead of silently lost.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from typing import Optional

# Reference date used only for time arithmetic (add_task never needs "today").
_REF_DATE = datetime.min.date()

# Higher number = higher priority. Unknown labels rank lowest (0).
PRIORITY_RANK = {"high": 3, "medium": 2, "low": 1}


def _as_dt(t: time) -> datetime:
    """Combine a time with the reference date so we can do arithmetic on it."""
    return datetime.combine(_REF_DATE, t)


@dataclass
class Task:
    """A single scheduled activity for a pet (feeding, walk, medicine, ...)."""

    description: str
    scheduled_time: time            # due time
    duration: int = 0               # minutes
    skippable: bool = False         # True if it can be dropped for the day (a walk)
    priority: str = "medium"        # high / medium / low
    completed: bool = False         # completion status
    pet_assigned: Optional["Pet"] = None  # set by Pet.add_task

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True

    def change_description(self, description: str) -> None:
        self.description = description

    def update_duration(self, duration: int) -> None:
        self.duration = duration


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
        if task in self.tasks:
            self.tasks.remove(task)
            task.pet_assigned = None

    def list_tasks(self) -> list[Task]:
        """Return this pet's tasks sorted by due time."""
        return sorted(self.tasks, key=lambda t: t.scheduled_time)

    def pending_tasks(self) -> list[Task]:
        return [t for t in self.list_tasks() if not t.completed]

    # --- activity logging ------------------------------------------------
    def log_meal(self, note: str = "") -> None:
        self.meal_log.append(note or "meal")

    def log_exercise(self, note: str = "") -> None:
        self.exercise_log.append(note or "exercise")

    def log_medicine(self, note: str = "") -> None:
        self.medicine_log.append(note or "medicine")

    # --- attribute updates ----------------------------------------------
    def update_name(self, name: str) -> None:
        self.name = name

    def add_medicine(self, medicine: str) -> None:
        self.medicines.append(medicine)

    def remove_medicine(self, medicine: str) -> None:
        if medicine in self.medicines:
            self.medicines.remove(medicine)

    def update_diet(self, diet: str) -> None:
        self.diet = diet

    def update_energy_level(self, level: str) -> None:
        self.energy_level = level


class Owner:
    """A pet owner: identifying info, their pets, and an end-of-day cutoff."""

    def __init__(self, first: str, last: str, end_of_day: time) -> None:
        self.first = first
        self.last = last
        self.end_of_day = end_of_day        # no task may be scheduled past this time
        self.pet_list: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        self.pet_list.append(pet)

    def remove_pet(self, pet: Pet) -> None:
        if pet in self.pet_list:
            self.pet_list.remove(pet)

    def update_first(self, first: str) -> None:
        self.first = first

    def update_last(self, last: str) -> None:
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
        self.owner = owner
        self.daily_schedule: dict[time, Task] = {}   # start time -> Task
        self.skipped: list[Task] = []                # skippable tasks dropped
        self.unplaced: list[Task] = []               # tasks that couldn't fit

    # --- public entry point ---------------------------------------------
    def build_daily_schedule(self) -> dict[time, Task]:
        """Gather tasks from every pet and place them, highest priority first.

        Returns the resulting {time: Task} schedule.
        """
        self.daily_schedule.clear()
        self.skipped.clear()
        self.unplaced.clear()

        # High-priority tasks claim their preferred slot before lower ones.
        tasks = sorted(
            self.owner.all_tasks(),
            key=lambda t: (-PRIORITY_RANK.get(t.priority, 0), t.scheduled_time),
        )
        for task in tasks:
            self.add_task(task, self.owner.end_of_day)
        return self.daily_schedule

    def get_schedule(self) -> list[Task]:
        """The organized timeline: tasks sorted by start time (across pets)."""
        return [self.daily_schedule[k] for k in sorted(self.daily_schedule)]

    def tasks_for_pet(self, pet: Pet) -> list[Task]:
        """Scheduled tasks belonging to one pet (organizing the shared timeline)."""
        return [t for t in self.get_schedule() if t.pet_assigned is pet]

    # --- core scheduling logic ------------------------------------------
    def conflict_check(self, task: Task) -> Optional[Task]:
        """Detector: return an already-scheduled task whose time interval
        overlaps ``task``, or None if the slot range is free.
        """
        start = _as_dt(task.scheduled_time)
        end = start + timedelta(minutes=max(task.duration, 0))
        for other in self.daily_schedule.values():
            if other is task:
                continue
            o_start = _as_dt(other.scheduled_time)
            o_end = o_start + timedelta(minutes=max(other.duration, 0))
            if start < o_end and o_start < end:      # intervals overlap
                return other
        return None

    def resolve_conflict(self, new_task: Task, existing: Task) -> Task:
        """Decider: return the "loser" that must leave the slot.

        1. A skippable task yields to a non-skippable one.
        2. Otherwise the lower-priority task loses.
        3. On a tie, first-come-stays: the existing task keeps the slot.
        """
        if new_task.skippable != existing.skippable:
            return new_task if new_task.skippable else existing

        rank_new = PRIORITY_RANK.get(new_task.priority, 0)
        rank_existing = PRIORITY_RANK.get(existing.priority, 0)
        if rank_new > rank_existing:
            return existing
        if rank_existing > rank_new:
            return new_task
        return new_task  # tie -> existing stays

    def add_task(self, task: Task, end_of_day: time) -> bool:
        """Entry point / orchestrator. Try to place ``task``.

        Returns True if ``task`` ended up on the schedule (possibly nudged to a
        later slot), False if it could not be placed before ``end_of_day`` or
        was intentionally skipped.
        """
        # 1. Bounds check (also stops the recursion from running past midnight).
        if task.scheduled_time > end_of_day:
            self._record_unplaced(task, "past end_of_day")
            return False

        # 2. Free slot?
        existing = self.conflict_check(task)
        if existing is None:
            self.daily_schedule[task.scheduled_time] = task
            return True

        # 3. Conflict -> decide who leaves the slot.
        loser = self.resolve_conflict(task, existing)

        if loser is existing:
            # New task wins: remove the existing task, then place the new one
            # (re-checking against any OTHER overlaps via recursion).
            del self.daily_schedule[existing.scheduled_time]
            placed = self.add_task(task, end_of_day)
            self._reschedule_loser(existing, winner=task, end_of_day=end_of_day)
            return placed

        # task itself is the loser.
        if task.skippable:
            self._record_skipped(task)
            return False
        return self._reschedule_loser(task, winner=existing, end_of_day=end_of_day)

    # --- helpers ---------------------------------------------------------
    def _reschedule_loser(self, loser: Task, winner: Task, end_of_day: time) -> bool:
        """Move ``loser`` to just after ``winner`` ends and re-add it.

        Skippable losers are dropped (logged) rather than nudged.
        """
        if loser.skippable:
            self._record_skipped(loser)
            return False

        nudged = self._nudge_after(winner)
        if nudged is None:                      # rolled past midnight
            self._record_unplaced(loser, "nudged past midnight")
            return False
        loser.scheduled_time = nudged
        return self.add_task(loser, end_of_day)

    def _nudge_after(self, winner: Task) -> Optional[time]:
        """The first free start time after ``winner`` ends.

        Advances by at least 1 minute so a zero-duration winner can't cause an
        infinite loop. Returns None if the new time rolls past midnight.
        """
        minutes = max(winner.duration, 1)
        new_dt = _as_dt(winner.scheduled_time) + timedelta(minutes=minutes)
        if new_dt.date() != _REF_DATE:          # crossed midnight
            return None
        return new_dt.time()

    def _record_skipped(self, task: Task) -> None:
        self.skipped.append(task)
        print(f"[skipped] '{task.description}' for "
              f"{task.pet_assigned.name if task.pet_assigned else '?'} "
              f"(skippable, lost its slot)")

    def _record_unplaced(self, task: Task, reason: str) -> None:
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

    # Both breakfast feedings want 07:00 (high, non-skippable) -> one gets nudged.
    rex.add_task(Task("Breakfast", time(7, 0), duration=15, priority="high"))
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
