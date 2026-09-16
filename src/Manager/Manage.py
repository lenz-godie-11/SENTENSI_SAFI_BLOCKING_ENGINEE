

import os
import sys


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

SRC_DIR = os.path.join(BASE_DIR, "src")

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)


def Main():
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "BlockingEngine.Config.Settings",
    )

    try:
        from django.core.management import execute_from_command_line
    except ImportError as Exc:
        raise ImportError(
            "Django could not be imported. "
            "Make sure the virtual environment is activated "
            "and Django is installed."
        ) from Exc

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    Main()