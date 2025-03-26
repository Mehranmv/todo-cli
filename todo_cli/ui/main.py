import customtkinter as ctk
from tkinter import ttk
from datetime import datetime
from todo_cli.models import Todo, Category, UserSetting, ChangeHistory, Setting
from todo_cli.database import SessionLocal
from sqlalchemy import func
import json
import os
from tkinter import messagebox, filedialog, colorchooser
from tkcalendar import DateEntry
import tkinter as tk
from alembic import command
from alembic.config import Config

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")


class MainMenu(ctk.CTkFrame):
    def __init__(self, parent, switch_page):
        super().__init__(parent)
        self.switch_page = switch_page

        buttons = [("📋 Tasks", "list"), ("➕ Add", "add"), ("⚙️ Settings", "settings")]

        for i, (text, page) in enumerate(buttons):
            btn = ctk.CTkButton(
                self,
                text=text,
                command=lambda p=page: switch_page(p),
                font=ctk.CTkFont(size=14),
                width=120,
                height=40,
                fg_color="#2B2B2B",
                hover_color="#404040",
            )
            btn.grid(row=i, column=0, padx=10, pady=5)


class BasePage(ctk.CTkFrame):
    def __init__(self, parent, title, switch_page):
        super().__init__(parent)
        self.switch_page = switch_page

        # Header with back button
        header = ctk.CTkFrame(self)
        header.pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(
            header,
            text="← Back",
            command=lambda: switch_page("menu"),
            width=80,
            height=30,
            font=ctk.CTkFont(size=12),
        ).pack(side="left")

        ctk.CTkLabel(header, text=title, font=ctk.CTkFont(size=16, weight="bold")).pack(
            side="left", padx=10
        )


class TaskListPage(BasePage):
    def __init__(self, parent, switch_page):
        super().__init__(parent, "Task List", switch_page)
        self.db = SessionLocal()

        # Add fixed size container
        container = ctk.CTkFrame(self, width=1200, height=400)
        container.pack_propagate(False)  # Prevent size changes
        container.pack(padx=10, pady=10)

        # Minimal task list
        self.tree = ttk.Treeview(
            container,
            columns=("id", "title", "priority", "status", "due_date"),
            show="headings",
            height=15,
        )

        # Configure style
        style = ttk.Style()
        style.configure("Custom.Treeview", font=("Helvetica", 12))
        style.configure("Custom.Treeview.Heading", font=("Helvetica", 13, "bold"))

        self.tree.heading("title", text="Title")
        self.tree.heading("status", text="Status")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Load initial data
        self.load_data()

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        todos = self.db.query(Todo).filter(Todo.is_deleted != True).all()
        for todo in todos:
            status = (
                "✅" if todo.is_completed else "🔄" if todo.is_in_progress else "📝"
            )
            self.tree.insert("", "end", values=(todo.title, status))


