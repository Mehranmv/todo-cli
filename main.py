# local imports
from datetime import datetime
from database import SessionLocal
from models import Todo

# third party imports
import typer
from rich import print
from rich.table import Table
from rich.console import Console
from rich.prompt import Prompt
from enum import Enum

app = typer.Typer()
console = Console()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db = next(get_db())
# db = Annotated[session, get_db]


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
    todos = db.query(Todo).filter(Todo.is_completed != True).all()
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
def list_all():
    """
    list_all : Getting list of all todos (new, in progress, completed)
    """
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


@app.command(help="Updating a todo that todo is 'in progress' or 'completed'")
def update(
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
        )  # Normalize input
        if is_in_progress in ["1", "0"]:
            todo.is_in_progress = is_in_progress == "true"  # Convert to boolean
            break
        print("[bold red]Invalid input! Please enter 'True' or 'False'.[/bold red]")

    while True:
        is_completed = (
            Prompt.ask("[bold yellow]Is todo completed (1.True/0.False)?[/bold yellow]")
            .strip()
            .lower()
        )  # Normalize input
        if is_completed in ["1", "0"]:
            todo.is_completed = is_completed == "true"  # Convert to boolean
            break
        print("[bold red]Invalid input! Please enter 'True' or 'False'.[/bold red]")

    todo.is_in_progress = bool(int(is_in_progress))
    todo.is_completed = bool(int(is_completed))
    db.commit()
    print("Todo updated successfully!")


if __name__ == "__main__":
    app()
