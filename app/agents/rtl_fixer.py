from pathlib import Path


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

    fix_rtl(input_rtl, output_rtl)

    print("=== SiliconPilot RTL Fixer ===")
    print(f"Input : {input_rtl}")
    print(f"Output: {output_rtl}")
    print("\nFix applied successfully.")