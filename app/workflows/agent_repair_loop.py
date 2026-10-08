from pathlib import Path

from app.llm.mock_nemotron import mock_nemotron_repair
from app.tools.rtl_diagnostics import analyze_rtl


def extract_corrected_rtl(response: str) -> str:
    marker = "CORRECTED_RTL:"

    if marker not in response:
        raise ValueError(
            "Model response does not contain CORRECTED_RTL section."
        )

    corrected_rtl = response.split(marker, 1)[1].strip()

    if not corrected_rtl:
        raise ValueError(
            "CORRECTED_RTL section is empty."
        )

    return corrected_rtl


def save_corrected_rtl(
    rtl_code: str,
    output_file: str
) -> None:
    if not rtl_code.endswith("\n"):
        rtl_code += "\n"

    Path(output_file).write_text(
        rtl_code,
        encoding="utf-8"
    )


def main():
    input_file = "examples/broken_counter.sv"
    output_file = "outputs/broken_counter.sv"

    print("=== SiliconPilot Agent Repair Loop ===\n")

    print("STEP 1: Analyze original RTL")
    original_analysis = analyze_rtl(input_file)

    print(
        f"Errors   : "
        f"{original_analysis['diagnostics']['error_count']}"
    )

    print(
        f"Warnings : "
        f"{original_analysis['diagnostics']['warning_count']}"
    )

    print("\nSTEP 2: Ask repair agent")

    model_response = mock_nemotron_repair(
        input_file
    )

    print("Repair response received.")

    print("\nSTEP 3: Extract corrected RTL")

    corrected_rtl = extract_corrected_rtl(
        model_response
    )

    save_corrected_rtl(
        corrected_rtl,
        output_file
    )

    print(
        f"Saved repaired RTL to: {output_file}"
    )

    print("\nSTEP 4: Verify repaired RTL with Verilator")

    repaired_analysis = analyze_rtl(
        output_file
    )

    print(
        f"Errors   : "
        f"{repaired_analysis['diagnostics']['error_count']}"
    )

    print(
        f"Warnings : "
        f"{repaired_analysis['diagnostics']['warning_count']}"
    )

    print("\n=== FINAL RESULT ===")

    if (
        repaired_analysis["diagnostics"]["error_count"] == 0
        and repaired_analysis["diagnostics"]["warning_count"] == 0
    ):
        print("PASS")
        print(
            "SiliconPilot repaired and verified "
            "the RTL automatically."
        )
    else:
        print("FAIL")
        print(
            "SiliconPilot repair still has "
            "Verilator diagnostics."
        )


if __name__ == "__main__":
    main()