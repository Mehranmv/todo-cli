# local imports
from database import SessionLocal
from models import Todo

# third party imports
import typer
from rich import print
from rich.table import Table
from rich.console import Console

app = typer.Typer()
console = Console()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db = next(get_db())


@app.command(help="Display a list of todos that are not completed.")
def list():
    """
    Display a list of todos that are not completed.
    """
    print("[bold white]Todos List :[/bold white]")
    todos = db.query(Todo).filter(Todo.is_completed != True).all()
    table = Table("id", "title", "body", "priority", "in progress")
    for todo in todos:
        row_style = "green" if todo.is_in_progress else "white"
        table.add_row(
            str(todo.id),
            todo.title,
            todo.todo_body,
            todo.priority,
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
    todos = db.query(Todo).filter(Todo.is_completed != True).all()
    table = Table("id", "title", "body", "priority", "in progress", "is completed")
    for todo in todos:
        if todo.is_in_progress:
            row_style = "green"
        elif todo.is_completed:
            row_style = "yellow"
        else:
            row_style = "white"
        table.add_row(
            str(todo.id),
            todo.title,
            todo.todo_body,
            todo.priority,
            ":heavy_check_mark:" if todo.is_in_progress else ":x:",
            ":heavy_check_mark:" if todo.is_completed else ":x:",
            style=row_style,
        )
    table.caption = "[green]in progress todos are in green[/green] \n[red]completed todos are in red[/red]"
    console.print(table)


if __name__ == "__main__":
    app()
