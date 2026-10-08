import json

from app.tools.diagnostic_classifier import classify_diagnostics


STRATEGY_MAP = {
    "SEQUENTIAL_ASSIGNMENT": "repair_sequential_assignments",
    "WIDTH_MISMATCH": "repair_width_mismatch",
    "LATCH_RISK": "repair_combinational_latch",
    "UNUSED_SIGNAL": "review_unused_signal",
    "UNDRIVEN_SIGNAL": "repair_undriven_signal",
    "FILENAME_MISMATCH": "repair_filename_mismatch",
    "STYLE": "repair_style",
    "OTHER": "request_ai_analysis",
}


def route_repairs(file_path: str) -> dict:
    classified = classify_diagnostics(file_path)

    categories = classified["category_summary"]

    strategies = []

    for category, count in categories.items():
        strategy = STRATEGY_MAP.get(
            category,
            "request_ai_analysis"
        )

        strategies.append({
            "category": category,
            "diagnostic_count": count,
            "strategy": strategy,
        })

    # Priority: real RTL correctness issues before style issues.
    priority_order = {
        "SEQUENTIAL_ASSIGNMENT": 1,
        "LATCH_RISK": 2,
        "WIDTH_MISMATCH": 3,
        "UNDRIVEN_SIGNAL": 4,
        "UNUSED_SIGNAL": 5,
        "FILENAME_MISMATCH": 6,
        "STYLE": 7,
        "OTHER": 8,
    }

    strategies.sort(
        key=lambda item: priority_order.get(
            item["category"],
            99
        )
    )

    return {
        "file": file_path,
        "status": classified["status"],
        "repair_required": classified["status"] == "fail"
        or classified["total_diagnostics"] > 0,
        "strategies": strategies,
    }


if __name__ == "__main__":
    result = route_repairs(
        "examples/broken_logic.sv"
    )

    print(
        json.dumps(
            result,
            indent=2
        )
    )