import subprocess
from pathlib import Path


def run_verilator(file_path: str) -> dict:
    file_path = Path(file_path)

    command = [
        "wsl",
        "verilator",
        "--lint-only",
        "-Wall",
        str(file_path).replace("\\", "/"),
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    output = result.stdout + result.stderr

    return {
        "returncode": result.returncode,
        "output": output,
    }


if __name__ == "__main__":
    result = run_verilator("examples/broken_counter.sv")

    print("=== SiliconPilot Verilator Tool ===\n")
    print(f"Return code: {result['returncode']}\n")
    print(result["output"])
