"""
Main Agent Loop 
"""
from typing import Optional, List, Dict, Any
from colorama import Fore, Style, init
from llm import LLMInterface
from todo import TodoList, Task, TaskStatus
from tools import AgentTools


init(autoreset=True)


class Agent:
    """
    The main agent that handles the complete workflow:
    1. Chat with user about goal
    2. Generate TODO list
    3. Get mode selection (Confirm/Auto)
    4. Execute tasks with logging
    """
    
    def __init__(self):
        self.llm = LLMInterface()
        self.todo_list = TodoList()
        self.tools = AgentTools()
        self.mode: Optional[str] = None  
        self.user_expertise: str = "intermediate"  
        self.clarifications: List[Dict[str, str]] = [] 
    
    def print_header(self, text: str, color=Fore.CYAN):
        """Print a nice header"""
        print(f"\n{color}{'═' * 60}{Style.RESET_ALL}")
        print(f"{color}{text}{Style.RESET_ALL}")
        print(f"{color}{'═' * 60}{Style.RESET_ALL}\n")
    
    def print_log(self, icon: str, message: str, color=Fore.WHITE):
        """Print a log message with icon"""
        print(f"{color}{icon} {message}{Style.RESET_ALL}")
    
    def get_user_goal(self) -> str:
        """
        Get the high-level goal from user with expertise detection
        
        Returns:
            User's goal as string
        """
        self.print_header("🤖 Agent-Driven TODO Executor", Fore.CYAN)
        print(f"{Fore.YELLOW}Welcome! I'll help you break down your goal into tasks and execute them.{Style.RESET_ALL}\n")
        
        # Ask about expertise level for adaptive detail
        print(f"{Fore.CYAN} First, let me understand your experience level:{Style.RESET_ALL}\n")
        print(f"{Fore.WHITE}1. {Fore.LIGHTBLUE_EX}Beginner{Style.RESET_ALL} - I need detailed, step-by-step guidance")
        print(f"{Fore.WHITE}2. {Fore.LIGHTCYAN_EX}Intermediate{Style.RESET_ALL} - I have some technical knowledge")
        print(f"{Fore.WHITE}3. {Fore.LIGHTGREEN_EX}Expert{Style.RESET_ALL} - I'm experienced, just show high-level tasks\n")
        
        while True:
            expertise = input(f"{Fore.GREEN}Your level (1-3, or Enter for 2): {Style.RESET_ALL}").strip()
            if not expertise:
                expertise = "2"
            if expertise in ["1", "2", "3"]:
                self.user_expertise = {"1": "beginner", "2": "intermediate", "3": "expert"}[expertise]
                break
            print(f"{Fore.RED}Please enter 1, 2, or 3{Style.RESET_ALL}")
        
        print(f"\n{Fore.GREEN}✓ Got it! I'll tailor tasks for {self.user_expertise} level.{Style.RESET_ALL}\n")
        
        goal = input(f"{Fore.GREEN}What would you like to achieve? {Style.RESET_ALL}\n> ")
        return goal.strip()
    
    def select_mode(self) -> str:
        """
        Let user choose execution mode before generating list
        
        Returns:
            Selected mode: "confirm" or "auto"
        """
        self.print_header("Select Execution Mode", Fore.MAGENTA)
        print(f"{Fore.YELLOW}Choose how you want to proceed:{Style.RESET_ALL}\n")
        print(f"{Fore.WHITE}1. {Fore.CYAN}CONFIRM MODE{Style.RESET_ALL} - Review and approve TODO list before execution")
        print(f"{Fore.WHITE}2. {Fore.GREEN}AUTO MODE{Style.RESET_ALL} - Execute immediately after seeing the list\n")
        
        while True:
            choice = input(f"{Fore.GREEN}Enter mode (1 or 2): {Style.RESET_ALL}").strip()
            if choice == "1":
                return "confirm"
            elif choice == "2":
                return "auto"
            else:
                print(f"{Fore.RED}Invalid choice. Please enter 1 or 2.{Style.RESET_ALL}")
    
    def generate_todo_list(self, user_goal: str) -> bool:
        """
        Generate to-do list from user goal using LLM(GPT) with clarifications
        
        Args:
            user_goal: The user's high-level goal
            
        Returns:
            True if successful, False otherwise
        """
        # First, analyze if we need clarifications
        self.print_header("Analyzing Your Goal...", Fore.YELLOW)
        analysis = self.llm.analyze_goal(user_goal)
        
        # Ask clarifying questions if needed
        if analysis.get("needs_clarification") and analysis.get("questions"):
            print(f"{Fore.YELLOW} I have some questions to create better tasks:{Style.RESET_ALL}\n")
            
            for question in analysis["questions"]:
                print(f"{Fore.CYAN}Q: {question['question']}{Style.RESET_ALL}")
                print(f"{Fore.LIGHTBLACK_EX}   (Why: {question['why']}){Style.RESET_ALL}")
                answer = input(f"{Fore.GREEN}A: {Style.RESET_ALL}").strip()
                question["answer"] = answer
                self.clarifications.append(question)
                print()
            
            print(f"{Fore.GREEN}✓ Thanks! Now I can create precise tasks.{Style.RESET_ALL}\n")
        
        # Generate TODO list with all context
        self.print_header("Generating TODO List...", Fore.YELLOW)
        
        tasks_data = self.llm.generate_todos(
            user_goal,
            expertise_level=self.user_expertise,
            clarifications=self.clarifications if self.clarifications else None
        )
        
        if not tasks_data:
            self.print_log("❌", "Failed to generate TODO list", Fore.RED)
            return False
        
        self.todo_list.load_from_dict(tasks_data)
        self.todo_list.display()
        
        return True
    
    def get_user_confirmation(self) -> str:
        """
        Get user confirmation for To-do list in confirm mode
        
        Returns:
            User action: "approve", "edit", "regenerate", or "cancel"
        """
        print(f"\n{Fore.YELLOW}What would you like to do?{Style.RESET_ALL}")
        print(f"{Fore.WHITE}  [a] Approve - Start execution")
        print(f"{Fore.WHITE}  [e] Edit - Modify a task")
        print(f"{Fore.WHITE}  [r] Regenerate - Create a new list")
        print(f"{Fore.WHITE}  [c] Cancel - Exit\n")
        
        while True:
            choice = input(f"{Fore.GREEN}Your choice: {Style.RESET_ALL}").strip().lower()
            if choice in ['a', 'approve']:
                return "approve"
            elif choice in ['e', 'edit']:
                return "edit"
            elif choice in ['r', 'regenerate']:
                return "regenerate"
            elif choice in ['c', 'cancel']:
                return "cancel"
            else:
                print(f"{Fore.RED}Invalid choice. Please enter a, e, r, or c.{Style.RESET_ALL}")
    
    def edit_task(self):
        """Allow user to edit a task with intelligent interpretation"""
        print(f"\n{Fore.CYAN}{'═' * 60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN} TASK EDITOR{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'═' * 60}{Style.RESET_ALL}\n")
        
        # Show numbered task list for easy reference
        print(f"{Fore.YELLOW}Current tasks (look for [#ID]):{Style.RESET_ALL}\n")
        self.todo_list.display()
        
        # Get task ID
        task_id_input = input(f"{Fore.GREEN}Enter task ID (the number in [#ID]): {Style.RESET_ALL}").strip()
        
        try:
            task_id = int(task_id_input)
            task = self.todo_list.get_task_by_id(task_id)
            
            if not task:
                print(f"{Fore.RED}❌ Task #{task_id} not found.{Style.RESET_ALL}")
                return
            
            # Show current task clearly
            phase_icon = {"planning": "📐", "development": "💻", "testing": "🧪", "deployment": "🚀"}.get(task.phase, "📌")
            print(f"\n{Fore.CYAN}{'─' * 60}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Current Task #{task.id}:{Style.RESET_ALL}")
            print(f"{Fore.WHITE}Phase: {phase_icon} {task.phase.title()}{Style.RESET_ALL}")
            print(f"{Fore.WHITE}Title: {task.title}{Style.RESET_ALL}")
            print(f"{Fore.WHITE}Description: {task.description}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'─' * 60}{Style.RESET_ALL}\n")
            
            # Get edit request in natural language
            print(f"{Fore.YELLOW}💡 Tell me how you want to edit this task:{Style.RESET_ALL}")
            print(f"{Fore.LIGHTBLACK_EX}Examples:{Style.RESET_ALL}")
            print(f"{Fore.LIGHTBLACK_EX}  - \"Change the title to 'Build responsive landing page'\"{Style.RESET_ALL}")
            print(f"{Fore.LIGHTBLACK_EX}  - \"Add 'include mobile optimization' to the description\"{Style.RESET_ALL}")
            print(f"{Fore.LIGHTBLACK_EX}  - \"Move this to testing phase\"{Style.RESET_ALL}")
            print(f"{Fore.LIGHTBLACK_EX}  - \"Make it more detailed for beginners\"{Style.RESET_ALL}\n")
            
            edit_request = input(f"{Fore.GREEN}Your edit request: {Style.RESET_ALL}").strip()
            
            if not edit_request:
                print(f"{Fore.YELLOW}No changes made.{Style.RESET_ALL}")
                return
            
            # Use LLM to interpret and apply edits
            print(f"\n{Fore.YELLOW} Interpreting your request...{Style.RESET_ALL}")
            
            current_task_data = {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "phase": task.phase,
                "reasoning": task.reasoning
            }
            
            updated_data = self.llm.interpret_edit_request(edit_request, current_task_data)
            
            # Show interpretation
            print(f"\n{Fore.CYAN} My interpretation:{Style.RESET_ALL}")
            print(f"{Fore.LIGHTBLACK_EX}{updated_data.get('interpretation', 'Applied your changes')}{Style.RESET_ALL}\n")
            
            # Show changes
            if updated_data.get('changes_made'):
                print(f"{Fore.YELLOW}Changes to apply:{Style.RESET_ALL}")
                for change in updated_data['changes_made']:
                    print(f"{Fore.GREEN}  ✓ {change}{Style.RESET_ALL}")
                print()
            
            # Confirm before applying - loop until user is satisfied
            while True:
                confirm = input(f"{Fore.GREEN}Apply these changes? (y/n): {Style.RESET_ALL}").strip().lower()
                
                if confirm == 'y':
                    # Apply changes
                    task.title = updated_data.get('title', task.title)
                    task.description = updated_data.get('description', task.description)
                    task.phase = updated_data.get('phase', task.phase)
                    
                    print(f"\n{Fore.GREEN} Task #{task.id} updated successfully!{Style.RESET_ALL}\n")
                    
                    # Show updated task
                    print(f"{Fore.CYAN}Updated Task:{Style.RESET_ALL}")
                    print(f"{Fore.WHITE}Title: {task.title}{Style.RESET_ALL}")
                    print(f"{Fore.WHITE}Description: {task.description}{Style.RESET_ALL}")
                    print(f"{Fore.WHITE}Phase: {task.phase}{Style.RESET_ALL}\n")
                    break  # Exit the edit loop
                    
                elif confirm == 'n':
                    # User wants to make different changes - ask again
                    print(f"\n{Fore.YELLOW}Let's try again. What would you like to change?{Style.RESET_ALL}\n")
                    
                    edit_request = input(f"{Fore.GREEN}Your new edit request: {Style.RESET_ALL}").strip()
                    
                    if not edit_request:
                        print(f"{Fore.YELLOW}No changes made.{Style.RESET_ALL}")
                        return
                    
                    # Re-interpret with new request
                    print(f"\n{Fore.YELLOW} Interpreting your request...{Style.RESET_ALL}")
                    
                    updated_data = self.llm.interpret_edit_request(edit_request, current_task_data)
                    
                    # Show new interpretation
                    print(f"\n{Fore.CYAN}📝 My interpretation:{Style.RESET_ALL}")
                    print(f"{Fore.LIGHTBLACK_EX}{updated_data.get('interpretation', 'Applied your changes')}{Style.RESET_ALL}\n")
                    
                    # Show new changes
                    if updated_data.get('changes_made'):
                        print(f"{Fore.YELLOW}Changes to apply:{Style.RESET_ALL}")
                        for change in updated_data['changes_made']:
                            print(f"{Fore.GREEN}  ✓ {change}{Style.RESET_ALL}")
                        print()
                    
                    # Loop back to ask for confirmation again
                else:
                    print(f"{Fore.RED}Please enter 'y' or 'n'.{Style.RESET_ALL}")
            
        except ValueError:
            print(f"{Fore.RED} Invalid task ID. Please enter a number.{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED} Error editing task: {str(e)}{Style.RESET_ALL}")
    
    def execute_task(self, task: Task):
        """
        Execute a single task with full logging
        
        Args:
            task: The task to execute
        """
        # Mark as in progress
        task.update_status(TaskStatus.IN_PROGRESS)
        
        # Log selection with phase
        phase_icon = {"planning": "📐", "development": "💻", "testing": "🧪", "deployment": "🚀"}.get(task.phase, "📌")
        self.print_log("🔄", f"Selected task #{task.id}: {task.title}", Fore.CYAN)
        print(f"   {Fore.LIGHTBLACK_EX}Phase: {phase_icon} {task.phase.title()}{Style.RESET_ALL}")
        print(f"   {Fore.LIGHTBLACK_EX}Description: {task.description}{Style.RESET_ALL}")
        
        # Show reasoning if available
        if task.reasoning:
            print(f"   {Fore.BLUE}💡 Why: {task.reasoning}{Style.RESET_ALL}")
        print()
        
        # Log execution start
        self.print_log("⚙️", "Executing task...", Fore.YELLOW)
        
        # Execute using LLM
        result = self.llm.execute_task(
            task={
                "id": task.id,
                "title": task.title,
                "description": task.description
            },
            available_tools=self.tools.get_available_tools()
        )
        
        # Store result
        task.set_result(result)
        
        # Log result
        status = result.get("status", "unknown")
        if status == "done":
            icon = "✅"
            color = Fore.GREEN
            status_text = "SUCCESS"
        elif status == "failed":
            icon = "❌"
            color = Fore.RED
            status_text = "FAILED"
        else:
            icon = "🔄"
            color = Fore.MAGENTA
            status_text = "NEEDS FOLLOW-UP"
        
        self.print_log(icon, f"Result: {status_text}", color)
        
        # Log output
        output = result.get("output", "No output")
        print(f"   {Fore.WHITE}Output: {output}{Style.RESET_ALL}")
        
        # Log reflection
        reflection = result.get("reflection", "No reflection")
        self.print_log("💭", f"Reflection: {reflection}", Fore.LIGHTBLUE_EX)
        
        # Log tools used
        tools_used = result.get("tools_used", [])
        if tools_used:
            print(f"   {Fore.LIGHTBLACK_EX}Tools used: {', '.join(tools_used)}{Style.RESET_ALL}")
        
        print()  # Blank line for spacing
    
    def execution_loop(self):
        """
        Main execution loop - runs until all tasks are terminal
        """
        self.print_header("Starting Execution", Fore.GREEN)
        
        iteration = 0
        max_iterations = 100  # Safety limit
        
        while not self.todo_list.all_tasks_terminal() and iteration < max_iterations:
            iteration += 1
            
            # Get next task
            next_task = self.todo_list.get_next_task()
            
            if not next_task:
                # No pending tasks left, check if any need follow-up
                break
            
            # Execute the task
            self.execute_task(next_task)
        
        # Final summary
        self.print_header("Execution Complete", Fore.CYAN)
        summary = self.todo_list.get_summary()
        
        print(f"{Fore.WHITE}Total tasks: {summary['total']}{Style.RESET_ALL}")
        print(f"{Fore.GREEN} Completed: {summary['done']}{Style.RESET_ALL}")
        print(f"{Fore.RED} Failed: {summary['failed']}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA} Needs follow-up: {summary['needs_follow_up']}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW} Pending: {summary['pending']}{Style.RESET_ALL}\n")
    
    def run(self):
        """
        Main entry point - runs the complete agent workflow
        """
        try:
            # Step 1: Get user goal
            user_goal = self.get_user_goal()
            
            if not user_goal:
                print(f"{Fore.RED}No goal provided. Exiting.{Style.RESET_ALL}")
                return
            
            # Step 2: Select mode BEFORE generating list
            self.mode = self.select_mode()
            print(f"\n{Fore.GREEN}✓ Mode selected: {self.mode.upper()}{Style.RESET_ALL}")
            
            # Step 3: Generate initial TODO list
            success = self.generate_todo_list(user_goal)
            
            if not success:
                print(f"{Fore.RED}Failed to generate TODO list. Exiting.{Style.RESET_ALL}")
                return
            
            # Step 4: Confirmation/Execution loop
            while True:
                # Handle based on mode
                if self.mode == "confirm":
                    action = self.get_user_confirmation()
                    
                    if action == "approve":
                        break  # Proceed to execution
                    elif action == "edit":
                        self.edit_task()
                        # After editing, loop continues and asks for confirmation again
                        # Will display list and show approve/edit/regenerate/cancel menu
                        self.todo_list.display()
                    elif action == "regenerate":
                        # Clear clarifications for fresh start
                        self.clarifications = []
                        # Regenerate the TODO list
                        success = self.generate_todo_list(user_goal)
                        if not success:
                            print(f"{Fore.RED}Failed to generate TODO list. Exiting.{Style.RESET_ALL}")
                            return
                        # Loop continues, will show list and ask for confirmation
                    else:  # cancel
                        print(f"\n{Fore.YELLOW}Cancelled by user. Goodbye{Style.RESET_ALL}")
                        return
                else:  # auto mode
                    print(f"\n{Fore.GREEN} Auto mode - proceeding with execution...{Style.RESET_ALL}")
                    break
            
            # Step 5: Execute all tasks
            self.execution_loop()
            
            # Step 6: Final display
            self.todo_list.display()
            
            print(f"{Fore.CYAN} All done.{Style.RESET_ALL}\n")
            
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}Interrupted by user. Goodbye{Style.RESET_ALL}")
        except Exception as e:
            print(f"\n{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")

