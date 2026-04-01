import streamlit as st
from datetime import date
from pawpal_system import Owner, Pet, Scheduler, Task
st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")


owner_name = st.text_input("Owner name", value="Jordan")

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name=owner_name)

owner: Owner = st.session_state.owner
owner.name = owner_name

st.markdown("### Add / Select Pet")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])


def _pairs_to_table_rows(pairs):
    return [
        {
            "pet": pet.name,
            "task": task.description,
            "duration_minutes": task.duration_minutes,
            "priority": task.priority,
            "frequency": task.frequency,
            "completed": task.is_completed,
        }
        for pet, task in pairs
    ]


if st.button("Add/Update pet"):
    existing = owner.get_pet(pet_name)
    if existing is None:
        owner.add_pet(Pet(name=pet_name, species=species))
        st.success(f"Added pet: {pet_name}")
    else:
        existing.species = species
        st.info(f"Updated pet: {pet_name}")

if owner.pets:
    selected_pet_name = st.selectbox("Assign tasks to", [p.name for p in owner.pets])
    selected_pet = owner.get_pet(selected_pet_name)
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
    pet = selected_pet or owner.get_pet(pet_name)
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

scheduler = Scheduler(owner)
all_pairs = scheduler.filter_tasks(on=date.today(), status="all")
all_tasks_for_table = _pairs_to_table_rows(all_pairs)

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
            for pet, task in scheduler.organize_by_priority(plan)
        ]
        st.table(schedule_rows)

        total = sum(task.duration_minutes for _, task in plan)
        st.write(f"Total scheduled: {total} minutes")
        st.write(f"Unused time: {max(0, int(time_available) - total)} minutes")
