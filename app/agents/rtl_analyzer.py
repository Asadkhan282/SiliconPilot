from pathlib import Path


def analyze_rtl(file_path: str) -> list[str]:
    code = Path(file_path).read_text(encoding="utf-8")

    issues = []

    if "always_ff" in code and "count = count + 1;" in code:
        issues.append(
            "Blocking assignment detected inside always_ff. "
            "Use nonblocking assignment <= for sequential logic."
        )

    if not issues:
        issues.append("No basic issues detected.")

    return issues


if __name__ == "__main__":
    rtl_file = "examples/broken_counter.sv"

    print("=== SiliconPilot RTL Analysis ===")
    print(f"File: {rtl_file}\n")

    results = analyze_rtl(rtl_file)

    for i, issue in enumerate(results, start=1):
        print(f"{i}. {issue}")