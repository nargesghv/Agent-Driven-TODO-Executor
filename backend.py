"""
Simple FastAPI Backend 
Port: 8007
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import asyncio

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from agent import Agent
    from todo import Task
except ImportError as e:
    print(f"Import Error: {e}")
    print("Make sure agent.py and todo.py are in the same directory as backend.py")
    sys.exit(1)

app = FastAPI(title="Agent TODO Executor API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active sessions
sessions: Dict[str, Agent] = {}


@app.get("/api/debug/sessions")
async def debug_sessions():
    """Debug endpoint to see all active sessions"""
    return {
        "active_sessions": list(sessions.keys()),
        "total": len(sessions)
    }


class GoalRequest(BaseModel):
    goal: str
    expertise_level: str = "intermediate"
    mode: str = "confirm"


class EditRequest(BaseModel):
    task_id: int
    edit_request: str


class AnswerRequest(BaseModel):
    answers: List[str]


@app.get("/")
async def root():
    return {"status": "Agent TODO Executor API is running", "port": 8007}


@app.post("/api/start")
async def start_session(request: GoalRequest):
    """Start a new agent session"""
    try:
        # Create new agent
        session_id = f"session_{len(sessions)}"
        print(f"Creating session: {session_id}")
        
        agent = Agent()
        agent.user_expertise = request.expertise_level
        agent.mode = request.mode
        
        sessions[session_id] = agent
        print(f"Session created successfully: {session_id}")
        
        return {
            "status": "success",
            "session_id": session_id,
            "message": "Agent session started"
        }
    except Exception as e:
        import traceback
        error_msg = f"Error creating session: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )


@app.post("/api/analyze/{session_id}")
async def analyze_goal(session_id: str, request: GoalRequest):
    """Analyze goal and get clarifying questions"""
    try:
        agent = sessions.get(session_id)
        if not agent:
            return JSONResponse(
                status_code=404,
                content={"status": "error", "message": "Session not found"}
            )
        
        # Analyze the goal
        analysis = agent.llm.analyze_goal(request.goal)
        
        return {
            "status": "success",
            "needs_clarification": analysis.get("needs_clarification", False),
            "questions": analysis.get("questions", []),
            "analysis": analysis.get("analysis", "")
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )


@app.post("/api/generate/{session_id}")
async def generate_todos(session_id: str, request: GoalRequest):
    """Generate TODO list"""
    try:
        print(f"Generating TODOs for session: {session_id}")
        print(f"Request data: goal={request.goal}, expertise={request.expertise_level}")
        
        agent = sessions.get(session_id)
        if not agent:
            return JSONResponse(
                status_code=404,
                content={"status": "error", "message": "Session not found"}
            )
        
        # Generate TODOs
        print(f"Calling LLM to generate TODOs...")
        tasks_data = agent.llm.generate_todos(
            request.goal,
            expertise_level=agent.user_expertise,
            clarifications=agent.clarifications if agent.clarifications else None
        )
        print(f"Generated {len(tasks_data)} tasks")
        
        if not tasks_data:
            return JSONResponse(
                status_code=500,
                content={"status": "error", "message": "Failed to generate tasks"}
            )
        
        # Load into agent
        agent.todo_list.load_from_dict(tasks_data)
        
        # Return tasks grouped by phase
        tasks_by_phase = {}
        for task in agent.todo_list.tasks:
            phase = task.phase
            if phase not in tasks_by_phase:
                tasks_by_phase[phase] = []
            tasks_by_phase[phase].append({
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "phase": task.phase,
                "reasoning": task.reasoning,
                "status": task.status.value
            })
        
        return {
            "status": "success",
            "tasks": tasks_by_phase,
            "total": len(agent.todo_list.tasks)
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )


@app.post("/api/edit/{session_id}")
async def edit_task(session_id: str, request: EditRequest):
    """Edit a task using natural language"""
    try:
        agent = sessions.get(session_id)
        if not agent:
            return JSONResponse(
                status_code=404,
                content={"status": "error", "message": "Session not found"}
            )
        
        # Get task
        task = agent.todo_list.get_task_by_id(request.task_id)
        if not task:
            return JSONResponse(
                status_code=404,
                content={"status": "error", "message": "Task not found"}
            )
        
        # Get current task data
        current_task_data = {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "phase": task.phase,
            "reasoning": task.reasoning
        }
        
        # Interpret edit request
        updated_data = agent.llm.interpret_edit_request(request.edit_request, current_task_data)
        
        return {
            "status": "success",
            "interpretation": updated_data.get("interpretation", ""),
            "changes_made": updated_data.get("changes_made", []),
            "updated_task": {
                "title": updated_data.get("title", task.title),
                "description": updated_data.get("description", task.description),
                "phase": updated_data.get("phase", task.phase)
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )


class UpdateTaskRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    phase: Optional[str] = None


@app.get("/api/get-tasks/{session_id}")
async def get_tasks(session_id: str):
    """Get current task list"""
    try:
        print(f"Getting tasks for session: {session_id}")
        print(f"Available sessions: {list(sessions.keys())}")
        
        agent = sessions.get(session_id)
        if not agent:
            print(f" Session {session_id} not found!")
            return JSONResponse(
                status_code=404,
                content={"status": "error", "message": f"Session {session_id} not found. Available: {list(sessions.keys())}"}
            )
        
        # Return tasks grouped by phase
        tasks_by_phase = {}
        for task in agent.todo_list.tasks:
            phase = task.phase
            if phase not in tasks_by_phase:
                tasks_by_phase[phase] = []
            tasks_by_phase[phase].append({
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "phase": task.phase,
                "reasoning": task.reasoning,
                "status": task.status.value
            })
        
        print(f"✅ Returning {len(agent.todo_list.tasks)} tasks for session {session_id}")
        
        return {
            "status": "success",
            "tasks": tasks_by_phase,
            "total": len(agent.todo_list.tasks)
        }
    except Exception as e:
        import traceback
        print(f" Error getting tasks: {e}\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )


@app.post("/api/apply-edit/{session_id}")
async def apply_edit(session_id: str, task_id: int, request: UpdateTaskRequest):
    """Apply the edit to a task"""
    try:
        print(f"Applying edit to task #{task_id} in session {session_id}")
        print(f"Available sessions: {list(sessions.keys())}")
        
        agent = sessions.get(session_id)
        if not agent:
            print(f" Session {session_id} not found!")
            return JSONResponse(
                status_code=404,
                content={"status": "error", "message": f"Session {session_id} not found"}
            )
        
        task = agent.todo_list.get_task_by_id(task_id)
        if not task:
            return JSONResponse(
                status_code=404,
                content={"status": "error", "message": "Task not found"}
            )
        
        # Apply changes
        if request.title:
            task.title = request.title
        if request.description:
            task.description = request.description
        if request.phase:
            task.phase = request.phase
        
        print(f"Task #{task_id} updated successfully")
        
        return {"status": "success", "message": "Task updated"}
    except Exception as e:
        import traceback
        print(f"Error applying edit: {e}\n{traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": str(e)}
        )


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket for real-time task execution"""
    await websocket.accept()
    
    try:
        agent = sessions.get(session_id)
        if not agent:
            await websocket.send_json({"type": "error", "message": "Session not found"})
            await websocket.close()
            return
        
        # Send initial status
        await websocket.send_json({
            "type": "status",
            "message": "Starting execution...",
            "total_tasks": len(agent.todo_list.tasks)
        })
        
        # Execute tasks
        iteration = 0
        max_iterations = 100
        
        while not agent.todo_list.all_tasks_terminal() and iteration < max_iterations:
            iteration += 1
            
            next_task = agent.todo_list.get_next_task()
            if not next_task:
                break
            
            # Send task started
            await websocket.send_json({
                "type": "task_start",
                "task": {
                    "id": next_task.id,
                    "title": next_task.title,
                    "description": next_task.description,
                    "phase": next_task.phase
                }
            })
            
            # Execute task
            result = agent.llm.execute_task(
                {
                    "id": next_task.id,
                    "title": next_task.title,
                    "description": next_task.description
                },
                agent.tools.get_available_tools()
            )
            
            # Update task
            next_task.set_result(result)
            
            # Send result
            await websocket.send_json({
                "type": "task_complete",
                "task_id": next_task.id,
                "status": result.get("status", "done"),
                "output": result.get("output", ""),
                "reflection": result.get("reflection", ""),
                "tools_used": result.get("tools_used", [])
            })
            
            await asyncio.sleep(0.5)  # Small delay for better UX
        
        # Send completion
        summary = agent.todo_list.get_summary()
        await websocket.send_json({
            "type": "complete",
            "summary": summary
        })
        
    except WebSocketDisconnect:
        print(f"Client disconnected from {session_id}")
    except Exception as e:
        await websocket.send_json({"type": "error", "message": str(e)})
    finally:
        await websocket.close()


if __name__ == "__main__":
    import uvicorn
    import sys
    
    print("=" * 60)
    print("Agent TODO Executor Backend")
    print("=" * 60)
    print(f"Backend API: http://localhost:8007")
    print(f"Health check: http://localhost:8007/")
    print(f"Frontend: Open frontend.html in your browser")
    print("=" * 60)
    print()
    
    # Fix for Windows event loop policy (Python 3.8+)
    if sys.platform == 'win32':
        import asyncio
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    uvicorn.run(
        app, 
        host="127.0.0.1",  # Use localhost instead of 0.0.0.0 for Windows
        port=8007,
        log_level="info"
    )

