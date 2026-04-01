from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Dict, Iterable, List, Literal, Optional, Tuple

Priority = Literal["low", "medium", "high"]
Frequency = Literal["once", "daily", "weekly", "monthly"]


@dataclass
class Task:
	"""Represents a single pet-care activity."""

	description: str
	duration_minutes: int
	frequency: Frequency = "once"
	priority: Priority = "medium"
	is_completed: bool = False
	last_completed: Optional[date] = None

	def mark_complete(self, completed_on: Optional[date] = None) -> None:
		self.is_completed = True
		self.last_completed = completed_on or date.today()

	def mark_completed(self, completed_on: Optional[date] = None) -> None:
		"""Alias for `mark_complete()` (common naming)."""

		self.mark_complete(completed_on=completed_on)

	def mark_incomplete(self) -> None:
		self.is_completed = False

	def is_due(self, on: Optional[date] = None) -> bool:
		"""Simple due-ness check based on frequency and last completion."""

		on = on or date.today()
		if self.frequency == "once":
			return not self.is_completed

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
		task.mark_complete(completed_on=completed_on)

