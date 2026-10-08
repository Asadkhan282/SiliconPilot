import os
import platform
import shutil
import subprocess
from pathlib import Path


def is_windows() -> bool:
    return platform.system().lower() == "windows"


def to_wsl_path(path: str) -> str:
    """
    Convert a Windows path to a WSL path.

    Example:
        D:\\project\\file.sv
        ->
        /mnt/d/project/file.sv
    """

    path_obj = Path(path).resolve()

    drive = path_obj.drive.replace(
        ":",
        "",
    ).lower()

    remainder = str(
        path_obj
    ).replace(
        path_obj.drive,
        "",
        1,
    )

    remainder = remainder.replace(
        "\\",
        "/",
    )

    return (
        f"/mnt/{drive}"
        f"{remainder}"
    )


def tool_available(
    tool_name: str,
) -> bool:
    """
    Check whether the requested tool is available.
    """

    if is_windows():

        command = [
            "wsl",
            "which",
            tool_name,
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
        )

        return (
            result.returncode == 0
        )

    return (
        shutil.which(
            tool_name
        )
        is not None
    )


def run_verilator(
    file_path: str,
) -> dict:
    """
    Run Verilator lint.

    Windows:
        Uses Verilator inside WSL.

    Linux / Streamlit Cloud:
        Uses Verilator directly.
    """

    source_path = Path(
        file_path
    )

    if not source_path.exists():

        return {
            "returncode": -1,
            "status": "file_not_found",
            "output": (
                f"RTL file not found: "
                f"{source_path}"
            ),
        }

    if not tool_available(
        "verilator"
    ):

        return {
            "returncode": -1,
            "status": "tool_not_found",
            "output": (
                "Verilator is not installed "
                "or not available in PATH."
            ),
        }

    if is_windows():

        rtl_path = to_wsl_path(
            str(source_path)
        )

        command = [
            "wsl",
            "verilator",
            "--lint-only",
            "-Wall",
            rtl_path,
        ]

    else:

        rtl_path = str(
            source_path.resolve()
        )

        command = [
            "verilator",
            "--lint-only",
            "-Wall",
            rtl_path,
        ]

    try:

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
        )

    except FileNotFoundError as exc:

        return {
            "returncode": -1,
            "status": "tool_not_found",
            "output": str(
                exc
            ),
        }

    output = (
        result.stdout
        + result.stderr
    )

    return {
        "returncode": result.returncode,
        "status": (
            "pass"
            if result.returncode == 0
            else "fail"
        ),
        "output": output,
        "command": command,
        "platform": (
            "windows_wsl"
            if is_windows()
            else "linux"
        ),
    }


if __name__ == "__main__":

    result = run_verilator(
        "examples/broken_counter.sv"
    )

    print(
        "=== SiliconPilot Verilator Tool ==="
    )

    print(
        f"Platform: "
        f"{result.get('platform')}"
    )

    print(
        f"Status: "
        f"{result.get('status')}"
    )

    print(
        f"Return code: "
        f"{result.get('returncode')}"
    )

    print()

    print(
        result.get(
            "output",
            "",
        )
    )