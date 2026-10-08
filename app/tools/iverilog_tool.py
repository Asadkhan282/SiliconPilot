import subprocess
from pathlib import Path


def to_wsl_path(path: str) -> str:
    path_obj = Path(path).resolve()
    drive = path_obj.drive.replace(":", "").lower()
    remainder = str(path_obj).replace(path_obj.drive, "")
    remainder = remainder.replace("\\", "/")

    return f"/mnt/{drive}{remainder}"


def run_iverilog_simulation(
    rtl_file: str,
    testbench_file: str,
    output_file: str = "outputs/simulation.out",
) -> dict:

    rtl_wsl = to_wsl_path(rtl_file)
    tb_wsl = to_wsl_path(testbench_file)
    output_wsl = to_wsl_path(output_file)

    compile_command = [
        "wsl",
        "iverilog",
        "-g2012",
        "-o",
        output_wsl,
        rtl_wsl,
        tb_wsl,
    ]

    compile_result = subprocess.run(
        compile_command,
        capture_output=True,
        text=True,
    )

    if compile_result.returncode != 0:
        return {
            "status": "compile_fail",
            "passed": False,
            "compile_output": (
                compile_result.stdout
                + compile_result.stderr
            ),
            "simulation_output": "",
        }

    run_command = [
        "wsl",
        "vvp",
        output_wsl,
    ]

    run_result = subprocess.run(
        run_command,
        capture_output=True,
        text=True,
    )

    simulation_output = (
        run_result.stdout
        + run_result.stderr
    )

    passed = (
        run_result.returncode == 0
        and "TEST_PASS" in simulation_output
        and "TEST_FAIL" not in simulation_output
    )

    return {
        "status": (
            "pass"
            if passed
            else "simulation_fail"
        ),
        "passed": passed,
        "compile_output": (
            compile_result.stdout
            + compile_result.stderr
        ),
        "simulation_output": simulation_output,
    }


if __name__ == "__main__":
    result = run_iverilog_simulation(
        "outputs/broken_alu.sv",
        "tests/tb_broken_alu.sv",
        "outputs/alu_sim_auto",
    )

    print(result)