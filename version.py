import os
import subprocess

def get_version():
    version = os.environ.get("CRAFT_HELPER_VERSION")
    if version:
        return version
    try:
        tag = subprocess.check_output(
            ["git", "describe", "--tags", "--abbrev=0"],
            stderr=subprocess.DEVNULL
        ).decode().strip().lstrip("v")
        return tag if tag else "0.0.0"
    except Exception:
        return "0.0.0"

__version__ = get_version()
APP_NAME = "CraftHelper"
GITHUB_REPO = "gitovsky-b/craft-helper"