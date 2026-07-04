# PawPal+ Project Reflection

## 1. System Design
**3 Core Actions**
- Create an owner profile and be able to add pets
- Adjust/create a feeding schedule
- Adjust/create a exercise/playtime schedule

**a. Initial design**

- Briefly describe your initial UML design.
The UML design relies on a hierarchical relationship where a single Owner manages multiple Pets (objects --> one-to-many relationship). Each Pet is linked to specific Task objects, representing individual daily care requirements. The Scheduler acts as the central logic engine, using owner's data and associated tasks to build an organized, conflict-free chronological timeline.

- What classes did you include, and what responsibilities did you assign to each?
1. Pet
    Attributes:
        Name
        Type of pet (cat/dog/fish..)
        Breed
        Age
        Diet
        Medicines
        Energy Level (high, medium, low)
    Methods:
        log meal
        log exercise
        log medicine
        update name
        add medicine
        remove medicine
        update diet
        update energy level
        
2. Owner
    Attributes:
        First
        Last
        Pet list
    Methods:
        Add pet
        Remove pet
        update first
        update last
3. Task
    Attributes:
        Name of task
        Pet assigned to task
        Length of time (duration)
        How often per day (frequency)
        Boolean to set if task is "skippable"
        When (scheduled time)
        completed task
    Methods:
        Change name
        update length of time	
4. Scheduler
    Attributes:
        daily schedule			
    Methods:	
        conflict check
        add task to schedule


**b. Design changes**

- Did your design change during implementation?
Yes it changed slightly in a few classes and greatly in others

- If yes, describe at least one change and why you made it.
The biggest change was to the Scheduler class. My initial logic was pretty vague so when we began to diagram it was necessary to further define the class. Specifically, we highlighted that conflictCheck could be split into: Detector (conflictCheck), Decider (newly created resolveConflict), and addTask (previously existed, but now acts as the entry point and has recursion to check if tasks get moved from original intended scheduled time). Doing this allowed not only better logic, but hopefully allowed for better future proofing. This also added functionality and error checking because not only does it check for conflicts, it'll reschedule those conflicts if need be (checking the skippable flag). Then if neither task is skippable, Tasks has a newly added priority attribute which is then used to decide who gets nudged to another time. To avoid further conflicts, addTask is called again to make sure there isn't a conflict at the new time. The process continues from here until all conflicts are resolved or owner declared endOfDay is reached.

EndofDay acts as a guardrail to prevent the addTask from constantly running if there happens to be constant conflicts on a task(s). Once the time stored in endOfDay (declared by the owner) is reached, the task is then dropped from the schedule for the day. 

After building the skeleton of classes, Claude noticed that Task pointed to Pet on paper (each task knew which pet it was for). However, Pet had no way to hold or manage its own tasks and log_meal/log_exercise methods had nowhere to store anything. Seeing the skeleton made this gap obvious, so we turned the relationship around: Pet owns a collection of Task's with methods to add/list/remove them. Pet.add_task automatically stamps the task with its owner pet, fixing two problems at once. 
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?

The scheduler considers time and priority, however there is no implementation for preferences.
- How did you decide which constraints mattered most?

Due to how priority is implemented, it is given the most weight so that when there is a conflict, the highest priority will always win. 

The logic behind this is that tasks such as feeding, medicine that needs to be taken at a certain time, etc. should be given precendence over walking, exercise, playtime. While those are important, not eating is detrimental to pets. 

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.

The tradeoff: Priority over punctuality.
When two tasks want the same slot, the scheduler favors priority over keeping the request time. The higher priority task keeps its requested slot and the lower priority is either dropped if designated as skippable or nudged to the next free time slot.

- Why is that tradeoff reasonable for this scenario?

This is reasonable because it allows those important tasks to not be ignored while allowing tasks that can be pushed to a later time (i.e. going for a walk) moved to a conflict-free time. This also gives control to the Owner to dictate those tasks which have to happen when they are requested by setting the priority and then allowing those tasks that would be great if we do them (puppy play park) but it's okay if we don't do them today (skippable).
---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?

I used AI as a second set of "eyes" to help confirm the code or responses were following the corresponding prompt. Also used AI to develop tests and demo data to allow me to do more in depth bug hunting/fine tuning. Further I prompted Claude to inspect if additions were possibly being over-engineered, lack efficiency, or adding no value.

- What kinds of prompts or questions were most helpful?

"Develop a set of Tasks for a Pet which will cause a conflict."
"This logic/set of functions feel too complicated for the task they are assigned, is there a simpler way to achieve the same result?"

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.

Claude wanted to "make sure" the pytest file was able to import the root, so Claude wanted to use a random line of code to "bring in the root".

