from pathlib import Path
import subprocess


def run_verilator(file_path: str) -> dict:
    command = [
        "wsl",
        "verilator",
        "--lint-only",
        "-Wall",
        file_path.replace("\\", "/"),
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


def fix_rtl(input_file: str, output_file: str) -> None:
    code = Path(input_file).read_text(encoding="utf-8")

    fixed_code = code.replace(
        "count = count + 1;",
        "count <= count + 1;"
    )

    if not fixed_code.endswith("\n"):
        fixed_code += "\n"

    Path(output_file).write_text(
        fixed_code,
        encoding="utf-8"
    )


if __name__ == "__main__":
    broken_file = "examples/broken_counter.sv"
    fixed_file = "outputs/broken_counter.sv"
    print("=== SiliconPilot Verilator Repair Workflow ===\n")

    print("STEP 1: Lint original RTL")
    before = run_verilator(broken_file)

    print(before["output"])

    print("\nSTEP 2: Applying SiliconPilot fix...")
    fix_rtl(broken_file, fixed_file)

    print("\nSTEP 3: Lint repaired RTL")
    after = run_verilator(fixed_file)

    print(after["output"])

    print("\n=== FINAL RESULT ===")

    if after["returncode"] == 0:
        print("PASS")
        print("SiliconPilot repaired the RTL and Verilator accepted it.")
    else:
        print("FAIL")
        print("Verilator still reports issues.")