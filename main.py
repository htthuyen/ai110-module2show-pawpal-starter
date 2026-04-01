
from datetime import date

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
	# Create an owner and two pets
	owner = Owner(name="Jordan")
	mochi = Pet(name="Mochi", species="dog")
	luna = Pet(name="Luna", species="cat")
	owner.add_pet(mochi)
	owner.add_pet(luna)

	# Add at least three tasks with different times (durations)
	mochi.add_task(Task(description="Morning walk", duration_minutes=20, frequency="daily", priority="high"))
	mochi.add_task(Task(description="Supplements + food", duration_minutes=10, frequency="daily", priority="high"))
	mochi.add_task(Task(description="Brush coat", duration_minutes=15, frequency="weekly", priority="medium"))

	luna.add_task(Task(description="Clean litter box", duration_minutes=8, frequency="daily", priority="high"))
	luna.add_task(Task(description="Playtime (wand toy)", duration_minutes=12, frequency="daily", priority="medium"))

	# Generate and print today's schedule
	today = date.today()
	scheduler = Scheduler(owner)
	time_budget = 45
	plan = scheduler.generate_plan(time_available_minutes=time_budget, on=today)

	print(f"Today's Schedule ({today.isoformat()})")
	print("=" * 32)
	print(f"Owner: {owner.name}")
	print(f"Time available: {time_budget} minutes")
	print()

	if not plan:
		print("No tasks scheduled.")
		return

	total = 0
	for idx, (pet, task) in enumerate(plan, start=1):
		total += task.duration_minutes
		print(
			f"{idx}. [{pet.name} ({pet.species})] {task.description} "
			f"— {task.duration_minutes} min — priority: {task.priority} — freq: {task.frequency}"
		)

	print()
	print(f"Total scheduled: {total} minutes")
	print(f"Unused time: {max(0, time_budget - total)} minutes")


if __name__ == "__main__":
	main()
