# PawPal+ Project Reflection

## 1. System Design


A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

**a. Initial design**

- Briefly describe your initial UML design.
    - A pet assistant app should have core functions such as user and pet info, task listings, task reminders, calendar for scheduling, etc. 
    - An app will allow user to prioritize tasks, set preferences, and make changes on task schedules
    - An app will alert users essential pet care, hold pet care history, and recommend prioritized task
- What classes did you include, and what responsibilities did you assign to each?
    - User Class 
        - Add pet info
        - create schedule
        - create task
    - Pet Class
        - Pet info
    - Task Class
        - walking
        - annual check-up
        - supplement + food
        - send notification to the pet owner



**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
    - I have made some design changes during implementattion. The initial design was missing the owner relationhip user and pet. Therefore, I asjusted and modified the code to ensure the pet needed to be tied with their owner. I also added pet to schedule so schedule items can be linked with a specific pet. 

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
    - I used copilot-agent to generate classes from UML, perform refactoring, and write test cases
- What kinds of prompts or questions were most helpful?
    - The most helpful prompts were specific, context-rich, and goal-oriented. I described the problem clearly along with specific lines of code or files and then asked targeted questions. 

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
    - AI generated a redundant function, so I didn't accept it
- How did you evaluate or verify what the AI suggested?
    - I verified by going through the codes and reviewed what AI suggested
---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
    - I tested the schedule conflicts, task additions, task completions
- Why were these tests important?
    - Those are core functions of the application. 
**b. Confidence**

- How confident are you that your scheduler works correctly?
    - I have high confidence that the scheduler works correctly
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
    - The UML design. With AI, I saved a lot of time on sketching UML diagram

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
    - I would make the UI more poslished

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
    - Knowing how to use AI to generate test cases is extremely helpful on this project