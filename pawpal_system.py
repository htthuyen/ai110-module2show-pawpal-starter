from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from typing import Dict, Iterable, List, Literal, Optional, Tuple

Priority = Literal["low", "medium", "high"]
Frequency = Literal["once", "daily", "weekly", "monthly"]
TaskStatus = Literal["all", "due", "completed", "incomplete"]


def _combine(on: date, at: time) -> datetime:
	return datetime.combine(on, at)


@dataclass(frozen=True)
class ScheduleEntry:
	pet: Pet
	task: Task
	start: datetime
	end: datetime


@dataclass(frozen=True)
class ScheduleConflict:
	first: ScheduleEntry
	second: ScheduleEntry
	reason: str


@dataclass
class Task:
	"""Represents a single pet-care activity."""

	description: str
	duration_minutes: int
	frequency: Frequency = "once"
	priority: Priority = "medium"
	is_completed: bool = False
	last_completed: Optional[date] = None
	# If set, this task instance represents a specific occurrence due on this date.
	# This supports “spawn a new instance for the next occurrence” for recurring tasks.
	due_on: Optional[date] = None
	preferred_start_time: Optional[time] = None
	fixed_time: bool = False

	def mark_complete(self, completed_on: Optional[date] = None) -> None:
		self.is_completed = True
		self.last_completed = completed_on or date.today()

	def mark_incomplete(self) -> None:
		self.is_completed = False

	def is_due(self, on: Optional[date] = None) -> bool:
		"""Simple due-ness check based on frequency and last completion."""

		on = on or date.today()
		if self.frequency == "once":
			return not self.is_completed

		# Occurrence-based recurring task.
		if self.due_on is not None:
			return (not self.is_completed) and (on >= self.due_on)

		if self.last_completed is None:
			return True

		days_since = (on - self.last_completed).days
		if self.frequency == "daily":
			return days_since >= 1
		if self.frequency == "weekly":
			return days_since >= 7
		if self.frequency == "monthly":
			return days_since >= 30
		return True

	def is_completed_on(self, on: Optional[date] = None) -> bool:
		"""Completion status for a specific day.

		- For one-time tasks: uses `is_completed`.
		- For recurring tasks: treated as completed if last_completed == on.
		"""

		on = on or date.today()
		if self.frequency == "once":
			return self.is_completed
		return self.last_completed == on

	def priority_rank(self) -> int:
		return {"high": 3, "medium": 2, "low": 1}[self.priority]


@dataclass
class Pet:
	"""Stores pet details and a list of tasks."""

	name: str
	species: str
	tasks: List[Task] = field(default_factory=list)

	def add_task(self, task: Task) -> None:
		self.tasks.append(task)

	def remove_task(self, task: Task) -> None:
		self.tasks.remove(task)

	def pending_tasks(self, on: Optional[date] = None) -> List[Task]:
		return [t for t in self.tasks if t.is_due(on=on)]


@dataclass
class Owner:
	"""Manages multiple pets and provides access to all their tasks."""

	name: str
	pets: List[Pet] = field(default_factory=list)

	def add_pet(self, pet: Pet) -> None:
		self.pets.append(pet)

	def remove_pet(self, pet: Pet) -> None:
		self.pets.remove(pet)

	def all_tasks(self) -> List[Task]:
		return [task for pet in self.pets for task in pet.tasks]

	def all_tasks_with_pet(self) -> List[Tuple[Pet, Task]]:
		return [(pet, task) for pet in self.pets for task in pet.tasks]

	def get_pet(self, name: str) -> Optional[Pet]:
		for pet in self.pets:
			if pet.name == name:
				return pet
		return None


