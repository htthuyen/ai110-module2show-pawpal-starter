
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time
from typing import Any, Dict, List, Optional


@dataclass
class Task:
	"""A pet care task such as walking, feeding, or a vet appointment."""

	title: str
	category: str = "general"
	duration_minutes: int = 0
	priority: str = "medium"  # low | medium | high

	def send_notification(self, owner: User) -> str:
		"""Placeholder for notification logic (email/push/in-app)."""

		return f"Reminder for {owner.name}: {self.title}"


@dataclass
class Pet:
	"""A pet owned by a user, with a list of care tasks."""

	name: str
	species: str
	tasks: List[Task] = field(default_factory=list)

	def add_task(self, task: Task) -> None:
		self.tasks.append(task)


@dataclass
class ScheduledTask:
	"""A Task placed on a schedule (optionally with a start time)."""

	task: Task
	start_time: Optional[time] = None
	rationale: str = ""


@dataclass
class Schedule:
	"""A daily plan produced by the scheduler."""

	day: date
	items: List[ScheduledTask] = field(default_factory=list)
	explanation: str = ""

	def total_minutes(self) -> int:
		return sum(item.task.duration_minutes for item in self.items)


class User:
	"""A pet owner who can manage pets, tasks, and build a daily schedule."""

	def __init__(self, name: str, preferences: Optional[Dict[str, Any]] = None):
		self.name = name
		self.pets: List[Pet] = []
		self.preferences: Dict[str, Any] = preferences or {}

	def add_pet(self, pet: Pet) -> None:
		self.pets.append(pet)

	def create_task(self, pet: Pet, task: Task) -> None:
		"""Add a task to a specific pet."""

		pet.add_task(task)

	def create_schedule(self, day: date, time_available_minutes: int) -> Schedule:
		"""Create a schedule for a given day.

		Skeleton only: this currently returns an empty plan. Implement your
		scheduling logic here (priorities, constraints, preferences, etc.).
		"""

		_ = time_available_minutes
		return Schedule(day=day)

	def explain_schedule(self, schedule: Schedule) -> str:
		"""Human-readable explanation for a produced schedule."""

		if schedule.explanation:
			return schedule.explanation
		return "Scheduling explanation not implemented yet."