class AddTaskPage(BasePage):
    def __init__(self, parent, switch_page):
        super().__init__(parent, "Add New Task", switch_page)
        self.db = SessionLocal()
        self._create_form()

    def _create_form(self):
        form_frame = ctk.CTkFrame(self, width=400, height=500)
        form_frame.pack_propagate(False)  # Prevent size changes
        form_frame.pack(padx=20, pady=20)

        fields = [
            ("Title", ctk.CTkEntry),
            ("Description", ctk.CTkTextbox),
            ("Priority", ctk.CTkComboBox),
            ("Due Date", DateEntry),
            ("Start Now", ctk.CTkCheckBox),
        ]

        self.entries = {}
        for i, (label, widget_type) in enumerate(fields):
            ctk.CTkLabel(form_frame, text=label + ":").grid(
                row=i, column=0, pady=5, sticky="w"
            )

            if widget_type == ctk.CTkComboBox:
                entry = ctk.CTkComboBox(form_frame, values=["LOW", "MEDIUM", "HIGH"])
                entry.set("MEDIUM")
            elif widget_type == DateEntry:
                entry = DateEntry(form_frame, date_pattern="yyyy-mm-dd")
            elif widget_type == ctk.CTkCheckBox:
                entry = ctk.CTkCheckBox(form_frame, text="")
            elif widget_type == ctk.CTkTextbox:
                entry = ctk.CTkTextbox(form_frame, height=80)
            else:
                entry = widget_type(form_frame)

            entry.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
            self.entries[label.lower().replace(" ", "_")] = entry

        submit_btn = ctk.CTkButton(
            form_frame,
            text="Add Task",
            command=self._submit_task,
            fg_color="#4CAF50",
            hover_color="#45a049",
        )
        submit_btn.grid(row=len(fields), columnspan=2, pady=20)

    def _submit_task(self):
        try:
            due_date_str = self.entries["due_date"].get()
            if not due_date_str:
                raise ValueError("Due date is required")

            due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
            if due_date < datetime.now():
                raise ValueError("Due date cannot be in the past")

            # Get selected category
            category_name = self.entries["category"].get()
            category = self.db.query(Category).filter_by(name=category_name).first()

            new_todo = Todo(
                title=self.entries["title"].get(),
                todo_body=self.entries["description"].get("1.0", "end-1c"),
                priority=self.entries["priority"].get(),
                due_date=due_date,
                is_in_progress=self.entries["start_now"].get(),
                created_at=datetime.now(),
                category=category,
            )
            self.db.add(new_todo)
            self.db.commit()
            messagebox.showinfo("Success", "Task added successfully!")
            self.master.switch_page("list")
        except ValueError as ve:
            messagebox.showerror("Validation Error", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add task: {str(e)}")


class SettingsPage(BasePage):
    def __init__(self, parent, switch_page, size="400x600"):
        super().__init__(parent, "Settings", switch_page)
        self.db = SessionLocal()
        self.geometry(size)
        self._create_form()

    def _create_form(self):
        form_frame = ctk.CTkFrame(self)
        form_frame.pack_propagate(False)  # Prevent size changes
        form_frame.pack(padx=20, pady=20)

        # Theme selection
        ctk.CTkLabel(form_frame, text="Appearance Mode:").grid(row=0, column=0, pady=5)
        self.theme_var = ctk.StringVar(value=ctk.get_appearance_mode())
        theme_menu = ctk.CTkComboBox(
            form_frame,
            values=["Dark", "Light", "System"],
            command=self._change_theme,
            variable=self.theme_var,
        )
        theme_menu.grid(row=0, column=1, padx=10, pady=5)

        # Email settings
        ctk.CTkLabel(form_frame, text="Notification Email:").grid(
            row=1, column=0, pady=5
        )
        self.email_entry = ctk.CTkEntry(form_frame)
        self.email_entry.grid(row=1, column=1, padx=10, pady=5)

        # Save button
        save_btn = ctk.CTkButton(
            form_frame,
            text="Save Settings",
            command=self._save_settings,
            fg_color="#2196F3",
            hover_color="#1976D2",
        )
        save_btn.grid(row=2, columnspan=2, pady=20)

    def _change_theme(self, choice):
        ctk.set_appearance_mode(choice)

    def _save_settings(self):
        try:
            settings = self.db.query(UserSetting).first()
            if not settings:
                settings = UserSetting()

            settings.email = self.email_entry.get()
            self.db.add(settings)
            self.db.commit()
            messagebox.showinfo("Success", "Settings saved!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")


class TodoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Todo Manager")
        self.geometry("1315x500")
        self.resizable(False, False)
        self.db = SessionLocal()
        self._setup_ui()
        self.load_data()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        """Handler for proper application closure"""
        self.db.close()
        self.destroy()

    def _setup_ui(self):
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Task List
        self.tree = ttk.Treeview(
            self.main_frame,
            columns=(
                "id",
                "title",
                "body",
                "category",
                "priority",
                "status",
                "due_date",
            ),
            show="headings",
            height=15,
        )
        self._configure_columns()
        self.tree.pack(fill="both", expand=True)

        # Action Buttons
        self.btn_frame = ctk.CTkFrame(self.main_frame)
        self.btn_frame.pack(fill="x", pady=5)

        actions = [
            ("➕ Add", self.show_add_dialog),
            ("✏️ Edit", self.show_edit_dialog),
            ("✅ Complete", self.toggle_complete),
            ("🗑️ Delete", self.delete_task),
            ("⚡ Bulk", self.bulk_operations),
            ("⚙️ Settings", self.show_settings),
            ("📁 Categories", self.show_categories),
            ("Export", self.export_tasks),
            ("Import", self.import_tasks),
        ]

        for i, (text, cmd) in enumerate(actions):
            ctk.CTkButton(self.btn_frame, text=text, command=cmd).grid(
                row=0, column=i, padx=2
            )

    def _configure_columns(self):
        columns = [
            ("id", "ID", 35),
            ("title", "Title", 200),
            ("body", "Description", 200),
            ("category", "Category", 100),
            ("priority", "Priority", 80),
            ("status", "Status", 100),
            ("due_date", "Due Date", 100),
        ]
        for col_id, heading, width in columns:
            self.tree.heading(col_id, text=heading)
            self.tree.column(col_id, width=width, anchor="center")

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        todos = self.db.query(Todo).filter(Todo.is_deleted == False).all()
        for todo in todos:
            status = self._get_status(todo)
            due_date = todo.due_date.strftime("%Y-%m-%d") if todo.due_date else ""
            category = todo.category.name if todo.category else ""
            self.tree.insert(
                "",
                "end",
                values=(
                    todo.id,
                    todo.title,
                    todo.todo_body,
                    category,
                    todo.priority,
                    status,
                    due_date,
                ),
            )

    def _get_status(self, todo):
        if todo.is_completed:
            return "✅ Completed"
        if todo.is_in_progress:
            return "🔄 In Progress"
        return "📝 New"

    def show_add_dialog(self):
        AddTodoDialog(self, self.db, self.load_data)

    def show_edit_dialog(self):
        selected = self.tree.selection()
        if selected:
            todo_id = self.tree.item(selected[0], "values")[0]
            todo = self.db.query(Todo).get(todo_id)
            EditTodoDialog(self, self.db, todo, self.load_data)

    def toggle_complete(self):
        selected = self.tree.selection()
        if selected:
            todo_id = self.tree.item(selected[0], "values")[0]
            todo = self.db.query(Todo).get(todo_id)
            todo.is_completed = not todo.is_completed
            if todo.is_completed:
                todo.complete_time = datetime.now()
            self.db.commit()
            self.load_data()

    def delete_task(self):
        selected = self.tree.selection()
        if selected:
            try:
                todo_id = self.tree.item(selected[0], "values")[0]
                todo = self.db.query(Todo).get(todo_id)
                todo.is_deleted = True
                todo.updated_at = datetime.now()
                self.db.commit()
                self.load_data()
            except Exception as e:
                self.db.rollback()
                messagebox.showerror("Error", f"Failed to delete task: {str(e)}")
            finally:
                self.db.close()
                self.db = SessionLocal()

    def show_settings(self):
        """Show settings dialog"""
        SettingsDialog(self, self.db)
        self.load_data()

    def export_tasks(self):
        try:
            tasks = self.db.query(Todo).filter(Todo.is_deleted == False).all()

            tasks_data = []
            for task in tasks:
                tasks_data.append(
                    {
                        "title": task.title,
                        "description": task.todo_body,
                        "priority": task.priority,
                        "due_date": (
                            task.due_date.isoformat() if task.due_date else None
                        ),
                        "status": (
                            "completed"
                            if task.is_completed
                            else "in_progress" if task.is_in_progress else "new"
                        ),
                        "category": task.category.name if task.category else None,
                        "category_color": (
                            task.category.color if task.category else None
                        ),
                    }
                )

            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            )

            if file_path:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(tasks_data, f, indent=4, ensure_ascii=False)

                messagebox.showinfo(
                    "Export Successful",
                    f"Exported {len(tasks_data)} tasks to:\n{file_path}",
                )

        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export tasks: {str(e)}")

    def import_tasks(self):
        try:
            file_path = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )

            if file_path:
                with open(file_path, "r", encoding="utf-8") as f:
                    tasks_data = json.load(f)

                    for task in tasks_data:
                        # Handle category
                        category = None
                        if task.get("category"):
                            category = (
                                self.db.query(Category)
                                .filter_by(name=task["category"])
                                .first()
                            )

                            if not category:
                                category = Category(
                                    name=task["category"],
                                    color=task.get("category_color", "#FFFFFF"),
                                )
                                self.db.add(category)
                                self.db.commit()

                        new_todo = Todo(
                            title=task["title"],
                            todo_body=task["description"],
                            priority=task["priority"],
                            due_date=(
                                datetime.fromisoformat(task["due_date"])
                                if task["due_date"]
                                else None
                            ),
                            is_completed=task["status"] == "completed",
                            is_in_progress=task["status"] == "in_progress",
                            category=category,
                        )
                        self.db.add(new_todo)

                    self.db.commit()
                    self.load_data()
                    messagebox.showinfo(
                        "Import Successful",
                        f"Imported {len(tasks_data)} tasks from:\n{file_path}",
                    )

        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import tasks: {str(e)}")

    def bulk_operations(self):
        selected = self.tree.selection()
        if not selected:
            return

        menu = tk.Menu(self, tearoff=0)
        menu.add_command(
            label="Mark Complete", command=lambda: self._bulk_update(status="complete")
        )
        menu.add_command(
            label="Mark In Progress",
            command=lambda: self._bulk_update(status="progress"),
        )
        menu.add_command(label="Delete Tasks", command=self._bulk_delete)
        menu.tk_popup(*self.winfo_pointerxy())

    def _bulk_update(self, status):
        selected = self.tree.selection()
        for item in selected:
            todo_id = self.tree.item(item, "values")[0]
            todo = self.db.query(Todo).get(todo_id)
            if status == "complete":
                todo.is_completed = True
                todo.complete_time = datetime.now()
            elif status == "progress":
                todo.is_in_progress = not todo.is_in_progress
        self.db.commit()
        self.load_data()

    def _bulk_delete(self):
        selected = self.tree.selection()
        if not selected:
            return

        confirm = messagebox.askyesno(
            "Confirm Delete", f"Are you sure you want to delete {len(selected)} tasks?"
        )
        if not confirm:
            return

        for item in selected:
            todo_id = self.tree.item(item, "values")[0]
            todo = self.db.query(Todo).get(todo_id)
            todo.is_deleted = True
        self.db.commit()
        self.load_data()

    def show_categories(self):
        """Show category management dialog"""
        CategoryManagerDialog(self, self.db, self.load_data)


