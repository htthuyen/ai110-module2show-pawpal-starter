
from pawpal_system import Pet, Task


def test_task_completion_mark_complete_sets_completed_status():
	# Arrange
	task = Task(description="Morning walk", duration_minutes=20, frequency="daily")
	assert task.is_completed is False

	# Act
	task.mark_complete()

	# Assert
	assert task.is_completed is True
	assert task.last_completed is not None


def test_pet_add_task_increases_task_count():
	# Arrange
	pet = Pet(name="Mochi", species="dog")
	initial_count = len(pet.tasks)

	# Act
	pet.add_task(Task(description="Supplements + food", duration_minutes=10, frequency="daily"))

	# Assert
	assert len(pet.tasks) == initial_count + 1
