from pathlib import Path

from app.tools.rtl_diagnostics import analyze_rtl
from app.agents.strategy_executor import execute_strategies


def iterative_repair(
    input_file: str,
    output_file: str,
    max_iterations: int = 5,
) -> dict:

    print("=== SiliconPilot Iterative Repair Loop ===")

    input_path = Path(input_file)
    output_path = Path(output_file)

    current_input = str(input_path)

    history = []

    previous_signature = None
    stopped_for_no_progress = False

    for iteration in range(
        1,
        max_iterations + 1,
    ):

        print(
            f"\n--- Iteration {iteration} ---"
        )

        analysis = analyze_rtl(
            current_input
        )

        diagnostics = analysis[
            "diagnostics"
        ]

        errors = diagnostics[
            "error_count"
        ]

        warnings = diagnostics[
            "warning_count"
        ]

        warning_list = diagnostics.get(
            "warnings",
            [],
        )

        error_list = diagnostics.get(
            "errors",
            [],
        )

        print(
            f"Errors: {errors}"
        )

        print(
            f"Warnings: {warnings}"
        )

        # ---------------------------------------------
        # Build diagnostic signature.
        #
        # We intentionally ignore line numbers here,
        # because repairs can move source lines while
        # leaving the exact same unresolved issue.
        # ---------------------------------------------

        signature_items = []

        for diagnostic in (
            error_list + warning_list
        ):
            signature_items.append(
                (
                    diagnostic.get(
                        "severity",
                        "",
                    ),
                    diagnostic.get(
                        "code",
                        "",
                    ),
                    diagnostic.get(
                        "message",
                        "",
                    ),
                )
            )

        current_signature = tuple(
            sorted(signature_items)
        )

        history.append(
            {
                "iteration": iteration,
                "file": current_input,
                "errors": errors,
                "warnings": warnings,
                "diagnostics": [
                    {
                        "severity": item.get(
                            "severity"
                        ),
                        "code": item.get(
                            "code"
                        ),
                        "message": item.get(
                            "message"
                        ),
                    }
                    for item in (
                        error_list
                        + warning_list
                    )
                ],
            }
        )

        # ---------------------------------------------
        # Clean RTL: stop immediately.
        # ---------------------------------------------

        if (
            errors == 0
            and warnings == 0
        ):
            print(
                "RTL is clean."
            )
            break

        # ---------------------------------------------
        # No-progress detection.
        #
        # If the exact same diagnostics are present
        # as the previous iteration, further repair
        # attempts are unlikely to help.
        # ---------------------------------------------

        if (
            previous_signature
            is not None
            and current_signature
            == previous_signature
        ):
            print(
                "No progress detected."
            )

            print(
                "Remaining diagnostics require "
                "review or a new repair strategy."
            )

            stopped_for_no_progress = True
            break

        previous_signature = (
            current_signature
        )

        # ---------------------------------------------
        # First iteration repairs the original input.
        # Later iterations repair the generated output.
        # ---------------------------------------------

        repair_input = current_input
        repair_output = str(
            output_path
        )

        execute_strategies(
            repair_input,
            repair_output,
        )

        current_input = str(
            output_path
        )

    # =============================================
    # Final analysis
    # =============================================

    if output_path.exists():
        final_target = str(
            output_path
        )

    else:
        final_target = str(
            input_path
        )

    final_analysis = analyze_rtl(
        final_target
    )

    final_diagnostics = final_analysis[
        "diagnostics"
    ]

    final_errors = final_diagnostics[
        "error_count"
    ]

    final_warnings = final_diagnostics[
        "warning_count"
    ]

    final_warning_list = (
        final_diagnostics.get(
            "warnings",
            [],
        )
    )

    # =============================================
    # Classify remaining warnings
    # =============================================

    review_required = []

    for diagnostic in final_warning_list:

        code = diagnostic.get(
            "code",
            "",
        )

        message = diagnostic.get(
            "message",
            "",
        )

        # -----------------------------------------
        # UNUSED input/output ports should not be
        # deleted automatically because doing so
        # changes the module interface.
        # -----------------------------------------

        if code == "UNUSEDSIGNAL":
            review_required.append(
                {
                    "code": code,
                    "message": message,
                    "reason": (
                        "Unused interface or signal "
                        "requires design-intent review."
                    ),
                }
            )

    success = (
        final_errors == 0
        and final_warnings == 0
    )

    needs_review = (
        final_errors == 0
        and final_warnings > 0
        and len(review_required) > 0
    )

    if success:
        status = "PASS"

    elif needs_review:
        status = "REVIEW_REQUIRED"

    else:
        status = "FAIL"

    # =============================================
    # Final report
    # =============================================

    print(
        "\n=== Final Iterative Repair Result ==="
    )

    print(
        f"Errors: {final_errors}"
    )

    print(
        f"Warnings: {final_warnings}"
    )

    print(
        f"Status: {status}"
    )

    if stopped_for_no_progress:
        print(
            "Stopped early because no "
            "diagnostic progress was detected."
        )

    if review_required:
        print(
            "\nReview-required diagnostics:"
        )

        for item in review_required:
            print(
                f"- {item['code']}: "
                f"{item['message']}"
            )

            print(
                f"  Reason: "
                f"{item['reason']}"
            )

    return {
        "success": success,
        "status": status,
        "output_file": str(
            output_path
        ),
        "final_errors": final_errors,
        "final_warnings": final_warnings,
        "review_required": (
            review_required
        ),
        "stopped_for_no_progress": (
            stopped_for_no_progress
        ),
        "history": history,
    }


if __name__ == "__main__":
    result = iterative_repair(
        "unseen_tests/unseen_controller_01.sv",
        "unseen_outputs/unseen_controller_01.sv",
        max_iterations=5,
    )

    print(result)