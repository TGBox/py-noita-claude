import subprocess
import sys


def format_code() -> None:
    sys.exit(subprocess.run(["ruff", "format", "."], check=False).returncode)


def lint_code() -> None:
    sys.exit(subprocess.run(["ruff", "check", "."], check=False).returncode)


def build_native() -> None:
    """Compile the Rust simulation core (native/)."""
    from src import native

    native.build()
