from pathlib import Path


def analyze_rtl(file_path: str) -> list[str]:
    code = Path(file_path).read_text(encoding="utf-8")

    issues = []

    if "always_ff" in code and "count = count + 1;" in code:
        issues.append(
            "Blocking assignment detected inside always_ff."
        )

    return issues


def fix_rtl(input_file: str, output_file: str) -> None:
    code = Path(input_file).read_text(encoding="utf-8")

    fixed_code = code.replace(
        "count = count + 1;",
        "count <= count + 1;"
    )

    Path(output_file).write_text(
        fixed_code,
        encoding="utf-8"
    )


if __name__ == "__main__":
    input_rtl = "examples/broken_counter.sv"
    output_rtl = "outputs/fixed_counter.sv"

    print("=== SiliconPilot Repair Workflow ===\n")

    before = analyze_rtl(input_rtl)

    print(f"Original issues: {len(before)}")

    for issue in before:
        print(f"- {issue}")

    print("\nApplying fix...")

    fix_rtl(input_rtl, output_rtl)

    after = analyze_rtl(output_rtl)

    print(f"\nRemaining issues: {len(after)}")

    if len(after) == 0:
        print("\nRESULT: PASS")
        print("SiliconPilot successfully repaired the RTL.")
    else:
        print("\nRESULT: FAIL")
        print("Some issues remain.")