from pathlib import Path
import re


def repair_always_ff_assignments(rtl_code: str) -> str:
    lines = rtl_code.splitlines()

    fixed_lines = []
    inside_always_ff = False
    block_depth = 0

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("always_ff"):
            inside_always_ff = True

        if inside_always_ff:
            block_depth += line.count("begin")
            block_depth -= line.count("end")

            # Replace blocking assignments inside always_ff
            # but do not touch comparisons such as ==, !=, <=, >=
            if "=" in line:
                line = re.sub(
                    r"(?<![<>=!])=(?!=)",
                    "<=",
                    line
                )

        fixed_lines.append(line)

        if inside_always_ff and block_depth <= 0 and stripped == "end":
            inside_always_ff = False
            block_depth = 0

    fixed_code = "\n".join(fixed_lines)

    if not fixed_code.endswith("\n"):
        fixed_code += "\n"

    return fixed_code


def mock_nemotron_repair(file_path: str) -> str:
    rtl_code = Path(file_path).read_text(
        encoding="utf-8"
    )

    corrected_code = repair_always_ff_assignments(
        rtl_code
    )

    response = f"""
ROOT_CAUSE:
Blocking assignments were detected inside sequential always_ff logic.
This can create inconsistent sequential semantics and Verilator
BLKSEQ / BLKANDNBLK diagnostics.

FIXES:
- Converted blocking assignments inside always_ff to nonblocking assignments.
- Preserved comparisons and other operators.
- Preserved intended RTL functionality.
- Added a newline at the end of the source.

CORRECTED_RTL:
{corrected_code}
"""

    return response.strip()


if __name__ == "__main__":
    result = mock_nemotron_repair(
        "examples/broken_alu.sv"
    )

    print("=== Mock NVIDIA Nemotron Response ===\n")
    print(result)