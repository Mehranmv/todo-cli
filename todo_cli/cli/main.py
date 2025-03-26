# local imports
from datetime import datetime
from todo_cli.database import SessionLocal, engine, Base
from todo_cli.models import Todo, Setting, UserSetting, Category
from todo_cli.ui.main import run_ui

# Update the existing Alembic imports at the top
from alembic.config import Config
from alembic import command
import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys


def run_migrations():
    # Get the package directory path
    package_dir = os.path.dirname(os.path.abspath(__file__))
    alembic_ini_path = os.path.join(package_dir, "alembic.ini")
    alembic_cfg = Config(alembic_ini_path)
    command.upgrade(alembic_cfg, "head")


# third party imports
import typer
from rich import print
from rich.table import Table
from rich.console import Console
from rich.prompt import Prompt
from enum import Enum
from typing import Annotated, List

app = typer.Typer()
console = Console()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db = next(get_db())


class Priority(str, Enum):
    LOW = "1" or "LOW"
    MEDIUM = "2" or "MEDIUM"
    HIGH = "3" or "HIGH"


class InProgress(str, Enum):
    TRUE = "1"
    FALSE = "2"


@app.command(help="Display a list of todos that are not completed.")
def list():
    """
    Display a list of todos that are not completed.
    """
    print("[bold white]Todos List :[/bold white]")
    todos = (
        db.query(Todo).filter(Todo.is_completed != True, Todo.is_deleted != True).all()
    )
    table = Table("Id", "Title", "Body", "Priority", "In Progress")
    for todo in todos:
        row_style = "green" if todo.is_in_progress else "white"
        if todo.priority == "LOW":
            priority_color = "yellow"
        elif todo.priority == "MEDIUM":
            priority_color = "blue"
        else:
            priority_color = "purple"
        table.add_row(
            str(todo.id),
            todo.title,
            todo.todo_body,
            f"[{priority_color}]{todo.priority}[/{priority_color}]",
            ":heavy_check_mark:" if todo.is_in_progress else ":x:",
            style=row_style,
        )
    table.caption = "[red]in progress todo's are in green[/red]"
    console.print(table)


@app.command(help="Getting list of all todos (new, in progress, completed)")
def all():
    """
    list_all : Getting list of all todos (new, in progress, completed)
    """
    todos = db.query(Todo).filter(Todo.is_deleted != True).all()
    table = Table("Id", "Title", "Body", "Priority", "In Progress", "Completed")
    for todo in todos:
        if todo.is_in_progress:
            row_style = "green"
        elif todo.is_completed:
            row_style = "yellow"
        else:
            row_style = "white"
        if todo.priority == "LOW":
            priority_color = "yellow"
        elif todo.priority == "MEDIUM":
            priority_color = "blue"
        else:
            priority_color = "purple"

        table.add_row(
            str(todo.id),
            todo.title,
            todo.todo_body,
            f"[{priority_color}]{todo.priority}[/{priority_color}]",
            ":heavy_check_mark:" if todo.is_in_progress else ":x:",
            ":heavy_check_mark:" if todo.is_completed else ":x:",
            style=row_style,
        )
    table.caption = "[green]in progress todos are in green[/green] \n[red]completed todos are in red[/red]"
    console.print(table)


@app.command(help="Adding a todo")
def add():
    """
    Add a new todo to the database.
    """
    title = Prompt.ask("[bold]Title of the todo[/bold]")
    body = Prompt.ask("[bold]Body of the todo[/bold]")

    while True:
        priority = Prompt.ask(
            "[bold]Priority of the todo (1. Low, 2. Medium, 3. High)[/bold]",
        )
        if priority in [p.value for p in Priority]:
            priority = Priority(priority).name
            break
        print("[bold red]Invalid priority! Please enter 1, 2, or 3.[/bold red]")

    while True:
        is_in_progress = Prompt.ask(
            "[bold]Is the todo in progress? (1. True, 2. False)[/bold]"
        )
        if is_in_progress in [s.value for s in InProgress]:
            break
        print("[bold red]Invalid status! Please enter 1 or 2.[/bold red]")

    todo = Todo(
        created_at=datetime.now(),
        title=title,
        todo_body=body,
        priority=priority,
        is_in_progress=(is_in_progress == InProgress.TRUE.value),
        is_completed=False,
    )

    # Add to the database
    db.add(todo)
    db.commit()
    print("[bold green]Todo added successfully![/bold green]")
    list()


@app.command(name="progress", help="Updating a todo that todo is 'in progress'")
def add_to_in_progress(
    todo_id: int,
):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        print("[red bold]Todo not found![/red bold]")
        return
    list()

    while True:
        is_in_progress = (
            Prompt.ask("[bold green]Is todo in progress (1.True/0.False)?[/bold green]")
            .strip()
            .lower()
        )
        if is_in_progress in ["1", "0"]:
            todo.is_in_progress = is_in_progress == "true"
            break
        print("[bold red]Invalid input! Please enter 'True' or 'False'.[/bold red]")

    todo.is_in_progress = bool(int(is_in_progress))
    db.commit()
    print("[green bold]Todo added to in progress todos successfully![/green bold]")
    list()


@app.command(name="completed")
def get_in_completed(todo_id: int):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        print("[red bold]Todo not found![/red bold]")
        return
    while True:
        is_completed = (
            Prompt.ask(
                "[bold yellow]Is todo completed (1.True / 0.False)?[/bold yellow]"
            )
            .strip()
            .lower()
        )
        if int(is_completed) == 1:
            todo.is_completed = True
            todo.is_in_progress = False
            db.commit()
            break
        print("[bold red]Invalid input! Please enter 'True' or 'False'.[/bold red]")

        print("[green bold]Todo added to completed todos successfully![/green bold]")
        list()


@app.command(help="Delete a todo from app")
def delete(todo_id: int):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        print("[red bold]Todo not found![/red bold]")
        return
    todo.is_deleted = True
    db.commit()
    print("[green bold] Todo deleted successfully [/green bold]")
    list()


@app.command(help="Delete al todo from app")
def delete_all(
    force: Annotated[
        bool, typer.Option(prompt="Are you sure you want to delete all todos?")
    ],
):
    todos = db.query(Todo).all()
    if force:
        for todo in todos:
            todo.is_deleted = True
        db.commit()
        print("[green bold] Todos deleted successfully [/green bold]")
        list()


@app.command(help="Get history off all todos (include deleted todos)")
def history():
    todos = db.query(Todo).all()
    table = Table("Id", "Title", "Body", "Priority", "In Progress", "Completed")
    for todo in todos:
        if todo.is_in_progress:
            row_style = "green"
        elif todo.is_completed:
            row_style = "yellow"
        else:
            row_style = "white"
        if todo.priority == "LOW":
            priority_color = "yellow"
        elif todo.priority == "MEDIUM":
            priority_color = "blue"
        else:
            priority_color = "purple"

        table.add_row(
            str(todo.id),
            todo.title,
            todo.todo_body,
            f"[{priority_color}]{todo.priority}[/{priority_color}]",
            ":heavy_check_mark:" if todo.is_in_progress else ":x:",
            ":heavy_check_mark:" if todo.is_completed else ":x:",
            style=row_style,
        )
    table.caption = "[green]in progress todos are in green[/green] \n[red]completed todos are in red[/red]"
    console.print(table)


@app.command(help="Get statistics of todos.")
def stats():
    total_todos = db.query(Todo).count()
    completed_todos = db.query(Todo).filter(Todo.is_completed == True).count()
    in_progress_todos = db.query(Todo).filter(Todo.is_in_progress == True).count()
    deleted_todos = db.query(Todo).filter(Todo.is_deleted == True).count()

    print(f"[bold]Total Todos:[/bold] {total_todos}")
    print(f"[bold]Completed Todos:[/bold] {completed_todos}")
    print(f"[bold]In Progress Todos:[/bold] {in_progress_todos}")
    print(f"[bold]Deleted Todos:[/bold] {deleted_todos}")


@app.command(help="Edit a todo.")
def edit(todo_id: int):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        print("[red]Todo not found![/red]")
        return
    title = Prompt.ask("[bold]New Title : [/bold]", default=todo.title)
    body = Prompt.ask("[bold]New Body : [/bold]", default=todo.todo_body)
    todo.title = title
    todo.todo_body = body
    db.commit()
    print("[green]Todo updated successfully![/green]")


@app.command(help="Add a due date to a todo.")
def add_due_date(todo_id: int, due_date: str):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        print("[red]Todo not found![/red]")
        return
    todo.due_date = datetime.strptime(due_date, "%Y-%m-%d")
    db.commit()
    print("[green]Due date added successfully![/green]")


@app.command(help="Filter todos by date.")
def filter_by_date(start_date: str, end_date: str):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    todos = (
        db.query(Todo)
        .filter(
            Todo.created_at >= start, Todo.created_at <= end, Todo.is_deleted != True
        )
        .all()
    )
    table = Table("Id", "Title", "Body", "Priority", "In Progress")
    for todo in todos:
        row_style = "green" if todo.is_in_progress else "white"
        priority_color = (
            "yellow"
            if todo.priority == "LOW"
            else "blue" if todo.priority == "MEDIUM" else "purple"
        )
        table.add_row(
            str(todo.id),
            todo.title,
            todo.todo_body,
            f"[{priority_color}]{todo.priority}[/{priority_color}]",
            ":heavy_check_mark:" if todo.is_in_progress else ":x:",
            style=row_style,
        )
    console.print(table)


@app.command(help="Export todos to a JSON file.")
def export(file_path: str):
    todos = db.query(Todo).filter(Todo.is_deleted != True).all()
    with open(file_path, "w") as jsonfile:
        json.dump([todo.to_dict() for todo in todos], jsonfile, default=str)
    print(f"[green]Todos exported to {file_path} successfully![/green]")


@app.command(help="Load todos from a JSON file.")
def load(file_path: str):
    with open(file_path, "r") as file:
        todos = json.load(file)
        for todo_data in todos:
            todo = Todo(
                title=todo_data["Title"],
                todo_body=todo_data["Body"],
                priority=todo_data["Priority"],
                is_in_progress=todo_data["In Progress"],
                is_completed=todo_data["Completed"],
                created_at=datetime.now(),
                due_date=todo_data["Due Date"] if "Due Date" in todo_data else None,
                complete_time=(
                    todo_data["Complete Time"] if "Complete Time" in todo_data else None
                ),
                is_deleted=(
                    todo_data["Is Deleted"] if "Is Deleted" in todo_data else False
                ),
            )
            db.add(todo)
    db.commit()
    print(f"[green]Todos loaded from {file_path} successfully![/green]")


@app.command(help="Send reminder emails for upcoming todos.")
def send_reminders():
    settings = db.query(UserSetting).first()
    if not settings or not settings.email:
        print("[red]No email set for reminders.[/red]")
        return

    todos = (
        db.query(Todo).filter(Todo.due_date != None, Todo.is_completed == False).all()
    )
    for todo in todos:
        if (
            todo.due_date
            and (todo.due_date - datetime.now()).total_seconds() / 60
            <= settings.reminder_time
        ):
            send_email(settings.email, todo)


@app.command(help="Set user SMTP settings.")
def set_smtp_settings(email: str, smtp_server: str, smtp_port: int, smtp_password: str):
    settings = UserSetting(
        email=email,
        smtp_server=smtp_server,
        smtp_port=smtp_port,
        smtp_password=smtp_password,
    )
    db.add(settings)
    db.commit()
    print(f"[green]SMTP settings updated successfully![/green]")


def send_email(to_email, todo):
    settings = db.query(UserSetting).first()
    if not settings:
        print("[red]SMTP settings not found! Please set them first.[/red]")
        return

    from_email = settings.email
    password = settings.smtp_password
    smtp_server = settings.smtp_server
    smtp_port = settings.smtp_port

    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = f"Reminder: {todo.title}"

    body = f"Don't forget to complete your task: {todo.title}\n\nDetails: {todo.todo_body}\nDue Date: {todo.due_date}"
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(from_email, password)
        server.send_message(msg)

    print(f"[green]Reminder sent for {todo.title} to {to_email}.[/green]")


@app.command(help="Add a new category.")
def add_category(name: str, color: str):
    category = Category(name=name, color=color)
    db.add(category)
    db.commit()
    print(f"[green]Category '{name}' added successfully![/green]")


@app.command(help="Set user settings.")
def set_user_settings(email: str, theme: str = "light", reminder_time: int = 30):
    settings = UserSetting(email=email, reminder_time=reminder_time)
    db.add(settings)
    db.commit()
    print(f"[green]User settings updated successfully![/green]")


@app.command()
def ui():
    """Run the graphical interface"""
    run_ui()


# Add to existing CLI commands
@app.command()
def category_add(name: str, color: str = "#FFFFFF"):
    """Add new category"""
    with SessionLocal() as db:
        category = Category(name=name, color=color)
        db.add(category)
        db.commit()
    print(f"Added category: {name}")


@app.command()
def category_list():
    """List all categories"""
    with SessionLocal() as db:
        categories = db.query(Category).all()
        for cat in categories:
            print(f"{cat.name} ({cat.color})")


@app.command()
def category_delete(name: str):
    """Delete a category"""
    with SessionLocal() as db:
        category = db.query(Category).filter_by(name=name).first()
        if category:
            db.delete(category)
            db.commit()
            print(f"Deleted category: {name}")
        else:
            print("Category not found")


@app.command()
def bulk_update(status: str, ids: List[int]):
    """Bulk update task statuses"""
    with SessionLocal() as db:
        for task_id in ids:
            todo = db.query(Todo).get(task_id)
            if todo:
                if status == "complete":
                    todo.is_completed = True
                elif status == "progress":
                    todo.is_in_progress = True
        db.commit()
    print(f"Updated {len(ids)} tasks")


@app.command()
def bulk_delete(ids: List[int]):
    """Bulk delete tasks"""
    with SessionLocal() as db:
        for task_id in ids:
            todo = db.query(Todo).get(task_id)
            if todo:
                todo.is_deleted = True
        db.commit()
    print(f"Deleted {len(ids)} tasks")


@app.command()
def db_upgrade():
    """Run database migrations"""
    run_migrations()
    print("Database migrations applied")



def main():
    todo = db.query(Setting).first()
    if todo.is_database_migrated is None or todo.is_database_migrated is False:
        run_migrations()
    if len(sys.argv) > 1 and sys.argv[1] == "ui":
        run_ui()
    else:
        app()