---

- How did you evaluate or verify what the AI suggested?

When I saw the suggestion, it seemed out of the blue and it was during a time where we were adding several different modules for imports, so I was already trying to make sure we needed them all. Then I pushed back by asking if that line of code was necessary, and Claude agreed it was not.

- Additional thoughts

By using different chats, I was able to move between windows to accomplish multiple steps at the same time. Also this helped with keeping the context of a specific window free of aspects that I didn't want it to have or pay attention to. Designating one chat for pre-coding, design steps allowed me to be able to jump back to that same chat after implementing that original ideas and compare and contrast what we originaly designed and what we implemented. 


## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?

I wrote unit tests covering both the "happy path" and the higher-risk conflict logic:

* **Core task/pet behavior:** `mark_complete()` flips a task's status, and `add_task()` both grows a pet's task list and links the task back to the pet `(pet_assigned)`.
* **Sorting:** Tasks added out of chronological order are returned earliest-to-latest by `sort_by_time()`.
* **Recurrence:** Completing a `daily` task spawns a fresh, uncompleted occurrence dated one day later and re-attaches it to the same pet.
* **Conflict detection:** Two tasks requested at the same time are flagged as overlapping, and the scheduler resolves them onto two distinct slots.
* **Skippable handling:** A skippable task that clashes is *dropped* (lands in `scheduler.skipped`), never nudged, while the non-skippable task keeps its slot.
* **The new prompt/decline flow:** `suggest_free_time()` returns the correct nudged slot to offer the user, returns `None` when nothing fits before end-of-day, and — most importantly — checking for a conflict and computing a suggestion are non-mutating, so **when the user declines, the task is never added** to the pet or owner. I also tested the accept path: the task lands at the suggested time and no longer conflicts.
* **Empty edge case:** An owner with no pets builds an empty schedule without crashing.

- Why were these tests important?

The scheduler's whole promise is a conflict-free timeline, so the conflict, skippable, and suggestion logic are where a bug would do real damage. The decline test specifically protects the guarantee behind my new design — that a rejected suggestion leaves the data unchanged. The sorting, recurrence, and empty-owner tests guard the everyday behavior the UI depends on.

**b. Confidence**

- How confident are you that your scheduler works correctly?

I'm fairly confident the **backend scheduling logic** works correctly: conflict detection is interval-based (it catches overlaps by duration, not just identical start times), and every test passes. My main caveat is that the **accept/decline buttons are Streamlit UI**, which I couldn't unit-test directly — so I tested the backend contract those buttons rely on (`find_conflicts` + `suggest_free_time` + non-mutation) rather than the button clicks themselves

- What edge cases would you test next if you had more time?

* **Frequency expansion:** That a frequency=2/3 task spreads evenly across the day and degrades gracefully when there's no room to spread.
* **Boundary times:** A task starting exactly at `end_of_day`, and a nudge that would push a task's start past the cutoff (→ `unplaced`).
* **Adjacent, non-overlapping tasks:** (9:00–9:30 and 9:30–10:00) — confirming they *don't* falsely conflict.
* **Zero-duration and unknown-priority tasks:** How they rank and whether they conflict.
* **Multi-pet, fully-booked days:** A realistic run where several tasks compete and some legitimately can't fit.
* **An end-to-end UI test** of the accept/decline buttons using a Streamlit testing harness (e.g. `AppTest`).


---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I'm most proud of the conflict resolution and detection that was developed. Especially how it originally evolved from a misunderstanding of how the app was going to interact with the user and then was able to be *shifted* into a workable, useful main aspect of the app.


**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

If I had another iteration, I would redesign the `Scheduler` to support a multi-caretaker model. Right now the schedule represents a single owner's own time, so the app assumes one person is doing every task — which is why two tasks can't overlap and one gets nudged. That works for a personal pet-care app, but if `PawPal+` were a pet-sitting service, multiple caretakers could handle different pets at the same time. To support that I'd add a `Handler` (or C`aretaker`) class and give the scheduler a notion of capacity: instead of rejecting an overlap outright, it would check whether a free handler is available and only conflict/nudge when everyone is busy. This would turn the current one-person assumption into a resource-allocation problem, which is a more realistic and scalable design.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

The biggest takeaway I got from this is how important the overall design of the project is **BEFORE** any coding is done. Desigining the classes on paper, discussing their relationships with each other and questioning those relationships is exremely useful with being able to develop a product. Also, having a strong, solid understanding of what you intend to do with the project is helpful in being able to add features later, improve on existing features or just ovearll expand the project. Without having that solid understanding, you end up asking or trying to implement features that won't go with the overal point of the app. 
