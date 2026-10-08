import sys
from pathlib import Path

from app.agents.strategy_executor import execute_strategies
from app.tools.diagnostic_classifier import classify_diagnostics
from app.tools.rtl_diagnostics import analyze_rtl


def main():
    if len(sys.argv) != 2:
        print(
            "Usage: python -m app.workflows.full_repair "
            "<rtl_file>"
        )
        return

    input_file = sys.argv[1]

    if not Path(input_file).exists():
        print(f"ERROR: File not found: {input_file}")
        return

    output_file = f"outputs/{Path(input_file).name}"

    print("=== SiliconPilot Autonomous RTL Repair ===\n")

    print(f"Input: {input_file}\n")

    print("STEP 1: Initial Verilator analysis")

    initial = analyze_rtl(input_file)

    initial_errors = initial["diagnostics"]["error_count"]
    initial_warnings = initial["diagnostics"]["warning_count"]

    print(f"Errors   : {initial_errors}")
    print(f"Warnings : {initial_warnings}")

    classified = classify_diagnostics(input_file)

    print("\nSTEP 2: Detected categories")

    for category, count in classified["category_summary"].items():
        print(f"- {category}: {count}")

    if (
        initial_errors == 0
        and initial_warnings == 0
    ):
        print("\nRESULT: PASS")
        print("RTL is already clean.")
        return

    print("\nSTEP 3: Apply repair strategies")

    execute_strategies(
        input_file,
        output_file
    )

    print("\nSTEP 4: Verify repaired RTL")

    final = analyze_rtl(output_file)

    final_errors = final["diagnostics"]["error_count"]
    final_warnings = final["diagnostics"]["warning_count"]

    print(f"Errors   : {final_errors}")
    print(f"Warnings : {final_warnings}")

    print("\n=== FINAL RESULT ===")

    if final_errors == 0 and final_warnings == 0:
        print("PASS")
        print("SiliconPilot successfully repaired the RTL.")
        print(f"Output: {output_file}")
    else:
        print("FAIL")
        print("Some Verilator diagnostics remain.")
        print(f"Output: {output_file}")


if __name__ == "__main__":
    main()