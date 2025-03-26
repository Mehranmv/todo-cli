# Todo Manager 🚀

[![Python 3.6+](https://img.shields.io/badge/Python-3.6%2B-blue.svg)](https://www.python.org/)
[![PyPI Version](https://img.shields.io/pypi/v/rich-todo.svg)](https://pypi.org/project/rich-todo/)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/Mehranmv/todo-cli)

A modern cross-platform task manager with **dual interface** - Beautiful GUI ✨ and powerful CLI 💻

![UI Screenshot](https://raw.githubusercontent.com/Mehranmv/todo-cli/refs/heads/master/screenshots/gui.png)

## Features 🌟

### 🖥️ Modern GUI Interface
- **Windows 11 Style** with fluent design elements
- **Dark/Light Themes** with system auto-detection
- **Responsive Layout** that adapts to screen size
- **Task Preview Panel** with rich markdown support
- **Drag-and-Drop** task prioritization
- **Visual Category Tags** with custom colors
- **Bulk Operations** (multi-select delete/update)
- **Real-time Search** with instant filtering

### 📊 Interactive Dashboard
- Priority distribution pie chart
- Completion rate timeline graph
- Category usage heatmap
- Quick stats overview

### ⚙️ Advanced UI Features
- Customizable column layouts
- Sortable task lists (click headers)
- Progress percentage indicators
- Due date calendar picker
- Notification system with reminders
- Export/Import UI (JSON/CSV)
- Category color picker dialog

## Installation 💻

```bash
# Install with GUI support
pip install rich-todo

# Launch GUI version
todoui

# Or use CLI version
todo --help
```

## UI Usage 🖱️

### Main Interface
![Main Window](https://via.placeholder.com/600x300.png?text=Main+Interface)

1. **Quick Add Bar** - Type and press Enter
2. **Smart Filters** - Click to toggle views
3. **Priority Badges** - Drag to reorder
4. **Context Menu** - Right-click for actions

### Key Shortcuts
| Shortcut | Action                |
|----------|-----------------------|
| Ctrl+N   | New Task              |
| Ctrl+F   | Search                |
| Ctrl+S   | Save Changes          |
| Ctrl+E   | Export Tasks          |
| Alt+C    | Category Manager      |
| F5       | Refresh List          |

## Theme Customization 🎨
Choose from 6 built-in themes or create your own:
```bash
# Set theme (dark/light/system)
todoui --theme dark

# Custom theme colors
todoui --primary-color #2ecc71 --accent-color #3498db
```

## Documentation 📚
Explore our [UI Guide](docs/UI_GUIDE.md) for:
- Custom view configurations
- Notification preferences
- Data visualization tips
- Keyboard shortcut cheatsheet

---

Developed with ❤️ by Mehran Mirzaei  
📧 Contact: [mehranmirzaeiv@gmail.com](mailto:mehranmirzaeiv@gmail.com)  
```