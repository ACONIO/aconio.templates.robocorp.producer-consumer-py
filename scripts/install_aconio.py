"""Add or update the `aconio` library to your robot project.

Usage:
```bash
python scripts/install_aconio.py <git_tag> <github_token>
```
"""

import shutil
import glob
import os
import subprocess
import sys

LIBS_PATH = "libs/"


def cleanup():
    """Remove previous installations of `aconio`."""
    directories = glob.glob(os.path.join(LIBS_PATH, "aconio*"))
    for d in directories:
        shutil.rmtree(d)


def pip_install(requirement: str, dry_run: bool = False):
    call = [sys.executable, "-m", "pip", "install"]
    if dry_run is True:
        call.extend(
            [
                "--dry-run",
                requirement,
                "--target",
                LIBS_PATH,
            ]
        )
    else:
        call.extend(
            [
                requirement,
                "--no-deps",
                "--target",
                LIBS_PATH,
            ]
        )

    subprocess.check_call(call)


def main(argv):
    if len(argv) != 3:
        print(f"Usage: {argv[0]} GIT_TAG GITHUB_TOKEN")
        exit(1)

    print("Removing previous installations...")
    cleanup()

    requirement = (
        f"git+https://{argv[2]}@github.com/ACONIO/aconio.git@{argv[1]}"
    )

    print("Validating dependencies...")
    pip_install(requirement, dry_run=True)

    print("Installing aconio library...")
    pip_install(requirement)


if __name__ == "__main__":
    main(sys.argv)
