import streamlit as st
from datetime import date
from pawpal_system import Owner, Pet, Scheduler, Task
st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)


with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )
    

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs")

owner_name = st.text_input("Owner name", value="Jordan")

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name)

owner: Owner = st.session_state.owner
owner.name = owner_name

st.markdown("### Add / Select Pet")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])


def _get_pet_by_name(name: str):
    for pet in owner.pets:
        if pet.name == name:
            return pet
    return None


if st.button("Add/Update pet"):
    existing = _get_pet_by_name(pet_name)
    if existing is None:
        owner.add_pet(Pet(name=pet_name, species=species))
        st.success(f"Added pet: {pet_name}")
    else:
        existing.species = species
        st.info(f"Updated pet: {pet_name}")

if owner.pets:
    selected_pet_name = st.selectbox("Assign tasks to", [p.name for p in owner.pets])
    selected_pet = _get_pet_by_name(selected_pet_name)
else:
    selected_pet = None
 

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    pet = selected_pet or _get_pet_by_name(pet_name)
    if pet is None:
        pet = Pet(name=pet_name, species=species)
        owner.add_pet(pet)
        st.info(f"Created pet '{pet_name}' automatically.")

    pet.add_task(
        Task(
            description=task_title,
            duration_minutes=int(duration),
            frequency="once",
            priority=priority,
        )
    )

    st.success(f"Added task to {pet.name}.")

all_tasks_for_table = [
    {
        "pet": pet.name,
        "task": task.description,
        "duration_minutes": task.duration_minutes,
        "priority": task.priority,
        "frequency": task.frequency,
        "completed": task.is_completed,
    }
    for pet in owner.pets
    for task in pet.tasks
]

if all_tasks_for_table:
    st.write("Current tasks:")
    st.table(all_tasks_for_table)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")

time_available = st.number_input(
    "Time available today (minutes)", min_value=1, max_value=480, value=45
)

if st.button("Generate schedule"):
    scheduler = Scheduler(owner)
    plan = scheduler.generate_plan(time_available_minutes=int(time_available), on=date.today())

    st.markdown(f"### Today's Schedule ({date.today().isoformat()})")
    if not plan:
        st.info("No due tasks fit in the available time.")
    else:
        schedule_rows = [
            {
                "pet": pet.name,
                "task": task.description,
                "duration_minutes": task.duration_minutes,
                "priority": task.priority,
                "frequency": task.frequency,
            }
            for pet, task in plan
        ]
        st.table(schedule_rows)

        total = sum(task.duration_minutes for _, task in plan)
        st.write(f"Total scheduled: {total} minutes")
        st.write(f"Unused time: {max(0, int(time_available) - total)} minutes")