class BaseDialog(ctk.CTkToplevel):
    """Base class for all dialogs"""

    def __init__(self, parent, title, size="400x400"):
        super().__init__(parent)
        self.title(title)
        self.geometry(size)
        self.resizable(False, False)
        self.grab_set()
        self.transient(parent)
        self._create_widgets()

    def _create_widgets(self):
        raise NotImplementedError


class AddTodoDialog(BaseDialog):
    def __init__(self, parent, db, callback):
        self.db = db
        self.callback = callback
        super().__init__(parent, "Add New Task")

    def _create_widgets(self):
        form_frame = ctk.CTkFrame(self)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)

        fields = [
            ("title", "Title:", ctk.CTkEntry),
            ("description", "Description:", ctk.CTkTextbox, {"height": 140}),
            (
                "priority",
                "Priority:",
                ctk.CTkComboBox,
                {"values": ["LOW", "MEDIUM", "HIGH"]},
            ),
            ("due_date", "Due Date:", DateEntry, {"date_pattern": "yyyy-mm-dd"}),
            (
                "category",
                "Category:",
                ctk.CTkComboBox,
                {"values": self._get_categories()},
            ),
        ]

        self.entries = {}
        for row, (key, label, widget, *args) in enumerate(fields):
            ctk.CTkLabel(form_frame, text=label).grid(
                row=row, column=0, pady=5, sticky="w"
            )
            entry = widget(form_frame, **args[0] if args else {})
            entry.grid(row=row, column=1, padx=10, pady=5, sticky="ew")
            self.entries[key] = entry

        ctk.CTkButton(
            form_frame, text="Add Task", command=self._submit, fg_color="#4CAF50"
        ).grid(row=len(fields) + 1, columnspan=2, pady=20)

    def _submit(self):
        try:
            new_todo = Todo(
                title=self.entries["title"].get(),
                todo_body=self.entries["description"].get("1.0", "end-1c"),
                priority=self.entries["priority"].get(),
                due_date=datetime.strptime(self.entries["due_date"].get(), "%Y-%m-%d"),
                created_at=datetime.now(),
                updated_at=datetime.now(),
                category_id=self._get_category_id(),
            )
            self.db.add(new_todo)
            self.db.commit()
            self.callback()
            self.destroy()
        except Exception as e:
            self.db.rollback()
            messagebox.showerror("Error", f"Failed to add task: {str(e)}")

    def _get_categories(self):
        return [c.name for c in self.db.query(Category).all()]

    def _get_category_id(self):
        category_name = self.entries["category"].get()
        if category_name:
            return self.db.query(Category.id).filter_by(name=category_name).scalar()
        return None


