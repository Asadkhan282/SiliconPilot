import json
import subprocess
import re


def run_verilator(file_path: str) -> str:
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

    return result.stdout + result.stderr


def parse_verilator_output(output: str) -> dict:
    warnings = []
    errors = []

    warning_pattern = re.compile(
        r"%Warning-([A-Z0-9_]+):\s+([^:]+):(\d+):(\d+):\s+(.*)"
    )

    error_pattern = re.compile(
        r"%Error-([A-Z0-9_]+):\s+([^:]+):(\d+):(\d+):\s+(.*)"
    )

    for line in output.splitlines():
        warning_match = warning_pattern.match(line)

        if warning_match:
            warnings.append({
                "severity": "warning",
                "code": warning_match.group(1),
                "file": warning_match.group(2),
                "line": int(warning_match.group(3)),
                "column": int(warning_match.group(4)),
                "message": warning_match.group(5),
            })

        error_match = error_pattern.match(line)

        if error_match:
            errors.append({
                "severity": "error",
                "code": error_match.group(1),
                "file": error_match.group(2),
                "line": int(error_match.group(3)),
                "column": int(error_match.group(4)),
                "message": error_match.group(5),
            })

    return {
        "warning_count": len(warnings),
        "error_count": len(errors),
        "warnings": warnings,
        "errors": errors,
    }


def analyze_rtl(file_path: str) -> dict:
    raw_output = run_verilator(file_path)
    parsed = parse_verilator_output(raw_output)

    return {
        "file": file_path,
        "status": "pass" if parsed["error_count"] == 0 else "fail",
        "diagnostics": parsed,
        "raw_output": raw_output,
    }


if __name__ == "__main__":
    result = analyze_rtl("examples/broken_counter.sv")

    print(
        json.dumps(
            result,
            indent=2
        )
    )