# Task 1 Report: Repository Cloning via Autonomous AI Agent

**Course:** AI for Software Engineering (AI4SE)  
**Lab:** Week 06 – Implementation  
**Assignment:** Task 1 – Repository Cloning & Mechanism Analysis  
**Target Repository:** [https://github.com/Neltharion59/AI4SE_Playground](https://github.com/Neltharion59/AI4SE_Playground)  

---

## 1. Executive Summary

In this task, the AI coding assistant successfully cloned the target repository `AI4SE_Playground` into the local assignment workspace (`Week_06_Implementation/Assignments/Task_1/AI4SE_Playground`) and prepared the workspace for downstream Retrieval-Augmented Generation (RAG) and implementation tasks. 

As instructed, the internal `.git` directory of the cloned repository was removed immediately following the clone operation to prevent git submodule conflicts and repository history clutter in the parent repository.

---

## 2. Cloning Mechanism: How the Agent Performed the Task

A standard Large Language Model (LLM) is fundamentally a stateless next-token predictor. It has no native networking capabilities, no direct operating system handles, and no capability to execute shell commands independently. The ability of the agent to perform the repository cloning is enabled by an **agentic tool-use runtime architecture (Function Calling / Tool Augmentation)**.

### Architectural Breakdown of the Mechanism

1. **Agent Tool Declaration & Schema Exposure:**
   - The agent runtime (Antigravity CLI harness) injects structured tool definitions into the model's system prompt and tool calling schema.
   - Among these declared tools is `run_command`, which provides an interface to execute non-interactive commands in a Linux Bash shell environment with defined parameters (`CommandLine`, `WaitMsBeforeAsync`, `toolSummary`).

2. **Reasoning & Tool Invocation Decision (ReAct Loop):**
   - Upon receiving the user's prompt to complete the assignment, the agent analyzed the task requirements defined in `Task_1.md`.
   - The model recognized the need to pull an external Git repository from GitHub and formulated a structured function call:
     ```json
     {
       "tool": "run_command",
       "parameters": {
         "CommandLine": "git clone https://github.com/Neltharion59/AI4SE_Playground.git AI4SE_Playground",
         "toolSummary": "Clone AI4SE_Playground repository",
         "WaitMsBeforeAsync": 10000
       }
     }
     ```

3. **Runtime Execution & Host Subprocess Dispatch:**
   - The agent harness intercepted the JSON tool call before sending any response to the user.
   - The runtime spawned a subshell process on the host Linux OS (`/bin/bash`) executing the specified command.
   - The underlying host system fulfilled the prerequisites:
     - The `git` command-line utility was installed and available in the system `$PATH`.
     - Outbound HTTPS network access to `github.com` (port 443) was open, allowing the Git Smart Transfer Protocol to negotiate objects with GitHub.
     - The host file system granted write permissions in the working directory `/home/juraj/skola/zimny1/usingAI/AI4SE_Labs_2026/Week_06_Implementation/Assignments/Task_1`.

4. **Stream Capture & Feedback into Context:**
   - The subprocess output (standard output and standard error: object enumeration, delta compression, transfer speed) was captured by the runtime and returned to the LLM context as a tool execution response.
   - The model inspected the exit code (`0`) and the transfer log to verify successful completion.

5. **Post-Processing: Deleting the `.git` Directory:**
   - A nested `.git` directory within an existing Git repository causes Git to treat the directory as an untracked gitlink (submodule) rather than tracking the individual files.
   - The agent issued a second command:
     ```bash
     rm -rf AI4SE_Playground/.git
     ```
   - This transformed the directory tree into standard, fully trackable source files within the primary course repository.

6. **State Verification:**
   - The agent validated the repository tree using `tree` and verified Git tracking status via `git status -u`.

---

## 3. Workflow & Interaction Flow

The interaction sequence between User, Agent LLM, Agent Runtime, Host OS, and GitHub is visualized below:

```mermaid
sequenceDiagram
    autonumber
    actor User as User / Student
    participant Agent as LLM Agent (Cognitive Core)
    participant Runtime as Agent Runtime / Tool Dispatcher
    participant OS as Host OS & Shell (Linux)
    participant GitHub as Remote GitHub Repository

    User->>Agent: "Urob dane zadanie" (Execute Task 1)
    Agent->>Agent: Reads Task_1.md; determines repository URL
    Agent->>Runtime: Tool Call: run_command("git clone ...")
    Runtime->>OS: Spawn subshell: git clone https://github.com/...
    OS->>GitHub: HTTPS Handshake & Git Packfile Transfer
    GitHub-->>OS: Repository objects (35 objects, commits, trees)
    OS-->>Runtime: Subprocess finished (exit code 0)
    Runtime-->>Agent: Tool Response (stdout/stderr log)
    Agent->>Runtime: Tool Call: run_command("rm -rf AI4SE_Playground/.git")
    Runtime->>OS: Remove nested .git directory
    OS-->>Runtime: Success (exit code 0)
    Runtime-->>Agent: Confirmation
    Agent->>Runtime: Tool Call: Verify files (tree / git status)
    Runtime-->>Agent: 27 files found, cleanly tracked
    Agent->>User: Confirmation & Technical Report
```

---

## 4. Verification & Cloned Content Overview

The cloned repository contains a Python package simulating an event ticketing and order management system (`playground`), along with its unit test suite:

- **Total Files:** 27 files across 4 directories
- **Source Package (`playground/playground`):**
  - `base.py`, `decorators.py`, `enums.py`, `events.py`, `exceptions.py`
  - `inventory.py`, `models.py`, `orders.py`, `pricing.py`, `repository.py`
  - `simulation.py`, `util.py`
- **Test Suite (`playground/tests`):**
  - Unit tests covering all domain models, services, events, and simulations.

All source and test files are now directly accessible in the assignment workspace and ready for Task 2 (Context Chunking & RAG Preparation).
