import json
import re

from app.tools.verilator_tool import run_verilator


def parse_verilator_output(
    output: str,
) -> dict:
    """
    Parse Verilator warnings and errors.
    """

    warnings = []
    errors = []

    warning_pattern = re.compile(
        r"%Warning-([A-Z0-9_]+):\s+"
        r"([^:]+):"
        r"(\d+):"
        r"(\d+):\s+"
        r"(.*)"
    )

    error_pattern = re.compile(
        r"%Error-([A-Z0-9_]+):\s+"
        r"([^:]+):"
        r"(\d+):"
        r"(\d+):\s+"
        r"(.*)"
    )

    for line in output.splitlines():

        warning_match = (
            warning_pattern.match(
                line
            )
        )

        if warning_match:

            warnings.append(
                {
                    "severity": "warning",
                    "code": warning_match.group(1),
                    "file": warning_match.group(2),
                    "line": int(
                        warning_match.group(3)
                    ),
                    "column": int(
                        warning_match.group(4)
                    ),
                    "message": warning_match.group(5),
                }
            )

        error_match = (
            error_pattern.match(
                line
            )
        )

        if error_match:

            errors.append(
                {
                    "severity": "error",
                    "code": error_match.group(1),
                    "file": error_match.group(2),
                    "line": int(
                        error_match.group(3)
                    ),
                    "column": int(
                        error_match.group(4)
                    ),
                    "message": error_match.group(5),
                }
            )

    return {
        "warning_count": len(
            warnings
        ),
        "error_count": len(
            errors
        ),
        "warnings": warnings,
        "errors": errors,
    }


def analyze_rtl(
    file_path: str,
) -> dict:
    """
    Run Verilator using the cross-platform wrapper,
    then parse diagnostics.

    Windows:
        Verilator through WSL

    Linux / Streamlit Cloud:
        Verilator directly
    """

    tool_result = run_verilator(
        file_path
    )

    raw_output = tool_result.get(
        "output",
        "",
    )

    parsed = parse_verilator_output(
        raw_output
    )

    tool_status = tool_result.get(
        "status",
        "unknown",
    )

    return {
        "file": file_path,

        "status": (
            "pass"
            if (
                parsed["error_count"] == 0
                and tool_status
                not in {
                    "tool_not_found",
                    "file_not_found",
                }
            )
            else "fail"
        ),

        "diagnostics": parsed,

        "raw_output": raw_output,

        "tool_status": (
            tool_status
        ),

        "tool_returncode": (
            tool_result.get(
                "returncode"
            )
        ),

        "platform": (
            tool_result.get(
                "platform"
            )
        ),
    }


if __name__ == "__main__":

    result = analyze_rtl(
        "examples/broken_counter.sv"
    )

    print(
        json.dumps(
            result,
            indent=2,
        )
    )