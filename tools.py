"""
Tools that the agent can use to execute tasks
"""
import os
import json
from typing import Dict, Any, List
from datetime import datetime


class AgentTools:
    """
    Collection of tools the agent can use during task execution
    """
    
    def __init__(self, workspace_dir: str = "./output"):
        """
        Initialize tools with workspace directory
        
        Args:
            workspace_dir: Directory where agent can create files
        """
        self.workspace_dir = workspace_dir
        self._ensure_workspace()
    
    def _ensure_workspace(self):
        """Create workspace directory if it doesn't exist"""
        if not os.path.exists(self.workspace_dir):
            os.makedirs(self.workspace_dir)
            print(f"✓ Created workspace directory: {self.workspace_dir}")
    
    def create_file(self, filename: str, content: str) -> Dict[str, Any]:
        """
        Create a file with given content
        
        Args:
            filename: Name of the file to create
            content: Content to write to the file
            
        Returns:
            Result dictionary with success status and message
        """
        try:
            filepath = os.path.join(self.workspace_dir, filename)
            
            # Create subdirectories if needed
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "message": f"Created file: {filepath}",
                "filepath": filepath
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to create file: {str(e)}",
                "filepath": None
            }
    
    def read_file(self, filename: str) -> Dict[str, Any]:
        """
        Read contents of a file
        
        Args:
            filename: Name of the file to read
            
        Returns:
            Result dictionary with file contents or error
        """
        try:
            filepath = os.path.join(self.workspace_dir, filename)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "success": True,
                "content": content,
                "filepath": filepath
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to read file: {str(e)}",
                "content": None
            }
    
    def list_files(self) -> Dict[str, Any]:
        """
        List all files in workspace
        
        Returns:
            List of files in workspace
        """
        try:
            files = []
            for root, dirs, filenames in os.walk(self.workspace_dir):
                for filename in filenames:
                    filepath = os.path.join(root, filename)
                    rel_path = os.path.relpath(filepath, self.workspace_dir)
                    files.append(rel_path)
            
            return {
                "success": True,
                "files": files,
                "count": len(files)
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to list files: {str(e)}",
                "files": []
            }
    
    def calculate(self, expression: str) -> Dict[str, Any]:
        """
        Safely evaluate a mathematical expression
        
        Args:
            expression: Math expression to evaluate
            
        Returns:
            Calculation result
        """
        try:
            # Only allow safe operations
            allowed_chars = set("0123456789+-*/(). ")
            if not all(c in allowed_chars for c in expression):
                return {
                    "success": False,
                    "message": "Invalid characters in expression"
                }
            
            result = eval(expression)
            return {
                "success": True,
                "expression": expression,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Calculation error: {str(e)}"
            }
    
    def log_action(self, action: str, details: str = "") -> Dict[str, Any]:
        """
        Log an action to a log file
        
        Args:
            action: Action being performed
            details: Additional details
            
        Returns:
            Success status
        """
        try:
            log_file = os.path.join(self.workspace_dir, "agent_log.txt")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] {action}"
            if details:
                log_entry += f" - {details}"
            log_entry += "\n"
            
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
            
            return {
                "success": True,
                "message": "Action logged"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to log action: {str(e)}"
            }
    
    def get_available_tools(self) -> List[str]:
        """
        Get list of available tool names
        
        Returns:
            List of tool names
        """
        return [
            "create_file",
            "read_file",
            "list_files",
            "calculate",
            "log_action"
        ]
    
    def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a tool by name with given arguments
        
        Args:
            tool_name: Name of the tool to execute
            **kwargs: Tool-specific arguments
            
        Returns:
            Tool execution result
        """
        if not hasattr(self, tool_name):
            return {
                "success": False,
                "message": f"Tool '{tool_name}' not found"
            }
        
        tool_method = getattr(self, tool_name)
        try:
            return tool_method(**kwargs)
        except Exception as e:
            return {
                "success": False,
                "message": f"Tool execution error: {str(e)}"
            }

