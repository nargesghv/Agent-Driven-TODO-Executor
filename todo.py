"""
List and Task Management
"""
from typing import List, Dict, Any, Optional
from enum import Enum
from colorama import Fore, Style


class TaskStatus(Enum):
    """Task status states"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    FAILED = "failed"
    NEEDS_FOLLOW_UP = "needs-follow-up"


class Task:
    """
    Represents a single task 
    """
    
    def __init__(self, task_id: int, title: str, description: str, status: str = "pending",
                 phase: str = "development", reasoning: str = ""):
        self.id = task_id
        self.title = title
        self.description = description
        self.status = TaskStatus(status)
        self.phase = phase  # planning, development, testing, deployment
        self.reasoning = reasoning  # Why this task matters
        self.result: Optional[Dict[str, Any]] = None
    
    def update_status(self, new_status: TaskStatus):
        """Update task status"""
        self.status = new_status
    
    def set_result(self, result: Dict[str, Any]):
        """Store execution result"""
        self.result = result
        # Update status based on result
        if result.get("status"):
            self.status = TaskStatus(result["status"])
    
    def is_terminal(self) -> bool:
        """Check if task has reached a terminal state"""
        return self.status in [TaskStatus.DONE, TaskStatus.FAILED]
    
    def __repr__(self):
        return f"Task({self.id}, {self.title}, {self.status.value})"


class TodoList:
    """
    Manages the complete TODO list
    """
    
    def __init__(self):
        self.tasks: List[Task] = []
    
    def load_from_dict(self, tasks_data: List[Dict[str, Any]]):
        """Load tasks from dictionary (from LLM response)"""
        self.tasks = []
        for task_data in tasks_data:
            task = Task(
                task_id=task_data.get("id", len(self.tasks) + 1),
                title=task_data.get("title", ""),
                description=task_data.get("description", ""),
                status=task_data.get("status", "pending"),
                phase=task_data.get("phase", "development"),
                reasoning=task_data.get("reasoning", "")
            )
            self.tasks.append(task)
    
    def get_next_task(self) -> Optional[Task]:
        """Get the first unfinished task (FIFO policy)"""
        for task in self.tasks:
            if task.status == TaskStatus.PENDING:
                return task
        return None
    
    def all_tasks_terminal(self) -> bool:
        """Check if all tasks are in terminal state"""
        return all(task.is_terminal() for task in self.tasks)
    
    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """Get task by ID"""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def display(self):
        """Display the TODO list with nice formatting"""
        print(f"\n{Fore.CYAN}{'═' * 60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN} To-dos {len(self.tasks)}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'═' * 60}{Style.RESET_ALL}\n")
        
        # Group by phase for better organization
        phases = {}
        for task in self.tasks:
            phase = task.phase
            if phase not in phases:
                phases[phase] = []
            phases[phase].append(task)
        
        # Display by phase with task numbers
        phase_order = ["planning", "development", "testing", "deployment"]
        phase_icons = {
            "planning": "📐",
            "development": "💻",
            "testing": "🧪",
            "deployment": "🚀"
        }
        
        for phase in phase_order:
            if phase not in phases:
                continue
                
            print(f"{Fore.CYAN}{phase_icons.get(phase, '📌')} {phase.upper()}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'─' * 60}{Style.RESET_ALL}")
            
            for task in phases[phase]:
                # Status icon
                if task.status == TaskStatus.DONE:
                    icon = f"{Fore.GREEN}✅{Style.RESET_ALL}"
                elif task.status == TaskStatus.FAILED:
                    icon = f"{Fore.RED}❌{Style.RESET_ALL}"
                elif task.status == TaskStatus.IN_PROGRESS:
                    icon = f"{Fore.YELLOW}⚙️{Style.RESET_ALL}"
                elif task.status == TaskStatus.NEEDS_FOLLOW_UP:
                    icon = f"{Fore.MAGENTA}🔄{Style.RESET_ALL}"
                else:
                    icon = f"{Fore.WHITE}○{Style.RESET_ALL}"
                
                # Show task ID prominently
                print(f"{icon} {Fore.YELLOW}[#{task.id}]{Style.RESET_ALL} {Fore.WHITE}{task.title}{Style.RESET_ALL}")
                if task.description:
                    # Wrap description nicely
                    desc_lines = task.description.split('. ')
                    for line in desc_lines:
                        if line:
                            print(f"   {Fore.LIGHTBLACK_EX}{line.strip()}{Style.RESET_ALL}")
                print()
        
        print(f"{Fore.CYAN}{'═' * 60}{Style.RESET_ALL}\n")
    
    def get_summary(self) -> Dict[str, int]:
        """Get summary of task statuses"""
        summary = {
            "total": len(self.tasks),
            "pending": 0,
            "in_progress": 0,
            "done": 0,
            "failed": 0,
            "needs_follow_up": 0
        }
        
        for task in self.tasks:
            if task.status == TaskStatus.PENDING:
                summary["pending"] += 1
            elif task.status == TaskStatus.IN_PROGRESS:
                summary["in_progress"] += 1
            elif task.status == TaskStatus.DONE:
                summary["done"] += 1
            elif task.status == TaskStatus.FAILED:
                summary["failed"] += 1
            elif task.status == TaskStatus.NEEDS_FOLLOW_UP:
                summary["needs_follow_up"] += 1
        
        return summary

