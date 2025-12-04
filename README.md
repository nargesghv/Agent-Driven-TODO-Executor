# Agent-Driven TODO Executor

A smart agent that takes your high-level goals, breaks them down into actionable tasks, and executes them. No frameworks - just pure Python and OpenAI.

## What Does It Do?

You tell it what you want to build (like "create a landing page for my product"), and it:
1. Asks a few clarifying questions
2. Creates a detailed TODO list with all phases (planning, development, testing, deployment)
3. Lets you review and edit tasks
4. Executes them step by step with full logging

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run it
python main.py
```

## How It Works

Here's the actual flow when you run it:

```
┌─────────────────────────────────────┐
│  You: "Build a landing page"        │
└──────────────┬──────────────────────┘
               │
               ↓
┌─────────────────────────────────────┐
│  Agent: What's your skill level?    │
│  1. Beginner                        │
│  2. Intermediate                    │
│  3. Expert                          │
└──────────────┬──────────────────────┘
               │
               ↓
┌─────────────────────────────────────┐
│  Agent: I have some questions:      │
│  - What should the landing page do? │
│  - Any specific features?           │
└──────────────┬──────────────────────┘
               │
               ↓
┌─────────────────────────────────────┐
│  Agent generates TODO list:         │
│                                     │
│  PLANNING                           │
│  [#1] Define page structure         │
│                                     │
│  DEVELOPMENT                        │
│  [#2] Create HTML layout            │
│  [#3] Add CSS styling               │
│  [#4] Implement JavaScript          │
│                                     │
│  TESTING                            │
│  [#5] Test across browsers          │
│  [#6] Test mobile responsive        │
│                                     │
│  DEPLOYMENT                         │
│  [#7] Deploy to hosting             │
└──────────────┬──────────────────────┘
               │
               ↓
┌─────────────────────────────────────┐
│  Choose mode:                       │
│  • Confirm - Review before running  │
│  • Auto - Run immediately           │
└──────────────┬──────────────────────┘
               │
               ↓ (if Confirm mode)
┌─────────────────────────────────────┐
│  What do you want to do?            │
│  [a] Approve - Start execution      │
│  [e] Edit - Modify a task           │
│  [r] Regenerate - New list          │
│  [c] Cancel - Exit                  │
└──────────────┬──────────────────────┘
               │
               ↓ (you choose Approve)
┌─────────────────────────────────────┐
│  EXECUTING TASKS                    │
│                                     │
│  Task #1: Define page structure     │
│  Executing...                       │
│  SUCCESS                            │
│  Reflection: Created sitemap...     │
│                                     │
│  Task #2: Create HTML layout        │
│  Executing...                       │
│  SUCCESS                            │
│  ...                                │
└─────────────────────────────────────┘
```

## Features

### Smart Planning
The agent doesn't just list tasks - it understands context. Tell it you're building a marketplace, and it'll add things like:
- User authentication
- Payment handling
- Seller verification
- Reviews system
- Admin dashboard

Even if you didn't mention them. It knows what marketplaces need.

### Adaptive Detail Level
Choose your experience level and get tasks tailored to you:

**Beginner:**
```
[#1] Install Node.js from nodejs.org
[#2] Open terminal and run: npm init
[#3] Create a new file called index.html
[#4] Add basic HTML structure: <!DOCTYPE html>...
```

**Expert:**
```
[#1] Initialize React project with TypeScript
[#2] Configure build pipeline and testing framework
[#3] Implement component architecture
```

### Intelligent Editing
Don't like a task? Just tell the agent what you want to change in plain English:

```
You: "Add mobile optimization to task #3"
Agent: I'll add 'ensure mobile responsiveness' to the description
      Apply? (y/n)
```

### Complete Lifecycle
Every project gets proper phases:
- **Planning** - Structure, wireframes, design
- **Development** - Building features
- **Testing** - Cross-browser, mobile, functionality
- **Deployment** - Staging and production

No more "build it and forget to test."

### Two Modes

**Confirm Mode** (recommended first time)
- Review TODO list before execution
- Edit tasks if needed
- Regenerate if you don't like it
- Full control

**Auto Mode** (for when you trust it)
- Generates list and runs immediately
- Still shows all logs
- Faster workflow

## Project Structure

```
agent-todo-executor/
├── agent.py           # Main orchestrator (the brain)
├── llm.py             # OpenAI integration (the intelligence)
├── todo.py            # Task management (the memory)
├── tools.py           # Agent tools (the hands)
├── config.py          # Settings
├── main.py            # Entry point
└── requirements.txt   # Dependencies (just 3!)
```

## Configuration

### Set Your API Key

**Option 1: Edit config.py**
```python
OPENAI_API_KEY = "your-key-here"
OPENAI_MODEL=
```

**Option 2: Use .env file** 
```bash
echo "OPENAI_API_KEY=your-key-here" > .env
echo "OPENAI_MODEL=Model" >> .env
```

### Change the Model

In `config.py`:
```python
OPENAI_MODEL = " "       
```

## Example Session

Here's what a real session looks like:

```bash
$ python main.py

Agent-Driven TODO Executor
═══════════════════════════════════════

First, let me understand your experience level:
1. Beginner - I need detailed, step-by-step guidance
2. Intermediate - I have some technical knowledge
3. Expert - I'm experienced, just show high-level tasks

Your level (1-3): 2

✓ Got it! I'll tailor tasks for intermediate level.

What would you like to achieve?
> Build a simple portfolio website with projects gallery

Analyzing Your Goal...

I have some questions to create better tasks:

Q: What sections do you want? (e.g., about, projects, contact)
A: About me, projects showcase, skills, and contact form

Q: Do you have design preferences? (minimal, modern, colorful, etc.)
A: Clean and minimal design

Thanks! Now I can create precise tasks.

Generating TODO List...

═══════════════════════════════════════
To-dos 10
═══════════════════════════════════════

PLANNING
────────────────────────────────────────
[#1] Define site structure and navigation
   Create sitemap with about, projects, skills, contact sections
.
.
.
EPLOYMENT
────────────────────────────────────────
○ [#10] Deploy to hosting platform
    Set up domain, SSL, and configure hosting

═══════════════════════════════════════

⚙️ Select Execution Mode
1. CONFIRM MODE - Review and approve TODO list
2. AUTO MODE - Execute immediately

Enter mode (1 or 2): 1

✓ Mode selected: CONFIRM

What would you like to do?
  [a] Approve - Start execution
  [e] Edit - Modify a task
  [r] Regenerate - Create a new list
  [c] Cancel - Exit

Your choice: a

Starting Execution
═══════════════════════════════════════

Selected task #1: Define site structure and navigation
   Phase: Planning
   Description: Create sitemap with about, projects, skills, contact
     Why: Planning the structure prevents issues later

Executing task...
Result: SUCCESS
-----

## Smart Editing Example

You just tell it what you want to edit:

```bash
Your choice: e

TASK EDITOR

Current tasks (look for [#ID]):
○ [#3] Build about section with bio

Enter task ID: 3

Current Task #3:
Title: Build about section with bio
Description: Include profile photo and introduction

Tell me how you want to edit:
Your edit request: Add a timeline of my career history

Interpreting your request...

My interpretation:
I'll add 'include career timeline with key milestones' to the description

Changes to apply:
  ✓ Extend description with career timeline feature

Apply these changes? (y/n): y

Task #3 updated successfully!
```

If you say "n", it asks what else you want to change. Keeps going until you're happy.

## Technical Details

### No Frameworks
This Project doesn't use LangChain, LangGraph, or similar. Just:
- Pure Python for the agent loop
- OpenAI SDK for LLM calls

### How Generation Works

```python
# Simplified version of what happens:

1. User provides goal
2. Agent analyzes if clarification is needed
3. If vague → asks questions
4. Builds detailed prompt with:
   - User's goal
   - Their skill level (beginner/intermediate/expert)
   - Their answers to questions
   - Requirement to include all phases
5. Sends to OpenAI with JSON output format
6. Parses tasks with: id, title, description, phase, reasoning
7. Displays organized by phase
8.Run Tasks
```

### Execution Loop

```python
while tasks_remain:
    task = get_next_pending_task()  # FIFO order
    mark_in_progress(task)
    
    result = llm.execute_task(task, available_tools)
    
    log(task, result)
    update_status(task, result.status)
```

## Requirements

- Python 3.8+
- OpenAI API key
- 3 Python packages (openai, python-dotenv, colorama)

## Troubleshooting

**"Error calling LLM"**
- Check your API key in config.py
- Make sure you have credits in your OpenAI account

**Tasks not detailed enough**
- Choose "Beginner" level for more detail
- Or edit the tasks and ask for "more detail for beginners"

**Want different tasks**
- Choose [r] Regenerate
- Or [e] Edit individual tasks

**Agent misunderstood my goal**
- The clarifying questions help with this
- Be specific in your goal description
- You can always regenerate

## Contributing

This is a learning project. Feel free to:
- Add more tools in tools.py
- Improve the prompts in llm.py
- Add features you need
---

