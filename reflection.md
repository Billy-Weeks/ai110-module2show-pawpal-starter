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
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