class EditTodoDialog(ctk.CTkToplevel):
    def __init__(self, parent, db, todo, callback):
        super().__init__(parent)
        self.title("Edit Task")
        self.geometry("400x500")
        self.db = db
        self.todo = todo
        self.callback = callback

        # Form widgets
        self.entries = {}
        self._create_form()

        self.grab_set()
        self.transient(parent)

    def _create_form(self):
        form_frame = ctk.CTkFrame(self)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title Field
        ctk.CTkLabel(form_frame, text="Title:").grid(
            row=0, column=0, pady=5, sticky="w"
        )
        title_entry = ctk.CTkEntry(form_frame)
        title_entry.insert(0, self.todo.title)
        title_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.entries["title"] = title_entry

        # Description Field
        ctk.CTkLabel(form_frame, text="Description:").grid(
            row=1, column=0, pady=5, sticky="w"
        )
        desc_entry = ctk.CTkTextbox(form_frame, height=80)
        desc_entry.insert("1.0", self.todo.todo_body)
        desc_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self.entries["description"] = desc_entry

        # Priority Field
        ctk.CTkLabel(form_frame, text="Priority:").grid(
            row=2, column=0, pady=5, sticky="w"
        )
        priority_combo = ctk.CTkComboBox(form_frame, values=["LOW", "MEDIUM", "HIGH"])
        priority_combo.set(self.todo.priority)
        priority_combo.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        self.entries["priority"] = priority_combo

        # Due Date Field
        ctk.CTkLabel(form_frame, text="Due Date:").grid(
            row=3, column=0, pady=5, sticky="w"
        )
        due_date = DateEntry(form_frame, date_pattern="yyyy-mm-dd")
        if self.todo.due_date:
            due_date.set_date(self.todo.due_date)
        due_date.grid(row=3, column=1, padx=10, pady=5, sticky="ew")
        self.entries["due_date"] = due_date

        # Status Checkboxes
        status_frame = ctk.CTkFrame(form_frame)
        status_frame.grid(row=4, columnspan=2, pady=10)

        self.in_progress_var = ctk.BooleanVar(value=self.todo.is_in_progress)
        in_progress_check = ctk.CTkCheckBox(
            status_frame, text="In Progress", variable=self.in_progress_var
        )
        in_progress_check.pack(side="left", padx=10)

        self.completed_var = ctk.BooleanVar(value=self.todo.is_completed)
        completed_check = ctk.CTkCheckBox(
            status_frame, text="Completed", variable=self.completed_var
        )
        completed_check.pack(side="left", padx=10)

        # Category Field
        ctk.CTkLabel(form_frame, text="Category:").grid(
            row=5, column=0, pady=5, sticky="w"
        )
        category_combo = ctk.CTkComboBox(form_frame, values=self._get_categories())
        self.entries["category"] = category_combo
        category_combo.grid(row=5, column=1, padx=10, pady=5, sticky="ew")

        # Save Button
        save_btn = ctk.CTkButton(
            form_frame,
            text="Save Changes",
            command=self._save_changes,
            fg_color="#4CAF50",
            hover_color="#45a049",
        )
        save_btn.grid(row=6, columnspan=2, pady=20)

    def _get_categories(self):
        return [c.name for c in self.db.query(Category).all()]

    def _save_changes(self):
        try:
            self.todo.title = self.entries["title"].get()
            self.todo.todo_body = self.entries["description"].get("1.0", "end-1c")
            self.todo.priority = self.entries["priority"].get()
            self.todo.due_date = datetime.strptime(
                self.entries["due_date"].get(), "%Y-%m-%d"
            )
            self.todo.is_in_progress = self.in_progress_var.get()
            self.todo.is_completed = self.completed_var.get()

            if self.todo.is_completed and not self.todo.complete_time:
                self.todo.complete_time = datetime.now()

            change = ChangeHistory(
                todo_id=self.todo.id,
                change_description=f"Updated by user at {datetime.now()}",
            )
            self.db.add(change)

            self.db.commit()
            self.callback()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save changes: {str(e)}")


