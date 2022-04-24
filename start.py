import os
import platform
from pathlib import Path

root_path = Path(__file__).parent
os.chdir(str(root_path.absolute()))
SYSTEM = platform.system()


def install_dependencies():
    requirements_path = root_path / "requirements.txt"

    if SYSTEM == "Windows":
        install_command = "pip install wheel -r {requirements_path} --quiet"
    else:
        install_command = (
            "python3 -m pip install -U wheel -r {requirements_path} --quiet"
        )

    os.system(install_command.format(requirements_path=requirements_path))


def start_bot():
    if SYSTEM == "Windows":
        start_command = "python -m bot"
    else:
        start_command = "python3 -m bot"

    os.system(start_command)


def main():
    install_dependencies()
    __import__("update").main()
    start_bot()

    if SYSTEM == "Windows":
        os.system("pause")


if __name__ == "__main__":
    main()
