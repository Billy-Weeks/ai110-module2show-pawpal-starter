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
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

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
