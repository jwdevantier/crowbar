#!/usr/bin/env python3
"""
Standalone task runner, because Poetry's task system is... deficient.

Usage: python tasks.py <task> [args...]
Or make it executable: chmod +x tasks.py && ./tasks.py <task> [args...]
"""
import argparse
import subprocess
import sys
from typing import Callable, Dict
from pathlib import Path

# Registry to store all tasks
_tasks: Dict[str, Callable] = {}


def task(name: str, description: str = ""):
    """Decorator to register a task function."""

    def decorator(f):
        task_name = name or f.__name__.replace("run_", "")
        _tasks[task_name] = f
        f._task_name = task_name
        f._task_description = description
        return f

    return decorator


def get_parser_for_task(task_name: str) -> argparse.ArgumentParser:
    """Create an ArgumentParser for a specific task."""
    task_func = _tasks[task_name]
    description = getattr(task_func, "_task_description", "")
    parser = argparse.ArgumentParser(
        prog=f"./tasks.py {task_name}", description=description
    )
    return parser


def list_tasks():
    """List all available tasks."""
    if not _tasks:
        print("No tasks available.")
        return

    print("Available tasks:")
    for name, func in _tasks.items():
        description = getattr(func, "_task_description", "")
        print(f"  {name:<15} {description}")


@task("test", "Run unit tests")
def run_tests():
    parser = get_parser_for_task("test")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument(
        "target",
        nargs="?",
        default=None,
        help="provide a pytest pattern <file>[::<test-class>][::<function>]"
    )

    args = parser.parse_args()

    cmd = [
        sys.executable,
        "-m",
        "pytest",
    ]

    if args.target:
        cmd.append(str(Path("tests") / args.target))
    else:
        cmd.append("tests")

    if args.verbose:
        cmd.append("-vv")

    result = subprocess.run(cmd)
    sys.exit(result.returncode)


@task("lint", "Run mypy type checking")
def run_lint():
    parser = get_parser_for_task("lint")
    parser.add_argument("--strict", action="store_true", help="Run in strict mode")

    args = parser.parse_args()

    cmd = [sys.executable, "-m", "mypy", "crowbar.py"]
    if args.strict:
        cmd.append("--strict")

    result = subprocess.run(cmd)
    sys.exit(result.returncode)


@task("format", "Format code with black")
def run_format():
    parser = get_parser_for_task("format")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Don't write back modified files, just return status",
    )
    parser.add_argument("--diff", action="store_true", help="Show diff of changes")

    args = parser.parse_args()

    cmd = [sys.executable, "-m", "black"]
    if args.check:
        cmd.append("--check")
    if args.diff:
        cmd.append("--diff")

    cmd.extend(["crowbar.py", "tests/"])

    result = subprocess.run(cmd)
    sys.exit(result.returncode)


@task("tox", "Run tests with tox across multiple Python versions")
def run_tox():
    parser = get_parser_for_task("tox")
    parser.add_argument("-e", "--env", help="Run specific environment (e.g., py312)")
    parser.add_argument("--recreate", action="store_true", help="Force recreation of virtual environments")

    args = parser.parse_args()

    cmd = [sys.executable, "-m", "tox"]

    if args.env:
        cmd.extend(["-e", args.env])
    if args.recreate:
        cmd.append("--recreate")

    result = subprocess.run(cmd)
    sys.exit(result.returncode)


@task("gensite", "Generate website")
def run_gensite():
    parser = get_parser_for_task("gensite")

    args = parser.parse_args()

    print("Generating site support code")
    cmd = [sys.executable, "crowbar.py", "site/sitetags.py"]
    result = subprocess.run(cmd, check=True)
    print("Generating site")
    cmd = [sys.executable, "site/gensite.py"]
    result = subprocess.run(cmd, check=True)

    sys.exit(result.returncode)


def main():
    """Main entry point for task running."""
    if len(sys.argv) < 2:
        list_tasks()
        sys.exit(1)

    task_name = sys.argv[1]

    if task_name in ["-h", "--help"]:
        list_tasks()
        return

    if task_name not in _tasks:
        print(f"Unknown task: {task_name}")
        list_tasks()
        sys.exit(1)

    # Remove the task name from sys.argv so argparse works correctly
    sys.argv = [f"./tasks.py {task_name}"] + sys.argv[2:]

    # Run the task
    _tasks[task_name]()


if __name__ == "__main__":
    main()
