from setuptools import setup, find_packages

setup(
    name="rich-todo",
    version="0.1.5",
    packages=["todo_cli", "todo_cli.cli", "todo_cli.ui"],
    package_dir={"todo_cli": "todo_cli"},
    include_package_data=True,
    install_requires=[
        "sqlalchemy",
        "alembic",
        "typer",
        "rich",
        "platformdirs",
        "ttkbootstrap",
    ],
    entry_points={
        "console_scripts": [
            "todo = todo_cli.cli.main:app",
            "todoui = todo_cli.ui.main:main",
        ],
    },
    author="Mehran Mirzaei",
    author_email="mehranmirzaeiv@gmail.com",
    description="A CLI tool for managing todos directly from the terminal",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    keywords="todo, cli, productivity",
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_data={"todo_cli": ["alembic.ini", "alembic/*", "alembic/versions/*"]},
)
