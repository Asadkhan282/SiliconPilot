import re
import json


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
                "code": warning_match.group(1),
                "file": warning_match.group(2),
                "line": int(warning_match.group(3)),
                "column": int(warning_match.group(4)),
                "message": warning_match.group(5),
            })

        error_match = error_pattern.match(line)

        if error_match:
            errors.append({
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


if __name__ == "__main__":
    sample = """
%Warning-BLKSEQ: examples/broken_counter.sv:11:15: Blocking assignment '=' in sequential logic process
%Error-BLKANDNBLK: examples/broken_counter.sv:4:24: Unsupported: Blocked and non-blocking assignments to same variable: 'count'
"""

    result = parse_verilator_output(sample)

    print(
        json.dumps(
            result,
            indent=2
        )
    )