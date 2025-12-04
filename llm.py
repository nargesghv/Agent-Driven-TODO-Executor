"""
LLM Interface
"""
import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL, TEMPERATURE, MAX_TOKENS


class LLMInterface:
    
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL
        self.conversation_history: List[Dict[str, str]] = []
    
    def chat(self, user_message: str, system_prompt: Optional[str] = None) -> str:
        """
        Send a chat message and get response
        
        Args:
            user_message: The user's message
            system_prompt: Optional system prompt to guide behavior
            
        Returns:
            The assistant's response
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add conversation history
        messages.extend(self.conversation_history)
        
        # Add new user message
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS
            )
            
            assistant_message = response.choices[0].message.content
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": assistant_message})
            
            return assistant_message
            
        except Exception as e:
            return f"Error calling LLM: {str(e)}"
    
    def generate_todos(self, user_goal: str, expertise_level: str = "intermediate", 
                      clarifications: Optional[List[Dict[str, str]]] = None) -> List[Dict[str, Any]]:
        """
        Generate structured TODO list from user goal with adaptive detail
        
        Args:
            user_goal: High-level goal from user
            expertise_level: User's technical level (beginner/intermediate/expert)
            clarifications: Optional clarifying Q&A from user
            
        Returns:
            List of tasks with id, title, description, status, phase
        """
        # Adaptive detail based on expertise
        detail_instructions = {
            "beginner": "Break tasks into VERY detailed, small steps. Explain technical terms. Include setup and configuration steps.",
            "intermediate": "Balance detail and brevity. Assume basic technical knowledge. Focus on main deliverables.",
            "expert": "High-level tasks only. Assume deep technical expertise. Be concise but comprehensive."
        }
        
        # Add clarifications context
        clarification_context = ""
        if clarifications:
            clarification_context = "\n\nUser provided these clarifications:\n"
            for qa in clarifications:
                clarification_context += f"Q: {qa['question']}\nA: {qa['answer']}\n"
        
        system_prompt = f"""You are an expert project planner. Break down user goals into clear, actionable tasks.

User expertise level: {expertise_level}
{detail_instructions[expertise_level]}

CRITICAL: Always include a complete project lifecycle:
1. Planning/Design phase tasks
2. Development phase tasks (break into specific features/pages)
3. Testing phase tasks (functionality, UX, cross-browser, performance)
4. Deployment phase tasks (staging, production, monitoring)

{clarification_context}

Return a JSON object with this exact structure:
{{
    "tasks": [
        {{
            "id": 1,
            "title": "Brief task title",
            "description": "Detailed description of what needs to be done",
            "status": "pending",
            "phase": "planning|development|testing|deployment",
            "reasoning": "Why this task is important"
        }}
    ]
}}

Keep tasks atomic, actionable, and well-sequenced. Always include testing and deployment phases."""

        user_prompt = f"""User Goal: {user_goal}

Please break this down into a structured TODO list with complete lifecycle (design, develop, test, deploy). 
Return ONLY valid JSON, no other text."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get("tasks", [])
            
        except Exception as e:
            print(f"Error generating TODOs: {e}")
            return []
    
    def execute_task(self, task: Dict[str, Any], available_tools: List[str]) -> Dict[str, Any]:
        """
        Execute a single task using LLM reasoning and available tools
        
        Args:
            task: Task dictionary with id, title, description
            available_tools: List of tool names the agent can use
            
        Returns:
            Execution result with status, output, reflection
        """
        system_prompt = f"""You are an autonomous task executor. Given a task, you must:
1. Analyze what needs to be done
2. Choose appropriate tools from: {', '.join(available_tools)}
3. Execute the task step by step
4. Return a structured result

Return ONLY valid JSON with this structure:
{{
    "status": "done|failed|needs-follow-up",
    "actions_taken": ["List of actions performed"],
    "output": "Brief description of what was created/done",
    "reflection": "Brief reflection on the result",
    "tools_used": ["tool1", "tool2"]
}}"""

        user_prompt = f"""Task #{task['id']}: {task['title']}
Description: {task['description']}

Execute this task now. Return the result in JSON format."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.5,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            return {
                "status": "failed",
                "actions_taken": [],
                "output": f"Execution failed: {str(e)}",
                "reflection": "Error occurred during task execution",
                "tools_used": []
            }
    
    def analyze_goal(self, user_goal: str) -> Dict[str, Any]:
        """
        Analyze user goal and generate clarifying questions if needed
        
        Args:
            user_goal: High-level goal from user
            
        Returns:
            Analysis with questions if clarification needed
        """
        system_prompt = """You are a project analyst. Analyze the user's goal and determine if you need clarifying questions.

If the goal is vague or missing critical details, ask 2-3 specific questions.
If the goal is clear and detailed, proceed without questions.

Return JSON with this structure:
{
    "needs_clarification": true/false,
    "questions": [
        {
            "question": "Specific question to ask user",
            "why": "Why this matters for planning"
        }
    ],
    "analysis": "Brief analysis of the goal"
}"""

        user_prompt = f"""User Goal: {user_goal}

Analyze this goal. Does it need clarification? Return ONLY valid JSON."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"Error analyzing goal: {e}")
            return {"needs_clarification": False, "questions": [], "analysis": ""}
    
    def interpret_edit_request(self, edit_request: str, current_task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use LLM to interpret user's edit request and generate updated task
        
        Args:
            edit_request: User's natural language edit request
            current_task: Current task data (id, title, description, phase)
            
        Returns:
            Updated task data
        """
        system_prompt = """You are a task editor assistant. The user wants to edit a task.
        
Analyze their edit request and return the updated task.
If the request is unclear, make reasonable interpretation.

Return JSON with this structure:
{
    "title": "Updated task title (or keep original if not mentioned)",
    "description": "Updated description (or keep original if not mentioned)",
    "phase": "planning|development|testing|deployment (or keep original)",
    "changes_made": ["List of specific changes applied"],
    "interpretation": "How you interpreted the user's request"
}"""

        user_prompt = f"""Current Task:
Title: {current_task.get('title', '')}
Description: {current_task.get('description', '')}
Phase: {current_task.get('phase', 'development')}

User's Edit Request: {edit_request}

Apply the user's edits and return the updated task. Be smart about interpreting their intent."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"Error interpreting edit: {e}")
            return {
                "title": current_task.get('title'),
                "description": current_task.get('description'),
                "phase": current_task.get('phase'),
                "changes_made": [],
                "interpretation": "Could not interpret edit request"
            }
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []

