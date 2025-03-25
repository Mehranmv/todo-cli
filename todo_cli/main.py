# local imports
from datetime import datetime
from todo_cli.database import SessionLocal, engine, Base
from todo_cli.models import Todo, Setting

# Update the existing Alembic imports at the top
from alembic.config import Config
from alembic import command
import os


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
from typing import Annotated

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


def main():
    todo = db.query(Setting).first()
    if todo.is_database_migrated is None or todo.is_database_migrated is False:
        run_migrations()
    print("CCC")
    app()
