from setuptools import setup

setup(
    name="rich-todo",
    version="0.1.0",
    packages=["todo_cli"],
    package_dir={"todo_cli": "todo_cli"},
    include_package_data=True,
    install_requires=["sqlalchemy", "alembic", "typer", "rich", "platformdirs"],
    entry_points={
        "console_scripts": [
            "todo=todo_cli.main:app",
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
