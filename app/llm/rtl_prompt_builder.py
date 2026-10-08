import json
from pathlib import Path

from app.tools.rtl_diagnostics import analyze_rtl


def build_rtl_repair_prompt(file_path: str) -> str:
    rtl_code = Path(file_path).read_text(encoding="utf-8")
    analysis = analyze_rtl(file_path)

    diagnostics = analysis["diagnostics"]

    prompt = f"""
You are SiliconPilot, an expert RTL and SystemVerilog engineering agent.

Your task is to analyze the RTL source and the Verilator diagnostics,
identify the root cause of each issue, and produce a corrected RTL version.

IMPORTANT RULES:
1. Preserve the intended functionality.
2. Fix all Verilator errors.
3. Fix important Verilator warnings where appropriate.
4. Do not rename the module unless necessary.
5. Use synthesizable SystemVerilog.
6. Prefer nonblocking assignments inside sequential always_ff blocks.
7. Return the corrected RTL code.
8. Explain the changes briefly.

FILE:
{file_path}

SYSTEMVERILOG SOURCE:
{rtl_code}

VERILATOR DIAGNOSTICS:
{json.dumps(diagnostics, indent=2)}

Return your answer in this format:

ROOT_CAUSE:
<short explanation>

FIXES:
<bullet-style explanation>

CORRECTED_RTL:
<full corrected SystemVerilog>
"""

    return prompt.strip()


if __name__ == "__main__":
    prompt = build_rtl_repair_prompt(
        "examples/broken_counter.sv"
    )

    print("=== SiliconPilot Nemotron Prompt ===\n")
    print(prompt)