class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.title("Application Settings")
        self.geometry("400x400")
        self.db = db

        # Add settings components
        self._create_form()

        self.grab_set()
        self.transient(parent)

    def _create_form(self):
        form_frame = ctk.CTkFrame(self)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)

        migration_status = self.db.query(Setting).first()
        status_text = (
            "✅ Migrated"
            if migration_status and migration_status.is_database_migrated
            else "❌ Not Migrated"
        )
        # Theme Selection
        ctk.CTkLabel(form_frame, text="App Theme:").grid(
            row=0, column=0, pady=5, sticky="w"
        )
        self.theme_combo = ctk.CTkComboBox(
            form_frame, values=["Dark", "Light", "System"], command=self._change_theme
        )
        self.theme_combo.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        # Notification Settings
        ctk.CTkLabel(form_frame, text="Email Notifications:").grid(
            row=1, column=0, pady=5, sticky="w"
        )
        self.notify_email = ctk.CTkEntry(form_frame)
        self.notify_email.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # SMTP Settings
        ctk.CTkLabel(form_frame, text="SMTP Server:").grid(
            row=2, column=0, pady=5, sticky="w"
        )
        self.smtp_server = ctk.CTkEntry(form_frame)
        self.smtp_server.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(form_frame, text="SMTP Port:").grid(
            row=3, column=0, pady=5, sticky="w"
        )
        self.smtp_port = ctk.CTkEntry(form_frame)
        self.smtp_port.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(form_frame, text="SMTP Password:").grid(
            row=4, column=0, pady=5, sticky="w"
        )
        self.smtp_password = ctk.CTkEntry(form_frame, show="*")
        self.smtp_password.grid(row=4, column=1, padx=10, pady=5, sticky="ew")

        # Add migration status
        ctk.CTkLabel(form_frame, text="Database Version:").grid(row=5, column=0, pady=5)
        ctk.CTkLabel(form_frame, text=status_text).grid(
            row=5, column=1, padx=10, pady=5
        )

        # Add migration button
        ctk.CTkButton(
            form_frame,
            text="Run Migrations",
            command=self.run_migrations,
            fg_color="#795548",
            hover_color="#6d4c41",
        ).grid(row=6, columnspan=2, pady=10)

        # Save Button
        ctk.CTkButton(
            form_frame,
            text="Save Settings",
            command=self._save_settings,
            fg_color="#2196F3",
            hover_color="#1976D2",
        ).grid(row=7, columnspan=2, pady=20)

    def _load_settings(self):
        settings = self.db.query(UserSetting).first()
        if settings:
            self.notify_email.insert(0, settings.email or "")
            self.smtp_server.insert(0, settings.smtp_server or "")
            self.smtp_port.insert(0, str(settings.smtp_port) or "")
            self.smtp_password.insert(0, settings.smtp_password or "")

    def _change_theme(self, choice):
        ctk.set_appearance_mode(choice.lower())

    def _save_settings(self):
        try:
            settings = self.db.query(UserSetting).first() or UserSetting()
            settings.email = self.notify_email.get()
            settings.smtp_server = self.smtp_server.get()
            settings.smtp_port = (
                int(self.smtp_port.get()) if self.smtp_port.get() else 587
            )
            settings.smtp_password = self.smtp_password.get()

            self.db.add(settings)
            self.db.commit()
            messagebox.showinfo("Success", "Settings saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")

    def run_migrations(self):
        try:
            # Get package directory path
            package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            alembic_ini_path = os.path.join(package_dir, "alembic.ini")

            # Configure Alembic
            alembic_cfg = Config(alembic_ini_path)
            alembic_cfg.set_main_option(
                "script_location", os.path.join(package_dir, "alembic")
            )

            # Run migrations
            command.upgrade(alembic_cfg, "head")

            # Update migration status
            if not self.db.query(Setting).first():
                migration_status = Setting(is_database_migrated=True)
                self.db.add(migration_status)
            else:
                self.db.query(Setting).update({Setting.is_database_migrated: True})

            self.db.commit()
            messagebox.showinfo(
                "Migrations", "Database migrations applied successfully!"
            )
            self.destroy()
        except Exception as e:
            messagebox.showerror("Migration Error", str(e))


