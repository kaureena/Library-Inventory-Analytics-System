"""Simple environment validator (portfolio)."""

import sys

REQUIRED_MAJOR = 3
REQUIRED_MINOR = 10


def main() -> None:
    if sys.version_info < (REQUIRED_MAJOR, REQUIRED_MINOR):
        raise SystemExit(f"Python {REQUIRED_MAJOR}.{REQUIRED_MINOR}+ required")
    print("OK: Python version", sys.version.split()[0])


if __name__ == "__main__":
    main()
