import json

from app.tools.rtl_diagnostics import analyze_rtl


CATEGORY_MAP = {
    "BLKSEQ": "SEQUENTIAL_ASSIGNMENT",
    "BLKANDNBLK": "SEQUENTIAL_ASSIGNMENT",
    "EOFNEWLINE": "STYLE",
    "DECLFILENAME": "FILENAME_MISMATCH",
    "WIDTH": "WIDTH_MISMATCH",
    "LATCH": "LATCH_RISK",
    "UNUSEDSIGNAL": "UNUSED_SIGNAL",
    "UNDRIVEN": "UNDRIVEN_SIGNAL",
}


def classify_code(code: str) -> str:
    if code in CATEGORY_MAP:
        return CATEGORY_MAP[code]

    if code.startswith("WIDTH"):
        return "WIDTH_MISMATCH"

    if "LATCH" in code:
        return "LATCH_RISK"

    if "UNUSED" in code:
        return "UNUSED_SIGNAL"

    return "OTHER"


def classify_diagnostics(file_path: str) -> dict:
    analysis = analyze_rtl(file_path)

    classified = []

    diagnostics = analysis["diagnostics"]

    for warning in diagnostics["warnings"]:
        classified.append({
            **warning,
            "category": classify_code(warning["code"]),
        })

    for error in diagnostics["errors"]:
        classified.append({
            **error,
            "category": classify_code(error["code"]),
        })

    summary = {}

    for item in classified:
        category = item["category"]
        summary[category] = summary.get(category, 0) + 1

    return {
        "file": file_path,
        "status": analysis["status"],
        "total_diagnostics": len(classified),
        "category_summary": summary,
        "diagnostics": classified,
    }


if __name__ == "__main__":
    result = classify_diagnostics(
        "examples/broken_logic.sv"
    )

    print(
        json.dumps(
            result,
            indent=2
        )
    )