import streamlit as st
from datetime import time

from pawpal_system import Pet, Owner, Task, Scheduler


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption(
    "A pet-care planning assistant: add pets, give them tasks, and build a "
    "conflict-free daily schedule across all of an owner's pets."
)

with st.expander("Scenario", expanded=False):
    st.markdown(
        """
**PawPal+** helps a pet owner plan care tasks for their pet(s) based on
constraints like time, priority, and whether a task can be skipped. The
scheduler treats the day as the owner's single timeline, so overlapping tasks
are nudged or skipped based on priority.
"""
    )

# --- Persistent state ("the vault") --------------------------------------
# Create the Owner ONCE. Streamlit reruns this whole script on every click,
# so without session_state the Owner (and all its pets/tasks) would be rebuilt
# from scratch each time. Checking `"owner" not in st.session_state` first
# means we only build it on the very first run and reuse it afterwards.
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan", "Owner", end_of_day=time(20, 0))
owner = st.session_state.owner

st.divider()

# --- Owner profile --------------------------------------------------------
st.subheader("Owner profile")
col_a, col_b = st.columns(2)
with col_a:
    owner.first = st.text_input("First name", value=owner.first)
with col_b:
    owner.last = st.text_input("Last name", value=owner.last)
owner.end_of_day = st.time_input(
    "End of day (nothing gets scheduled past this)", value=owner.end_of_day
)

st.divider()

# --- Add a pet ------------------------------------------------------------
st.subheader("Add a pet")
p1, p2, p3 = st.columns(3)
with p1:
    pet_name = st.text_input("Pet name", value="Mochi")
    breed = st.text_input("Breed", value="Unknown")
with p2:
    species = st.selectbox("Species", ["dog", "cat", "bird", "fish", "other"])
    age = st.number_input("Age", min_value=0, max_value=100, value=1)
with p3:
    diet = st.text_input("Diet", value="Standard")
    energy = st.selectbox("Energy level", ["low", "medium", "high"], index=1)

# Real method call: build a Pet and add it to the persistent Owner.
if st.button("Add pet"):
    owner.add_pet(Pet(pet_name, species, breed, int(age), diet, energy))
    st.success(f"Added {pet_name} to {owner.first}'s pets.")

if owner.pet_list:
    st.write("**Current pets:** " + ", ".join(p.name for p in owner.pet_list))
else:
    st.info("No pets yet. Add one above.")

st.divider()

# --- Add a task to a pet --------------------------------------------------
st.subheader("Add a task")
if not owner.pet_list:
    st.warning("Add a pet first before creating tasks.")
else:
    pet = st.selectbox(
        "For which pet?", owner.pet_list, format_func=lambda p: p.name
    )

    t1, t2, t3 = st.columns(3)
    with t1:
        task_title = st.text_input("Task title", value="Morning walk")
        task_time = st.time_input("Time", value=time(9, 0))
    with t2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        frequency = st.number_input("Times per day", min_value=1, max_value=12, value=1)
    with t3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        recurrence = st.selectbox("Repeats", ["none", "daily", "weekly"])
        skippable = st.checkbox("Skippable (can be dropped for the day)")

    # Real method call: build a Task and add it to the chosen Pet.
    if st.button("Add task"):
        pet.add_task(Task(
            task_title,
            task_time,
            duration=int(duration),
            frequency=int(frequency),
            skippable=skippable,
            priority=priority,
            recurrence=recurrence,
        ))
        st.success(f"Added '{task_title}' to {pet.name}.")

# Show every task added so far, across all pets -- with sort/filter controls.
all_tasks = owner.all_tasks()
if all_tasks:
    st.write("**Tasks added:**")

    f1, f2 = st.columns(2)
    with f1:
        pet_filter = st.selectbox(
            "Filter by pet", ["(all)"] + [p.name for p in owner.pet_list]
        )
    with f2:
        status_filter = st.selectbox(
            "Filter by status", ["(all)", "pending", "completed"]
        )

    # Scheduler.filter_tasks / sort_by_time (no scheduling needed to view).
    view = Scheduler(owner)
    shown = view.filter_tasks(
        completed=None if status_filter == "(all)" else status_filter == "completed",
        pet_name=None if pet_filter == "(all)" else pet_filter,
    )
    shown = view.sort_by_time(shown)

    if shown:
        st.table([
            {
                "Pet": t.pet_assigned.name if t.pet_assigned else "?",
                "Task": t.description,
                "Time": t.scheduled_time.strftime("%H:%M"),
                "Duration": t.duration,
                "Times/day": t.frequency,
                "Priority": t.priority,
                "Repeats": t.recurrence,
                "Skippable": t.skippable,
                "Done": t.completed,
            }
            for t in shown
        ])
    else:
        st.info("No tasks match the current filter.")

st.divider()

# --- Build schedule -------------------------------------------------------
st.subheader("Today's schedule")
st.caption("Runs the Scheduler across all of the owner's pets on one timeline.")

if st.button("Generate schedule"):
    scheduler = Scheduler(owner)
    scheduler.build_daily_schedule()
    schedule = scheduler.get_schedule()

    if schedule:
        st.table([
            {
                "Time": t.scheduled_time.strftime("%H:%M"),
                "Pet": t.pet_assigned.name if t.pet_assigned else "?",
                "Task": t.description,
                "Duration": f"{t.duration}m",
                "Priority": t.priority,
            }
            for t in schedule
        ])
    else:
        st.info("Nothing to schedule yet. Add some tasks first.")

    # Surface any overlaps the scheduler had to resolve.
    if scheduler.conflicts:
        st.warning(
            "Conflicts detected and resolved:\n\n- "
            + "\n- ".join(scheduler.conflicts)
        )

    # Surface anything the scheduler dropped or couldn't fit.
    if scheduler.skipped:
        st.warning(
            "Skipped (skippable tasks that lost their slot): "
            + ", ".join(t.description for t in scheduler.skipped)
        )
    if scheduler.unplaced:
        st.error(
            "Could not fit before end of day: "
            + ", ".join(t.description for t in scheduler.unplaced)
        )