```mermaid
classDiagram
direction LR

class Owner {
    +name: str
    +pets: List~Pet~
    +add_pet(pet: Pet) void
    +remove_pet(pet: Pet) void
    +all_tasks() List~Task~
    +all_tasks_with_pet() List~Tuple~Pet, Task~~
    +get_pet(name: str) Pet?
}

class Pet {
    +name: str
    +species: str
    +tasks: List~Task~
    +add_task(task: Task) void
    +remove_task(task: Task) void
    +pending_tasks(on: date?) List~Task~
}

class Task {
    +description: str
    +duration_minutes: int
    +frequency: Frequency
    +priority: Priority
    +is_completed: bool
    +last_completed: date?
    +due_on: date?
    +preferred_start_time: time?
    +fixed_time: bool
    +mark_complete(completed_on: date?) void
    +mark_incomplete() void
    +is_due(on: date?) bool
    +is_completed_on(on: date?) bool
    +priority_rank() int
}

class Scheduler {
    +owner: Owner
    +get_due_tasks(on: date?) List~Tuple~Pet, Task~~
    +filter_tasks(on: date?, pet: Pet?, pet_name: str?, status: TaskStatus) List~Tuple~Pet, Task~~
    +organize_by_pet(tasks: Iterable~Tuple~Pet, Task~~~) Dict~str, List~Task~~
    +organize_by_priority(tasks: Iterable~Tuple~Pet, Task~~~) List~Tuple~Pet, Task~~
    +generate_plan(time_available_minutes: int, on: date?) List~Tuple~Pet, Task~~
    +generate_timed_plan(time_available_minutes: int, on: date?, day_start: time) Tuple~List~ScheduleEntry~, List~ScheduleConflict~~
    +mark_task_completed(pet: Pet, task: Task, completed_on: date?) void
}

class ScheduleEntry {
    +pet: Pet
    +task: Task
    +start: datetime
    +end: datetime
}

class ScheduleConflict {
    +first: ScheduleEntry
    +second: ScheduleEntry
    +reason: str
}

class "Priority" as Priority
<<type>> Priority

class "Frequency" as Frequency
<<type>> Frequency

class "TaskStatus" as TaskStatus
<<type>> TaskStatus

Owner "1" o-- "0..*" Pet : owns
Pet "1" o-- "0..*" Task : needs
Scheduler "1" --> "1" Owner : owner
Scheduler "1" ..> "0..*" ScheduleEntry : generates
Scheduler "1" ..> "0..*" ScheduleConflict : detects
ScheduleEntry "*" --> "1" Pet
ScheduleEntry "*" --> "1" Task
ScheduleConflict "*" --> "1" ScheduleEntry : first
ScheduleConflict "*" --> "1" ScheduleEntry : second
```