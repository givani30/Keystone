# Keystone - Gemini Integration Guide

## Overview

This document provides essential context for developing **Keystone**, a Python command-line tool that generates visually appealing keybind cheatsheets from JSON and YAML configuration files.

The core idea is to separate keybind data from presentation, allowing users to define their keybinds once and render them in multiple formats and styles using templates and themes.

## Essential Commands

### Package Management (`uv`)

This project uses `uv` for fast dependency management.

```bash
# Install project in editable mode with all optional dependencies
uv pip install -e .[pdf,dev]

# Check for broken dependencies
uv pip check

# Run linters/formatters (once configured)
# uv run lint
# uv run format
```

### Keystone CLI Usage

The main entry point is the `keystone` command.

```bash
# Auto-discover and run from keystone.yml, layout.yml, or .keystone.yml
keystone

# Run with an explicit layout file
keystone my_workflow.yml

# Override settings from the layout file
keystone my_workflow.yml --template reference_card --theme dark

# Control output format and location
keystone my_workflow.yml --format pdf --output ~/Desktop/cheatsheet.pdf

# Validate configuration files without generating output
keystone --validate

# Create example data and layout files in the current directory
keystone --init

# List available themes
keystone --list-themes
```

## Key Files & Project Structure

The project follows a modular architecture to separate concerns.

```
keystone/
├── main.py                   # CLI entry point (argparse)
├── core/
│   ├── generator.py          # Core HTML/PDF generation logic
│   ├── validator.py          # Schema validation (JSON Schema)
│   ├── data_loader.py        # Loads keybind data files (.json)
│   └── layout_parser.py      # Parses layout configuration (.yml)
├── templates/
│   ├── skill_tree.py         # Card-based "Skill Tree" template
│   └── reference_card.py     # Dense, table-based "Reference Card" template
├── themes/
│   ├── default.json          # Base theme with style classes
│   ├── dark.json             # Dark theme variant
│   └── minimal.json          # Minimalist theme variant
├── assets/
│   ├── icons.json            # SVG icon manifest (e.g., for Heroicons)
│   └── schemas/
│       ├── data_schema.json      # Schema for keybind data files
│       └── layout_schema.json    # Schema for layout config files
└── utils/
    ├── discovery.py          # Logic to find the layout config file
    ├── pdf_generator.py      # WeasyPrint integration for PDF output
    └── theme_loader.py       # Loads themes and handles inheritance
```

## Core Concepts

-   **Data Files (`.json`):** Contain tool-specific keybinds, organized into categories. Validated by `data_schema.json`.
-   **Layout File (`.yml`):** The main configuration file. It defines the title, output name, template, theme, and orchestrates which data files to use. It can also include inline keybinds that override imported ones. Validated by `layout_schema.json`.
-   **Templates (`.py`):** Python modules that generate the HTML structure. They receive the parsed data and theme information and return an HTML string.
-   **Themes (`.json`):** Define the visual appearance by mapping style names (e.g., `card_header`) to CSS utility classes (e.g., `bg-blue-500 text-white`). Themes can inherit from a base theme.
-   **Schemas (`.json`):** Define the valid structure for data and layout files, enabling robust validation.

## Development Workflow

1.  **Setup:** Ensure dependencies are installed with `uv pip install -e .[pdf,dev]`.
2.  **Create Test Data:** Use `keystone --init` to generate `layout.yml` and `keybinds.json` for testing.
3.  **Modify Code:**
    -   To change HTML structure, edit a file in `keystone/templates/`.
    -   To change styling, edit a file in `keystone/themes/`.
    -   To change core logic (data loading, validation, etc.), edit a file in `keystone/core/`.
4.  **Run & Test:** Execute `keystone layout.yml --format html --output test.html` to generate a cheatsheet.
5.  **View Output:** Open `test.html` in a browser to inspect the changes.
6.  **Validate:** Run `keystone --validate` to check your configuration against the schemas.
7.  **Testing:** (Future) Run `pytest` to execute the test suite.

## Taskmaster MCP Integration

This project can be managed using the Taskmaster MCP. The following are some of the most common commands that can be used to manage the project.

### Essential MCP Tools

- `initialize_project`: Initialize Task Master in the current project.
- `parse_prd`: Generate tasks from a Product Requirements Document.
- `get_tasks`: Show all tasks with their status.
- `next_task`: Get the next available task to work on.
- `get_task`: View detailed information about a specific task.
- `set_task_status`: Mark a task as complete.
- `add_task`: Add a new task with AI assistance.
- `expand_task`: Break a task into subtasks.
- `update_task`: Update a specific task.
- `update_subtask`: Add implementation notes to a subtask.
- `analyze_project_complexity`: Analyze the complexity of the tasks.
- `complexity_report`: View the complexity analysis.

### Development Workflow with Taskmaster

1.  **Project Initialization**
    -   Use `initialize_project` to set up Taskmaster.
    -   Create a `prd.md` file and use `parse_prd` to generate tasks.
    -   Use `analyze_project_complexity` and `expand_all` to break down tasks.

2.  **Daily Development Loop**
    -   Use `next_task` to get the next task to work on.
    -   Use `get_task` to review the task details.
    -   Use `update_subtask` to add implementation notes.
    -   Use `set_task_status` to mark tasks as complete.

---

_This guide provides the essential context for working on the Keystone project._
