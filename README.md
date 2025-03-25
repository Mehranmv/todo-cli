# Todo CLI 🚀

[![Python 3.6+](https://img.shields.io/badge/Python-3.6%2B-blue.svg)](https://www.python.org/)
[![PyPI Version](https://img.shields.io/pypi/v/rich-todo.svg)](https://pypi.org/project/rich-todo/)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/Mehranmv/todo-cli)
A beautiful terminal-based todo manager with database persistence and rich visual feedback. Organize tasks directly from your command line with style! ✨


## Features 🌟

- 🎨 **Rich Terminal UI** with colored output and emojis
- 📂 **SQLite Database** with automatic migrations
- 🏷️ **Priority Levels** (Low/Medium/High)
- 🔄 **Progress Tracking** (New/In Progress/Completed)
- 📆 **Automatic Timestamping** for task creation
- 🗑️ **Safe Deletion** with soft delete functionality
- 📦 **Packaged Application** easy installation via PyPI

## Installation 💻

```bash
# Install from PyPI
pip install todo-cli

# Install development version
pip install git+https://github.com/mehranmv/todo-cli.git
```

## Usage 🛠️

```bash
# Add a new todo (interactive prompt)
todo add

# List active todos
todo list

# List all todos including completed
todo all

# Mark todo as in progress
todo progress <todo_id>

# Complete a todo
todo completed <todo_id>

# Soft delete a todo
todo delete <todo_id>

# Show full history (including deleted)
todo history

# Delete all todos (with confirmation)
todo delete-all
```

## Configuration ⚙️

The application automatically handles database storage:
- **Virtual Environments**: Stores data in `{venv_path}/todo_data`
- **Global Installations**: Uses platform-appropriate user data directory

## Documentation 📚

For advanced usage and contribution guidelines, see our [documentation](docs/README.md).




---

Developed with ❤️ by Mehran Mirzaei  
📧 Contact: [mehranmirzaeiv@gmail.com](mailto:mehranmirzaeiv@gmail.com)  
```