class Scheduler:
	"""The “brain” that retrieves, organizes, and manages tasks across pets."""

	def __init__(self, owner: Owner):
		self.owner = owner

	def get_due_tasks(self, on: Optional[date] = None) -> List[Tuple[Pet, Task]]:
		on = on or date.today()
		due: List[Tuple[Pet, Task]] = []
		for pet in self.owner.pets:
			for task in pet.tasks:
				if task.is_due(on=on):
					due.append((pet, task))
		return due

	def filter_tasks(
		self,
		on: Optional[date] = None,
		pet: Optional[Pet] = None,
		pet_name: Optional[str] = None,
		status: TaskStatus = "all",
	) -> List[Tuple[Pet, Task]]:
		"""Filter tasks by pet and/or status.

		Status is computed for the given date:
		- due: task.is_due(on)
		- completed: task.is_completed_on(on)
		- incomplete: not task.is_completed_on(on)
		"""

		on = on or date.today()
		if pet is not None and pet_name is not None:
			raise ValueError("Provide either pet or pet_name, not both.")
		if pet is None and pet_name is not None:
			pet = self.owner.get_pet(pet_name)

		pairs: Iterable[Tuple[Pet, Task]]
		if pet is None:
			pairs = self.owner.all_tasks_with_pet()
		else:
			pairs = [(pet, task) for task in pet.tasks]

		results: List[Tuple[Pet, Task]] = []
		for p, task in pairs:
			if status == "all":
				results.append((p, task))
			elif status == "due" and task.is_due(on=on):
				results.append((p, task))
			elif status == "completed" and task.is_completed_on(on=on):
				results.append((p, task))
			elif status == "incomplete" and not task.is_completed_on(on=on):
				results.append((p, task))
		return results

	def organize_by_pet(self, tasks: Optional[Iterable[Tuple[Pet, Task]]] = None) -> Dict[str, List[Task]]:
		tasks = list(tasks) if tasks is not None else self.get_due_tasks()
		organized: Dict[str, List[Task]] = {}
		for pet, task in tasks:
			organized.setdefault(pet.name, []).append(task)
		return organized

	def organize_by_priority(
		self, tasks: Optional[Iterable[Tuple[Pet, Task]]] = None
	) -> List[Tuple[Pet, Task]]:
		tasks = list(tasks) if tasks is not None else self.get_due_tasks()
		return sorted(
			tasks,
			key=lambda pt: (
				-pt[1].priority_rank(),
				pt[1].duration_minutes,
				pt[0].name,
				pt[1].description,
			),
		)

	def sort_schedule_by_time(self, entries: Iterable[ScheduleEntry]) -> List[ScheduleEntry]:
		return sorted(entries, key=lambda e: (e.start, e.end, e.pet.name, e.task.description))

	def detect_conflicts(self, entries: Iterable[ScheduleEntry]) -> List[ScheduleConflict]:
		sorted_entries = self.sort_schedule_by_time(entries)
		conflicts: List[ScheduleConflict] = []
		for left, right in zip(sorted_entries, sorted_entries[1:]):
			if right.start < left.end:
				conflicts.append(
					ScheduleConflict(
						first=left,
						second=right,
						reason="Overlapping scheduled times.",
					)
				)
		return conflicts

	def _split_fixed_and_flex(
		self, due: Iterable[Tuple[Pet, Task]]
	) -> Tuple[List[Tuple[Pet, Task]], List[Tuple[Pet, Task]]]:
		fixed: List[Tuple[Pet, Task]] = []
		flex: List[Tuple[Pet, Task]] = []
		for pet, task in due:
			if task.fixed_time and task.preferred_start_time is not None:
				fixed.append((pet, task))
			else:
				flex.append((pet, task))
		return fixed, flex

	def _build_fixed_entries(
		self,
		fixed_pairs: Iterable[Tuple[Pet, Task]],
		on: date,
		window_start: datetime,
		window_end: datetime,
	) -> List[ScheduleEntry]:
		entries: List[ScheduleEntry] = []
		for pet, task in fixed_pairs:
			start = _combine(on, task.preferred_start_time)  # type: ignore[arg-type]
			end = start + timedelta(minutes=int(task.duration_minutes))
			if start < window_start or end > window_end:
				# Skip invalid fixed tasks rather than crashing.
				continue
			entries.append(ScheduleEntry(pet=pet, task=task, start=start, end=end))
		return self.sort_schedule_by_time(entries)

	def _gaps_from_entries(
		self,
		entries: Iterable[ScheduleEntry],
		window_start: datetime,
		window_end: datetime,
	) -> List[Tuple[datetime, datetime]]:
		gaps: List[Tuple[datetime, datetime]] = []
		cursor = window_start
		for entry in self.sort_schedule_by_time(entries):
			if cursor < entry.start:
				gaps.append((cursor, entry.start))
			cursor = max(cursor, entry.end)
		if cursor < window_end:
			gaps.append((cursor, window_end))
		return gaps

	def _split_gap(
		self,
		gap: Tuple[datetime, datetime],
		start: datetime,
		end: datetime,
	) -> List[Tuple[datetime, datetime]]:
		gap_start, gap_end = gap
		new_gaps: List[Tuple[datetime, datetime]] = []
		if gap_start < start:
			new_gaps.append((gap_start, start))
		if end < gap_end:
			new_gaps.append((end, gap_end))
		return new_gaps

	def _try_place_in_gaps(
		self,
		pet: Pet,
		task: Task,
		on: date,
		gaps: List[Tuple[datetime, datetime]],
	) -> Tuple[Optional[ScheduleEntry], List[Tuple[datetime, datetime]]]:
		duration = timedelta(minutes=int(task.duration_minutes))
		for idx, gap in enumerate(gaps):
			gap_start, gap_end = gap
			start = gap_start
			if task.preferred_start_time is not None:
				preferred = _combine(on, task.preferred_start_time)
				start = max(start, preferred)
			end = start + duration
			if end <= gap_end:
				entry = ScheduleEntry(pet=pet, task=task, start=start, end=end)
				new_gaps = gaps[:idx] + self._split_gap(gap, start, end) + gaps[idx + 1 :]
				return entry, new_gaps
		return None, gaps

	def generate_timed_plan(
		self,
		time_available_minutes: int,
		on: Optional[date] = None,
		day_start: time = time(8, 0),
	) -> Tuple[List[ScheduleEntry], List[ScheduleConflict]]:
		"""Generate a time-ordered daily schedule with basic conflict detection.

		Rules:
		- Fixed-time tasks (`fixed_time=True` and `preferred_start_time` set) are placed first.
		- Remaining tasks are placed greedily by priority into the earliest available gaps.
		- Schedule window is [day_start, day_start + time_available_minutes].
		"""

		on = on or date.today()
		window_start = _combine(on, day_start)
		window_end = window_start + timedelta(minutes=int(time_available_minutes))

		due = self.get_due_tasks(on=on)
		fixed_pairs, flex_pairs = self._split_fixed_and_flex(due)

		entries = self._build_fixed_entries(
			fixed_pairs=fixed_pairs,
			on=on,
			window_start=window_start,
			window_end=window_end,
		)

		conflicts = self.detect_conflicts(entries)
		if conflicts:
			# Return conflicts as warnings rather than crashing.
			return entries, conflicts

		gaps = self._gaps_from_entries(entries, window_start=window_start, window_end=window_end)
		for pet, task in self.organize_by_priority(flex_pairs):
			entry, gaps = self._try_place_in_gaps(pet=pet, task=task, on=on, gaps=gaps)
			if entry is not None:
				entries.append(entry)

		entries = self.sort_schedule_by_time(entries)
		conflicts = self.detect_conflicts(entries)
		return entries, conflicts

	def generate_plan(
		self, time_available_minutes: int, on: Optional[date] = None
	) -> List[Tuple[Pet, Task]]:
		"""Greedy plan: prioritize high-priority tasks within a time budget."""

		remaining = time_available_minutes
		plan: List[Tuple[Pet, Task]] = []
		for pet, task in self.organize_by_priority(self.get_due_tasks(on=on)):
			if task.duration_minutes <= remaining:
				plan.append((pet, task))
				remaining -= task.duration_minutes
		return plan

	def mark_task_completed(self, pet: Pet, task: Task, completed_on: Optional[date] = None) -> None:
		if pet not in self.owner.pets:
			raise ValueError("Pet must belong to owner.")
		if task not in pet.tasks:
			raise ValueError("Task must belong to pet.")
		completed_on = completed_on or date.today()
		# Idempotency: avoid spawning duplicates if already completed for this date.
		if task.is_completed and task.last_completed == completed_on:
			return

		# If a recurring task doesn't have an explicit occurrence date yet, treat this
		# completion as the current occurrence and lock it to that day.
		if task.frequency in ("daily", "weekly") and task.due_on is None:
			task.due_on = completed_on

		task.mark_complete(completed_on=completed_on)

		if task.frequency not in ("daily", "weekly"):
			return

		delta = timedelta(days=1 if task.frequency == "daily" else 7)
		base = task.due_on or completed_on
		next_due = base + delta
		pet.add_task(
			Task(
				description=task.description,
				duration_minutes=task.duration_minutes,
				frequency=task.frequency,
				priority=task.priority,
				is_completed=False,
				last_completed=None,
				due_on=next_due,
				preferred_start_time=task.preferred_start_time,
				fixed_time=task.fixed_time,
			)
		)

