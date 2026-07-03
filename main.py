# Imports
# NOTE: import `time` from datetime (the time-of-day class), NOT from the
# `time` module -- that one is a function and can't take (hour, minute).
from datetime import time

from pawpal_system import Task, Owner, Pet, Scheduler


# --- Owner ---------------------------------------------------------------
sally = Owner("Sally", "Weeks", end_of_day=time(20, 0))

# --- Pets ----------------------------------------------------------------
# Pet(name, pet_type, breed, age, diet, energy_level)
# medicines and tasks are optional -- they default to empty lists, so you
# don't have to pass them here.
dino = Pet("Dino", "Cat", "Short-haired", 5, "Wet food", "low")
rex = Pet("Rex", "Dog", "Corgi", 3, "Kibble", "high")
kiwi = Pet("Kiwi", "Bird", "Parakeet", 2, "Seeds", "medium")

sally.add_pet(dino)
sally.add_pet(rex)
sally.add_pet(kiwi)

# --- Tasks (3 per pet, at different times) -------------------------------
# Task(description, scheduled_time, duration, frequency, skippable, priority)
dino.add_task(Task("Breakfast", time(7, 0), duration=10, priority="high"))
dino.add_task(Task("Litter box", time(12, 0), duration=15, priority="medium"))
dino.add_task(Task("Play with feather toy", time(17, 0), duration=20,
                   skippable=True, priority="low"))

rex.add_task(Task("Breakfast", time(7, 30), duration=15, priority="high"))
rex.add_task(Task("Morning walk", time(9, 0), duration=30, priority="medium"))
rex.add_task(Task("Evening walk", time(18, 0), duration=30,
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
          f"{pet_name:5} {task.description}")
