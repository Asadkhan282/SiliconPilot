import platform
import shutil
import subprocess
from pathlib import Path


def is_windows() -> bool:
    return platform.system().lower() == "windows"


def to_wsl_path(
    path: str,
) -> str:
    """
    Convert Windows path to WSL path.

    Example:

        D:\\project\\file.sv

    becomes:

        /mnt/d/project/file.sv
    """

    path_obj = Path(
        path
    ).resolve()

    drive = (
        path_obj.drive
        .replace(
            ":",
            "",
        )
        .lower()
    )

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
    Check for a tool either in WSL or native Linux.
    """

    if is_windows():

        result = subprocess.run(
            [
                "wsl",
                "which",
                tool_name,
            ],
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


def run_iverilog_simulation(
    rtl_file: str,
    testbench_file: str,
    output_file: str = (
        "outputs/simulation.out"
    ),
) -> dict:
    """
    Compile and run RTL simulation.

    Windows:
        Uses WSL:
            iverilog
            vvp

    Linux / Streamlit Cloud:
        Uses native:
            iverilog
            vvp
    """

    rtl_path = Path(
        rtl_file
    )

    testbench_path = Path(
        testbench_file
    )

    output_path = Path(
        output_file
    )

    # -----------------------------------------------------
    # Basic file checks
    # -----------------------------------------------------

    if not rtl_path.exists():

        return {
            "status": "rtl_not_found",
            "passed": False,
            "compile_output": (
                f"RTL file not found: "
                f"{rtl_path}"
            ),
            "simulation_output": "",
        }

    if not testbench_path.exists():

        return {
            "status": "testbench_not_found",
            "passed": False,
            "compile_output": (
                f"Testbench not found: "
                f"{testbench_path}"
            ),
            "simulation_output": "",
        }

    # -----------------------------------------------------
    # Tool checks
    # -----------------------------------------------------

    if not tool_available(
        "iverilog"
    ):

        return {
            "status": "tool_not_found",
            "passed": False,
            "compile_output": (
                "iverilog is not installed "
                "or not available."
            ),
            "simulation_output": "",
        }

    if not tool_available(
        "vvp"
    ):

        return {
            "status": "tool_not_found",
            "passed": False,
            "compile_output": (
                "vvp is not installed "
                "or not available."
            ),
            "simulation_output": "",
        }

    # -----------------------------------------------------
    # Ensure output directory exists
    # -----------------------------------------------------

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # -----------------------------------------------------
    # Build platform-specific commands
    # -----------------------------------------------------

    if is_windows():

        rtl_exec = to_wsl_path(
            str(rtl_path)
        )

        tb_exec = to_wsl_path(
            str(testbench_path)
        )

        output_exec = to_wsl_path(
            str(output_path)
        )

        compile_command = [
            "wsl",
            "iverilog",
            "-g2012",
            "-o",
            output_exec,
            rtl_exec,
            tb_exec,
        ]

        run_command = [
            "wsl",
            "vvp",
            output_exec,
        ]

        platform_name = (
            "windows_wsl"
        )

    else:

        rtl_exec = str(
            rtl_path.resolve()
        )

        tb_exec = str(
            testbench_path.resolve()
        )

        output_exec = str(
            output_path.resolve()
        )

        compile_command = [
            "iverilog",
            "-g2012",
            "-o",
            output_exec,
            rtl_exec,
            tb_exec,
        ]

        run_command = [
            "vvp",
            output_exec,
        ]

        platform_name = "linux"

    # -----------------------------------------------------
    # Compile
    # -----------------------------------------------------

    try:

        compile_result = subprocess.run(
            compile_command,
            capture_output=True,
            text=True,
        )

    except FileNotFoundError as exc:

        return {
            "status": "tool_not_found",
            "passed": False,
            "compile_output": str(
                exc
            ),
            "simulation_output": "",
            "platform": (
                platform_name
            ),
        }

    compile_output = (
        compile_result.stdout
        + compile_result.stderr
    )

    if compile_result.returncode != 0:

        return {
            "status": "compile_fail",
            "passed": False,
            "compile_output": (
                compile_output
            ),
            "simulation_output": "",
            "platform": (
                platform_name
            ),
            "compile_command": (
                compile_command
            ),
        }

    # -----------------------------------------------------
    # Run simulation
    # -----------------------------------------------------

    try:

        run_result = subprocess.run(
            run_command,
            capture_output=True,
            text=True,
        )

    except FileNotFoundError as exc:

        return {
            "status": "tool_not_found",
            "passed": False,
            "compile_output": (
                compile_output
            ),
            "simulation_output": str(
                exc
            ),
            "platform": (
                platform_name
            ),
        }

    simulation_output = (
        run_result.stdout
        + run_result.stderr
    )

    passed = (
        run_result.returncode == 0
        and "TEST_PASS"
        in simulation_output
        and "TEST_FAIL"
        not in simulation_output
    )

    # -----------------------------------------------------
    # Final result
    # -----------------------------------------------------

    return {
        "status": (
            "pass"
            if passed
            else "simulation_fail"
        ),
        "passed": passed,
        "compile_output": (
            compile_output
        ),
        "simulation_output": (
            simulation_output
        ),
        "compile_returncode": (
            compile_result.returncode
        ),
        "simulation_returncode": (
            run_result.returncode
        ),
        "platform": (
            platform_name
        ),
        "compile_command": (
            compile_command
        ),
        "run_command": (
            run_command
        ),
    }


if __name__ == "__main__":

    result = (
        run_iverilog_simulation(
            "outputs/broken_alu.sv",
            "tests/tb_broken_alu.sv",
            "outputs/alu_sim_auto",
        )
    )

    print(
        "=== SiliconPilot Icarus Tool ==="
    )

    print(
        result
    )