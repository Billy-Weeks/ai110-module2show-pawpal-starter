# Imports

from datetime import time

from pawpal_system import Task, Owner, Pet, Scheduler


# --- Owner ---------------------------------------------------------------
sally = Owner("Sally", "Weeks", end_of_day=time(20, 0))

# --- Pets ----------------------------------------------------------------
# Pet(name, pet_type, breed, age, diet, energy_level)
dino = Pet("Dino", "Cat", "Short-haired", 5, "Wet food", "medium")
butterscotch = Pet("Butterscotch", "Dog", "German Shepherd", 12, "Kibble", "low")
kiwi = Pet("Kiwi", "Bird", "Parakeet", 2, "Seeds", "medium")

sally.add_pet(dino)
sally.add_pet(butterscotch)
sally.add_pet(kiwi)

# --- Tasks (3 per pet, at different times) -------------------------------
# Task(description, scheduled_time, duration, frequency, skippable, priority)
dino.add_task(Task("Breakfast", time(7, 0), duration=10, priority="high"))
dino.add_task(Task("Litter box", time(12, 0), duration=15, priority="medium"))
dino.add_task(Task("Play with feather toy", time(17, 0), duration=20,
                   skippable=True, priority="low"))

butterscotch.add_task(Task("Breakfast", time(7, 30), duration=15, priority="high"))
butterscotch.add_task(Task("Morning walk", time(9, 0), duration=30, priority="medium"))
butterscotch.add_task(Task("Evening walk", time(18, 0), duration=30,
                  skippable=True, priority="low"))

kiwi.add_task(Task("Refill seeds", time(8, 0), duration=5, priority="high"))
kiwi.add_task(Task("Clean cage", time(13, 0), duration=20, priority="medium"))
kiwi.add_task(Task("Cover cage for night", time(19, 30), duration=5,
                   priority="medium"))

# --- Build and print today's schedule ------------------------------------
scheduler = Scheduler(sally)
scheduler.build_daily_schedule()

print(f"\nToday's Schedule for {sally.first} {sally.last}:")
print("-" * 40)
for task in scheduler.get_schedule():
    pet_name = task.pet_assigned.name if task.pet_assigned else "?"
    print(f"  {task.scheduled_time.strftime('%H:%M')}  "
          f"{pet_name:15.15} {task.description}")


# --- Demo: tasks added OUT OF ORDER --------------------------------------
# Real users rarely enter tasks in chronological order. Here we deliberately
# add a pet's tasks scrambled by time to show that neither the ordering nor
# the scheduling depend on insertion order: sort_by_time() and
# build_daily_schedule() both normalize the timeline for us.
print(f"\n\nOut-of-order demo for {sally.first}:")
print("=" * 40)

gizmo = Pet("Gizmo", "Cat", "Tabby", 3, "Wet food", "high")
sally.add_pet(gizmo)

# Intentionally scrambled: evening, morning, afternoon, dawn, midday.
gizmo.add_task(Task("Bedtime snack", time(19, 30), duration=10, priority="medium"))
gizmo.add_task(Task("Breakfast", time(7, 0), duration=10, priority="high"))
gizmo.add_task(Task("Afternoon play", time(15, 0), duration=20,
                    skippable=True, priority="low"))
gizmo.add_task(Task("Sunrise medicine", time(6, 0), duration=5, priority="high"))
gizmo.add_task(Task("Lunch", time(12, 0), duration=15, priority="medium"))

print("\nAs entered (insertion order):")
for task in gizmo.tasks:
    print(f"  {task.scheduled_time.strftime('%H:%M')}  {task.description}")

# sort_by_time() reorders any task list chronologically without scheduling.
print("\nAfter Scheduler.sort_by_time():")
for task in scheduler.sort_by_time(gizmo.tasks):
    print(f"  {task.scheduled_time.strftime('%H:%M')}  {task.description}")

# build_daily_schedule() also places everything on an ordered timeline.
scheduler.build_daily_schedule()
print("\nRebuilt daily schedule (Gizmo's tasks in place):")
print("-" * 40)
for task in scheduler.tasks_for_pet(gizmo):
    print(f"  {task.scheduled_time.strftime('%H:%M')}  {task.description}")


# --- Demo: two tasks at the SAME time (direct conflict) ------------------
# An isolated owner so nothing else competes for the timeline. Two tasks are
# scheduled at the exact same time (08:00), so they can't both happen -- the
# Scheduler detects the overlap, keeps the higher-priority task in the slot,
# and nudges the loser to the next free time.
print("\n\nSame-time conflict demo:")
print("=" * 40)

alex = Owner("Alex", "Rivera", end_of_day=time(20, 0))
banjo = Pet("Banjo", "Dog", "Beagle", 4, "Kibble", "high")
alex.add_pet(banjo)

# Both want 08:00 -> guaranteed conflict.
banjo.add_task(Task("Breakfast", time(8, 0), duration=20, priority="high"))
banjo.add_task(Task("Morning walk", time(8, 0), duration=30, priority="low"))

print("\nBoth tasks requested for 08:00:")
for task in banjo.tasks:
    print(f"  {task.scheduled_time.strftime('%H:%M')}  {task.description} "
          f"({task.priority})")

conflict_scheduler = Scheduler(alex)
print("\nBuilding schedule (watch the [conflict] warning):")
conflict_scheduler.build_daily_schedule()

print("\nResolved schedule:")
print("-" * 40)
for task in conflict_scheduler.get_schedule():
    print(f"  {task.scheduled_time.strftime('%H:%M')}  {task.description} "
          f"({task.priority})")

if conflict_scheduler.conflicts:
    print("\nConflicts reported:")
    for note in conflict_scheduler.conflicts:
        print(f"  - {note}")
