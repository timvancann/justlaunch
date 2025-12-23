Product Vision
A terminal-based control center that turns a static justfile into an interactive dashboard. It eliminates the need to remember syntax or argument names, providing a safe, visual environment to trigger complex data pipelines or local dev tasks.

Tech Stack
Language: Python 3.12+

TUI Framework: Textual (using CSS-like styling and async workers).

Package/Build Manager: uv (for lightning-fast startup and uv tool install distribution).

Data Source: just --dump --dump-format json (The official machine-readable source).

Milestone 1: The "Finder" (MVP)
Goal: Load the current directory's justfile and list all commands with their documentation.

Feature 1.1: Schema Parsing. On startup, run just --dump --dump-format json. Parse the recipes object to extract name, docstrings (doc), and parameters.

Feature 1.2: The Command List. A sidebar (or main list) using ListView or OptionList.

Display the recipe name in bold.

Display the first line of the doc comment as a subtitle.

Feature 1.3: Fuzzy Search. A global Input field at the top. Typing instantly filters the list (case-insensitive fuzzy match).

Feature 1.4: Metadata View. Selecting a command updates a side-panel showing the full command body (what it actually runs) and all available parameters.

Milestone 2: The "Runner" (Execution & Logs)
Goal: Launch a command and see the output without leaving the TUI.

Feature 2.1: Async Execution. Use Textual Workers to spawn subprocess.Popen. This ensures the UI doesn't freeze while a long Spark job or local build is running.

Feature 2.2: Live Streaming Log. A RichLog or Log widget that captures stdout and stderr in real-time.

Feature 2.3: Status Indicators.

Running: A spinning loader or a "Running" badge next to the command.

Success/Fail: Color-coded border (Green/Red) based on the exit code.

Feature 2.4: Execution History. A small footer showing the last 5 executed commands and their run time.

Milestone 3: The "Injector" (Interactivity)
Goal: Handle just recipes that require arguments (e.g., just deploy {{env}}).

Feature 3.1: Auto-Generated Forms. If a recipe has parameters:

When the user hits Enter to run, open a Modal Screen.

Dynamically generate an Input field for every argument.

Show default values as "ghost text" (placeholders).

Feature 3.2: Argument Memory. Save the last-used values for each recipe in a local cache file (e.g., ~/.cache/jit/history.json).

Feature 3.3: Env Selector. A toggle to select a specific .env file to pass to just via the --dotenv-path flag.

Milestone 4: The "Pro" (Polish & Distribution)
Goal: Make it feel like a high-end CLI tool ready for uv.

Feature 4.1: Custom Themes. Support for "Dracula" or "Nord" themes via Textual CSS.

Feature 4.2: Hotkeys. * r: Re-run last command.

x: Kill currently running process.

k: Clear logs.

Feature 4.3: UV Distribution. Configure pyproject.toml so the tool is "ready to go."

Bash

# Distribution via UV
uv tool install git+https://github.com/timvancann/jl (justlaunch)
jl  # Starts the TUI instantly

# Testing
In this directory, create a justfile with a few commands that spec out what justfiles are capable of. (docker build, docker run, arguments, uvx <tool>, etc.). Think about:
- just lint (runs ruff [with import sorting] and ty)
- just run (runs this TUI in terminal or web mode), needs argumunt [tui, web]
- just build (runs uv build)

# Design
Reference the DESIGN_SKILL.md file for design guidelines, use a good color theme like Dracula. Make sure it it system agnostic, works on both dark and light mode, and runs on Mac, Linux and Windows. 
