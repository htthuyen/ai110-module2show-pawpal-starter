from datetime import date, time, timedelta

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task


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


def test_daily_task_due_again_after_yesterday_completion():
	today = date.today()
	yesterday = today - timedelta(days=1)
	task = Task(description="Meds", duration_minutes=5, frequency="daily")
	task.mark_complete(completed_on=yesterday)

	assert task.is_due(on=today) is True
	assert task.is_completed_on(on=today) is False
	assert task.is_completed_on(on=yesterday) is True


def test_scheduler_filter_by_pet_and_status_due():
	today = date.today()
	owner = Owner(name="Jordan")
	mochi = Pet(name="Mochi", species="dog")
	luna = Pet(name="Luna", species="cat")
	owner.add_pet(mochi)
	owner.add_pet(luna)

	mochi_task = Task(description="Walk", duration_minutes=20, frequency="daily")
	luna_task = Task(description="Litter", duration_minutes=10, frequency="daily")
	mochi.add_task(mochi_task)
	luna.add_task(luna_task)

	# Complete Luna's task today; Mochi's is still due.
	luna_task.mark_complete(completed_on=today)

	scheduler = Scheduler(owner)
	mochi_due = scheduler.filter_tasks(on=today, pet_name="Mochi", status="due")
	assert mochi_due == [(mochi, mochi_task)]

	luna_due = scheduler.filter_tasks(on=today, pet=luna, status="due")
	assert luna_due == []


def test_generate_timed_plan_is_sorted_and_respects_fixed_time():
	today = date.today()
	owner = Owner(name="Jordan")
	mochi = Pet(name="Mochi", species="dog")
	owner.add_pet(mochi)

	# Fixed at 9:00, should appear after any flexible tasks scheduled at 8:00.
	fixed = Task(
		description="Vet call",
		duration_minutes=30,
		frequency="once",
		priority="high",
		preferred_start_time=time(9, 0),
		fixed_time=True,
	)
	flex = Task(description="Walk", duration_minutes=20, frequency="once", priority="high")
	mochi.add_task(fixed)
	mochi.add_task(flex)

	scheduler = Scheduler(owner)
	entries, conflicts = scheduler.generate_timed_plan(time_available_minutes=120, on=today, day_start=time(8, 0))
	assert conflicts == []
	assert [e.task.description for e in entries] == ["Walk", "Vet call"]
	assert entries[0].start.time() == time(8, 0)
	assert entries[1].start.time() == time(9, 0)
	assert entries[0].end <= entries[1].start


def test_generate_timed_plan_returns_conflicts_on_fixed_time_conflict():
	today = date.today()
	owner = Owner(name="Jordan")
	mochi = Pet(name="Mochi", species="dog")
	owner.add_pet(mochi)

	t1 = Task(
		description="Task 1",
		duration_minutes=30,
		frequency="once",
		priority="high",
		preferred_start_time=time(9, 0),
		fixed_time=True,
	)
	t2 = Task(
		description="Task 2",
		duration_minutes=30,
		frequency="once",
		priority="high",
		preferred_start_time=time(9, 15),
		fixed_time=True,
	)
	mochi.add_task(t1)
	mochi.add_task(t2)

	scheduler = Scheduler(owner)
	entries, conflicts = scheduler.generate_timed_plan(time_available_minutes=180, on=today, day_start=time(8, 0))
	assert len(entries) == 2
	assert len(conflicts) >= 1


def test_mark_task_completed_spawns_next_daily_occurrence():
	today = date.today()
	owner = Owner(name="Jordan")
	pet = Pet(name="Mochi", species="dog")
	owner.add_pet(pet)

	task = Task(description="Supplements", duration_minutes=5, frequency="daily", priority="high")
	pet.add_task(task)
	scheduler = Scheduler(owner)

	scheduler.mark_task_completed(pet, task, completed_on=today)

	assert task.is_completed is True
	assert task.due_on == today
	assert len(pet.tasks) == 2
	spawned = pet.tasks[-1]
	assert spawned is not task
	assert spawned.description == task.description
	assert spawned.frequency == "daily"
	assert spawned.is_completed is False
	assert spawned.due_on == today + timedelta(days=1)


def test_mark_task_completed_spawns_next_weekly_occurrence():
	today = date.today()
	owner = Owner(name="Jordan")
	pet = Pet(name="Luna", species="cat")
	owner.add_pet(pet)

	task = Task(description="Brush coat", duration_minutes=15, frequency="weekly", priority="medium")
	pet.add_task(task)
	scheduler = Scheduler(owner)

	scheduler.mark_task_completed(pet, task, completed_on=today)

	assert len(pet.tasks) == 2
	spawned = pet.tasks[-1]
	assert spawned.frequency == "weekly"
	assert spawned.due_on == today + timedelta(days=7)


def test_generate_timed_plan_returns_entries_in_chronological_order():
	today = date.today()
	owner = Owner(name="Jordan")
	pet = Pet(name="Mochi", species="dog")
	owner.add_pet(pet)

	# Fixed task that creates a gap boundary.
	fixed = Task(
		description="Vet call",
		duration_minutes=30,
		frequency="once",
		priority="high",
		preferred_start_time=time(9, 0),
		fixed_time=True,
	)

	# Two flexible tasks; at least one should land before the fixed task.
	flex_short = Task(description="Quick walk", duration_minutes=45, frequency="once", priority="high")
	flex_long = Task(description="Grooming", duration_minutes=60, frequency="once", priority="high")

	pet.add_task(fixed)
	pet.add_task(flex_short)
	pet.add_task(flex_long)

	scheduler = Scheduler(owner)
	entries, conflicts = scheduler.generate_timed_plan(
		time_available_minutes=240,
		on=today,
		day_start=time(8, 0),
	)
	assert conflicts == []

	# Chronological order (non-decreasing starts) and no overlaps.
	assert [e.start for e in entries] == sorted(e.start for e in entries)
	for left, right in zip(entries, entries[1:]):
		assert left.end <= right.start

	# Fixed task is anchored at its preferred time.
	vet = next(e for e in entries if e.task.description == "Vet call")
	assert vet.start.time() == time(9, 0)


def test_generate_timed_plan_flags_duplicate_fixed_start_times():
	today = date.today()
	owner = Owner(name="Jordan")
	pet = Pet(name="Mochi", species="dog")
	owner.add_pet(pet)

	# Duplicate fixed start time should be flagged as a conflict.
	t1 = Task(
		description="Task 1",
		duration_minutes=15,
		frequency="once",
		priority="high",
		preferred_start_time=time(9, 0),
		fixed_time=True,
	)
	t2 = Task(
		description="Task 2",
		duration_minutes=30,
		frequency="once",
		priority="high",
		preferred_start_time=time(9, 0),
		fixed_time=True,
	)
	pet.add_task(t1)
	pet.add_task(t2)

	scheduler = Scheduler(owner)
	entries, conflicts = scheduler.generate_timed_plan(time_available_minutes=180, on=today, day_start=time(8, 0))

	assert len(entries) == 2
	assert len(conflicts) >= 1
	assert any(c.first.start.time() == time(9, 0) and c.second.start.time() == time(9, 0) for c in conflicts)
