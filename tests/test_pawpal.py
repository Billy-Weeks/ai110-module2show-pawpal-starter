"""Tests for the PawPal+ system."""

from datetime import time

from pawpal_system import Task, Pet


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


if __name__ == "__main__":
    test_mark_complete_changes_status()
    print("PASS: mark_complete() changes the task's status")

    test_add_task_increases_pet_task_count()
    print("PASS: adding a task increases the pet's task count")

    print("\nAll tests passed.")
