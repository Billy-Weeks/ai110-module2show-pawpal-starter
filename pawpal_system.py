"""PawPal+ system skeleton.

Class structure generated from the UML design in diagrams/uml_draft.mmd.
Method bodies are intentionally left unimplemented (skeleton only).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import time
from typing import Optional


@dataclass
class Pet:
    """A single pet owned by an Owner."""

    name: str
    pet_type: str          # cat / dog / fish ...
    breed: str
    age: int
    diet: str
    energy_level: str      # high / medium / low
    medicines: list[str] = field(default_factory=list)

    def log_meal(self) -> None:
        """Record that the pet was fed."""
        ...

    def log_exercise(self) -> None:
        """Record an exercise / playtime session."""
        ...

    def log_medicine(self) -> None:
        """Record that medicine was administered."""
        ...

    def update_name(self, name: str) -> None:
        ...

    def add_medicine(self, medicine: str) -> None:
        ...

    def remove_medicine(self, medicine: str) -> None:
        ...

    def update_diet(self, diet: str) -> None:
        ...

    def update_energy_level(self, level: str) -> None:
        ...


@dataclass
class Task:
    """A scheduled activity for a pet (feeding, walk, medicine, etc.)."""

    name: str
    pet_assigned: Pet
    duration: int              # minutes
    frequency: int             # times per day
    skippable: bool            # True if it can be dropped for the day (e.g. a walk)
    priority: str              # high / medium / low
    scheduled_time: time
    completed: bool = False

    def change_name(self, name: str) -> None:
        ...

    def update_duration(self, duration: int) -> None:
        ...


class Owner:
    """A pet owner. Holds their pets and their preferred end-of-day cutoff."""

    def __init__(self, first: str, last: str, end_of_day: time) -> None:
        self.first = first
        self.last = last
        self.end_of_day = end_of_day        # no task may be scheduled past this time
        self.pet_list: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        ...

    def remove_pet(self, pet: Pet) -> None:
        ...

    def update_first(self, first: str) -> None:
        ...

    def update_last(self, last: str) -> None:
        ...


class Scheduler:
    """Builds a daily schedule, keyed by time, and resolves conflicts."""

    def __init__(self) -> None:
        # time slot -> the Task occupying it
        self.daily_schedule: dict[time, Task] = {}

    def conflict_check(self, task: Task) -> Optional[Task]:
        """Detector.

        Return the Task already occupying ``task.scheduled_time``,
        or None if the slot is free.
        """
        ...

    def resolve_conflict(self, new_task: Task, existing: Task) -> Optional[Task]:
        """Decider.

        Decide which task keeps the slot when two collide, and return the
        "loser" that needs rescheduling (or None if the loser was skipped).

        Rule order:
          1. If exactly one task is skippable, that one is skipped (a walk can
             be dropped; feeding cannot).
          2. If neither is skippable, the lower-priority task is nudged and the
             higher-priority task keeps the slot.
        """
        ...

    def add_task(self, task: Task, end_of_day: time) -> bool:
        """Entry point / orchestrator.

        Try to place ``task`` on the schedule. Returns True if it was
        scheduled, False if it could not fit before ``end_of_day``.

        Flow:
          1. If task.scheduled_time is past end_of_day -> return False.
          2. existing = conflict_check(task); if None, place task -> return True.
          3. Otherwise loser = resolve_conflict(task, existing); winner keeps
             the slot. Nudge loser forward by the winner's duration and
             recurse: add_task(loser, end_of_day).
        """
        ...
