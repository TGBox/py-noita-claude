import os
import sys

import PyInstaller.__main__

from src import native


def main() -> None:
    if len(sys.argv) > 1:
        args = sys.argv[1:]
    else:
        native.build()
        args = [
            "--noconfirm",
            "--onedir",
            "--windowed",
            "--add-data",
            f"assets{os.pathsep}assets",
            "--add-binary",
            f"{native.library_path()}{os.pathsep}.",
            "src/main.py",
            "--name",
            "Cloita",
        ]
    PyInstaller.__main__.run(args)


if __name__ == "__main__":
    main()