class CategoryManagerDialog(ctk.CTkToplevel):
    def __init__(self, parent, db, callback):
        super().__init__(parent)
        self.title("Manage Categories")
        self.geometry("450x400")
        self.resizable(False, False)
        self.db = db
        self.callback = callback

        # Category list
        self.tree = ttk.Treeview(
            self, columns=("name", "color"), show="headings", height=10
        )
        self.tree.heading("name", text="Category Name")
        self.tree.heading("color", text="Color")
        self.tree.column("name", width=300)
        self.tree.column("color", width=150)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # Buttons
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(fill="x", pady=5)

        ctk.CTkButton(
            btn_frame,
            text="Add Category",
            command=self.add_category,
            fg_color="#4CAF50",
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="Edit Category",
            command=self.edit_category,
            fg_color="#2196F3",
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="Delete Category",
            command=self.delete_category,
            fg_color="#F44336",
        ).pack(side="left", padx=5)

        self.load_data()

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        categories = self.db.query(Category).all()
        for cat in categories:
            self.tree.insert("", "end", values=(cat.name, cat.color))

    def add_category(self):
        name_dialog = ctk.CTkInputDialog(
            text="Enter category name:", title="New Category"
        )
        name = name_dialog.get_input()

        if name:
            color = colorchooser.askcolor(title="Select Category Color")[1]
            if color:
                new_cat = Category(name=name, color=color)
                self.db.add(new_cat)
                self.db.commit()
                self.load_data()

    def edit_category(self):
        selected = self.tree.selection()
        if selected:
            old_name = self.tree.item(selected[0], "values")[0]
            category = self.db.query(Category).filter_by(name=old_name).first()

            name_dialog = ctk.CTkInputDialog(
                text=f"New name for {old_name}:", title="Edit Category"
            )
            new_name = name_dialog.get_input()

            if new_name:
                new_color = colorchooser.askcolor(
                    title="Select New Color", initialcolor=category.color
                )[1]

                category.name = new_name
                category.color = new_color
                self.db.commit()
                self.load_data()

    def delete_category(self):
        selected = self.tree.selection()
        if selected:
            name = self.tree.item(selected[0], "values")[0]
            category = self.db.query(Category).filter_by(name=name).first()

            confirm = messagebox.askyesno(
                "Confirm Delete", f"Delete category '{name}' and all its tasks?"
            )

            if confirm:
                # Delete associated todos
                self.db.query(Todo).filter_by(category_id=category.id).update(
                    {"is_deleted": True, "category_id": None}
                )

                # Delete category
                self.db.delete(category)
                self.db.commit()
                self.load_data()
                self.callback()


def main():
    app = TodoApp()
    app.mainloop()


def run_ui():
    app = TodoApp()
    app.mainloop()


