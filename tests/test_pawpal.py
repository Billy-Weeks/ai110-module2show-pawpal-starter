"""Tests for the PawPal+ system."""

from datetime import date, time

from pawpal_system import Task, Pet, Owner, Scheduler


def test_mark_complete_changes_status():
    """mark_complete() should flip a task's completion status to True."""
    task = Task("Feed the cat", time(8, 0), duration=10, priority="high")

    # A new task starts out not completed.
    assert task.completed is False

    task.mark_complete()

    # After marking, its status is now complete.
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    """Adding a task to a pet should grow that pet's task list by one."""
    pet = Pet("Mochi", "dog", "Shiba", 4, "kibble", "high")

    # A brand-new pet has no tasks.
    assert len(pet.tasks) == 0

    pet.add_task(Task("Morning walk", time(9, 0), duration=30, priority="medium"))

    # The count went up by one, and the task is now linked back to the pet.
    assert len(pet.tasks) == 1
    assert pet.tasks[0].pet_assigned is pet


def test_sort_by_time_returns_chronological_order():
    """sort_by_time() should return tasks ordered earliest -> latest,
    regardless of the order they were added in."""
    owner = Owner("Sam", "Lee", end_of_day=time(20, 0))
    pet = Pet("Mochi", "dog", "Shiba", 4, "kibble", "high")
    owner.add_pet(pet)

    # Added deliberately out of chronological order: noon, dawn, evening.
    pet.add_task(Task("Lunch", time(12, 0), duration=15, priority="medium"))
    pet.add_task(Task("Breakfast", time(7, 0), duration=10, priority="high"))
    pet.add_task(Task("Dinner", time(18, 0), duration=20, priority="medium"))

    ordered = Scheduler(owner).sort_by_time()
    times = [t.scheduled_time for t in ordered]

    # The result is sorted ascending by scheduled_time.
    assert times == [time(7, 0), time(12, 0), time(18, 0)]
    assert [t.description for t in ordered] == ["Breakfast", "Lunch", "Dinner"]


def test_mark_complete_on_daily_task_spawns_next_day():
    """Completing a daily-recurring task should create a fresh, uncompleted
    occurrence due one day later, attached back to the same pet."""
    pet = Pet("Kiwi", "bird", "Parakeet", 2, "seeds", "medium")
    task = Task(
        "Refill seeds",
        time(8, 0),
        duration=5,
        priority="high",
        recurrence="daily",
        due_date=date(2026, 7, 3),
    )
    pet.add_task(task)

    next_task = task.mark_complete()

    # The original is now complete; a next occurrence was returned.
    assert task.completed is True
    assert next_task is not None

    # The new occurrence is uncompleted, one day later, same time & pet.
    assert next_task.completed is False
    assert next_task.due_date == date(2026, 7, 4)
    assert next_task.scheduled_time == time(8, 0)
    assert next_task.pet_assigned is pet

    # spawn_next_occurrence auto-adds the new task back to the pet.
    assert next_task in pet.tasks


def test_scheduler_detects_same_time_conflict():
    """find_conflicts() should flag two tasks scheduled at the same time as
    overlapping."""
    owner = Owner("Alex", "Rivera", end_of_day=time(20, 0))
    dog = Pet("Banjo", "dog", "Beagle", 4, "kibble", "high")
    owner.add_pet(dog)

    breakfast = Task("Breakfast", time(8, 0), duration=20, priority="high")
    walk = Task("Morning walk", time(8, 0), duration=30, priority="low")
    dog.add_task(breakfast)
    dog.add_task(walk)

    # Checking the walk against all existing tasks flags the breakfast clash.
    clashes = Scheduler(owner).find_conflicts(walk, owner.all_tasks())
    assert breakfast in clashes

    # After building the schedule, the overlap is recorded and resolved:
    # both tasks still land (the loser is nudged), and a conflict is noted.
    scheduler = Scheduler(owner)
    scheduler.build_daily_schedule()
    assert len(scheduler.conflicts) >= 1
    scheduled_times = [t.scheduled_time for t in scheduler.get_schedule()]
    assert len(scheduled_times) == 2
    assert len(set(scheduled_times)) == 2  # no longer share a slot


def test_empty_owner_schedule_is_empty():
    """An owner with no pets (and therefore no tasks) should build an empty
    schedule without error."""
    owner = Owner("Jordan", "Owner", end_of_day=time(20, 0))

    assert owner.all_tasks() == []

    scheduler = Scheduler(owner)
    schedule = scheduler.build_daily_schedule()

    # Nothing to place -> empty timeline and no conflicts/skips/unplaced.
    assert schedule == []
    assert scheduler.get_schedule() == []
    assert scheduler.conflicts == []
    assert scheduler.skipped == []
    assert scheduler.unplaced == []


if __name__ == "__main__":
    test_mark_complete_changes_status()
    print("PASS: mark_complete() changes the task's status")

    test_add_task_increases_pet_task_count()
    print("PASS: adding a task increases the pet's task count")

    test_sort_by_time_returns_chronological_order()
    print("PASS: sort_by_time() returns tasks in chronological order")

    test_mark_complete_on_daily_task_spawns_next_day()
    print("PASS: completing a daily task spawns the next day's occurrence")

    test_scheduler_detects_same_time_conflict()
    print("PASS: scheduler detects and resolves same-time conflicts")

    test_empty_owner_schedule_is_empty()
    print("PASS: an empty owner builds an empty schedule")

    print("\nAll tests passed.")
