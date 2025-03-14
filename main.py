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


def main():
    print("[bold green]Welcome To [red]TODO APP[/red][/bold green]")
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
            str(todo.is_in_progress),
            style=row_style,
        )
    table.caption = "[red]in progress todo's are in green[/red]"
    console.print(table)


if __name__ == "__main__":
    typer.run(main)
