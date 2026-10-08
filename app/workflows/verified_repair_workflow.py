import sys
from pathlib import Path

from app.workflows.iterative_repair_loop import iterative_repair
from app.tools.iverilog_tool import run_iverilog_simulation


# =========================================================
# AUTOMATIC PATH DISCOVERY
# =========================================================

def discover_paths(
    input_rtl: str,
) -> dict:
    """
    Automatically derive:
    - repaired RTL output path
    - matching testbench path
    - simulation binary path

    Example:

        unseen_tests/unseen_latch_fsm_06.sv

    becomes:

        unseen_outputs/unseen_latch_fsm_06.sv
        tests/tb_unseen_latch_fsm_06.sv
        unseen_outputs/unseen_latch_fsm_06.out
    """

    input_path = Path(input_rtl)

    stem = input_path.stem

    output_path = (
        Path("unseen_outputs")
        / f"{stem}.sv"
    )

    testbench_path = (
        Path("tests")
        / f"tb_{stem}.sv"
    )

    simulation_output_path = (
        Path("unseen_outputs")
        / f"{stem}.out"
    )

    return {
        "input_rtl": input_path,
        "output_rtl": output_path,
        "testbench": testbench_path,
        "simulation_output": simulation_output_path,
    }


# =========================================================
# VERIFIED REPAIR WORKFLOW
# =========================================================

def verified_repair_workflow(
    input_rtl: str,
    output_rtl: str | None = None,
    testbench: str | None = None,
    simulation_output: str | None = None,
    max_iterations: int = 5,
) -> dict:
    """
    SiliconPilot end-to-end verified repair workflow.

    Flow:

        RTL
        -> automatic path discovery
        -> iterative repair
        -> lint verification
        -> functional simulation
        -> final verified status

    Final status possibilities:

        VERIFIED_PASS
            0 lint errors
            0 lint warnings
            simulation PASS

        VERIFIED_WITH_REVIEW
            0 lint errors
            one or more review warnings
            simulation PASS

        FUNCTIONAL_FAIL
            RTL is simulation-eligible
            simulation runs but fails

        SIMULATION_COMPILE_FAIL
            RTL lint stage allows simulation
            testbench/elaboration compilation fails

        LINT_FAIL
            one or more lint errors remain

        TESTBENCH_NOT_FOUND
            matching testbench does not exist

        INPUT_NOT_FOUND
            input RTL does not exist
    """

    print(
        "=== SiliconPilot Verified Repair Workflow ==="
    )

    # -----------------------------------------------------
    # Automatic path discovery
    # -----------------------------------------------------

    discovered = discover_paths(
        input_rtl
    )

    input_path = discovered[
        "input_rtl"
    ]

    if output_rtl is None:
        output_path = discovered[
            "output_rtl"
        ]
    else:
        output_path = Path(
            output_rtl
        )

    if testbench is None:
        testbench_path = discovered[
            "testbench"
        ]
    else:
        testbench_path = Path(
            testbench
        )

    if simulation_output is None:
        simulation_output_path = discovered[
            "simulation_output"
        ]
    else:
        simulation_output_path = Path(
            simulation_output
        )

    # -----------------------------------------------------
    # Show discovered configuration
    # -----------------------------------------------------

    print(
        "\nAuto-discovered workflow:"
    )

    print(
        f"Input RTL: {input_path}"
    )

    print(
        f"Output RTL: {output_path}"
    )

    print(
        f"Testbench: {testbench_path}"
    )

    print(
        f"Simulation binary: "
        f"{simulation_output_path}"
    )

    # -----------------------------------------------------
    # Basic file checks
    # -----------------------------------------------------

    if not input_path.exists():

        result = {
            "status": "INPUT_NOT_FOUND",
            "success": False,
            "message": (
                f"Input RTL not found: "
                f"{input_path}"
            ),
        }

        print(
            "\n"
            + result["message"]
        )

        return result

    if not testbench_path.exists():

        result = {
            "status": "TESTBENCH_NOT_FOUND",
            "success": False,
            "message": (
                f"Testbench not found: "
                f"{testbench_path}"
            ),
            "expected_testbench": str(
                testbench_path
            ),
        }

        print(
            "\n"
            + result["message"]
        )

        return result

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    simulation_output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # =====================================================
    # STEP 1
    # ITERATIVE REPAIR + LINT
    # =====================================================

    print(
        "\n[1/2] Running iterative RTL repair..."
    )

    repair_result = iterative_repair(
        str(input_path),
        str(output_path),
        max_iterations,
    )

    lint_success = bool(
        repair_result.get(
            "success",
            False,
        )
    )

    lint_status = repair_result.get(
        "status",
        "UNKNOWN",
    )

    final_errors = repair_result.get(
        "final_errors",
        None,
    )

    final_warnings = repair_result.get(
        "final_warnings",
        None,
    )

    review_required = repair_result.get(
        "review_required",
        [],
    )

    # -----------------------------------------------------
    # Decide whether simulation is allowed.
    #
    # PASS:
    #     0 errors, normally 0 warnings
    #
    # REVIEW_REQUIRED with 0 errors:
    #     simulation is still allowed.
    #
    # Remaining errors:
    #     simulation must NOT run.
    # -----------------------------------------------------

    simulation_allowed = (
        final_errors == 0
    )

    if not simulation_allowed:

        print(
            "\nLint stage still contains errors."
        )

        print(
            "\n=== SiliconPilot Verification Summary ==="
        )

        print(
            f"Input RTL: {input_path}"
        )

        print(
            f"Output RTL: {output_path}"
        )

        print(
            f"Testbench: {testbench_path}"
        )

        print(
            f"Lint status: {lint_status}"
        )

        print(
            f"Lint errors: {final_errors}"
        )

        print(
            f"Lint warnings: {final_warnings}"
        )

        print(
            "Simulation: NOT RUN"
        )

        print(
            "Overall status: LINT_FAIL"
        )

        return {
            "status": "LINT_FAIL",
            "success": False,
            "lint_passed": False,
            "simulation_passed": False,
            "simulation_ran": False,
            "final_errors": final_errors,
            "final_warnings": final_warnings,
            "review_required": review_required,
            "input_rtl": str(
                input_path
            ),
            "output_rtl": str(
                output_path
            ),
            "testbench": str(
                testbench_path
            ),
            "simulation_output": str(
                simulation_output_path
            ),
            "repair_result": repair_result,
            "simulation_result": None,
        }

    # -----------------------------------------------------
    # If there are warnings but no errors, explain that
    # simulation will continue.
    # -----------------------------------------------------

    if (
        lint_status == "REVIEW_REQUIRED"
        or (
            final_warnings is not None
            and final_warnings > 0
        )
    ):

        print(
            "\nLint contains review-required "
            "warnings but no errors."
        )

        print(
            "Continuing to functional simulation."
        )

        if review_required:

            print(
                "\nReview items:"
            )

            for item in review_required:

                code = item.get(
                    "code",
                    "UNKNOWN",
                )

                message = item.get(
                    "message",
                    "",
                )

                print(
                    f"- {code}: {message}"
                )

    # =====================================================
    # STEP 2
    # FUNCTIONAL SIMULATION
    # =====================================================

    print(
        "\n[2/2] Running functional simulation..."
    )

    simulation_result = (
        run_iverilog_simulation(
            str(output_path),
            str(testbench_path),
            str(simulation_output_path),
        )
    )

    simulation_status = (
        simulation_result.get(
            "status",
            "UNKNOWN",
        )
    )

    simulation_passed = bool(
        simulation_result.get(
            "passed",
            False,
        )
    )

    # =====================================================
    # FINAL STATUS CLASSIFICATION
    # =====================================================

    if simulation_passed:

        if (
            lint_status == "PASS"
            and final_warnings == 0
        ):

            final_status = (
                "VERIFIED_PASS"
            )

        else:

            final_status = (
                "VERIFIED_WITH_REVIEW"
            )

        overall_success = True

    else:

        if simulation_status == "compile_fail":

            final_status = (
                "SIMULATION_COMPILE_FAIL"
            )

        else:

            final_status = (
                "FUNCTIONAL_FAIL"
            )

        overall_success = False

    # -----------------------------------------------------
    # Lint verification semantics
    #
    # lint_passed means:
    # no lint ERRORS remain.
    #
    # A REVIEW_REQUIRED warning does not make lint_passed
    # false, because functional verification may still be
    # valid.
    # -----------------------------------------------------

    lint_passed = (
        final_errors == 0
    )

    # =====================================================
    # SUMMARY
    # =====================================================

    print(
        "\n=== SiliconPilot Verification Summary ==="
    )

    print(
        f"Input RTL: {input_path}"
    )

    print(
        f"Output RTL: {output_path}"
    )

    print(
        f"Testbench: {testbench_path}"
    )

    print(
        f"Simulation binary: "
        f"{simulation_output_path}"
    )

    print(
        f"Lint status: {lint_status}"
    )

    print(
        f"Lint errors: {final_errors}"
    )

    print(
        f"Lint warnings: {final_warnings}"
    )

    if simulation_status == "compile_fail":

        print(
            "Simulation: COMPILE FAIL"
        )

    else:

        print(
            "Simulation: "
            + (
                "PASS"
                if simulation_passed
                else "FAIL"
            )
        )

    if review_required:

        print(
            f"Review items: "
            f"{len(review_required)}"
        )

    print(
        f"Overall status: "
        f"{final_status}"
    )

    # =====================================================
    # RETURN RESULT
    # =====================================================

    return {
        "status": final_status,
        "success": overall_success,

        "lint_passed": lint_passed,
        "lint_clean": (
            final_errors == 0
            and final_warnings == 0
        ),

        "simulation_ran": True,
        "simulation_passed": (
            simulation_passed
        ),
        "simulation_status": (
            simulation_status
        ),

        "final_errors": final_errors,
        "final_warnings": final_warnings,

        "review_required": (
            review_required
        ),

        "input_rtl": str(
            input_path
        ),

        "output_rtl": str(
            output_path
        ),

        "testbench": str(
            testbench_path
        ),

        "simulation_output": str(
            simulation_output_path
        ),

        "repair_result": (
            repair_result
        ),

        "simulation_result": (
            simulation_result
        ),
    }


# =========================================================
# CLI USAGE
# =========================================================

def print_usage():

    print(
        "\nUsage:"
    )

    print(
        "python -m "
        "app.workflows.verified_repair_workflow "
        "<input_rtl>"
    )

    print(
        "\nExample:"
    )

    print(
        "python -m "
        "app.workflows.verified_repair_workflow "
        "unseen_tests\\unseen_latch_fsm_06.sv"
    )

    print(
        "\nAutomatic mapping:"
    )

    print(
        "Input:"
    )

    print(
        "  unseen_tests\\"
        "unseen_latch_fsm_06.sv"
    )

    print(
        "Output:"
    )

    print(
        "  unseen_outputs\\"
        "unseen_latch_fsm_06.sv"
    )

    print(
        "Testbench:"
    )

    print(
        "  tests\\"
        "tb_unseen_latch_fsm_06.sv"
    )

    print(
        "Simulation:"
    )

    print(
        "  unseen_outputs\\"
        "unseen_latch_fsm_06.out"
    )


# =========================================================
# MAIN
# =========================================================

def main():

    if len(sys.argv) < 2:

        print_usage()

        sys.exit(1)

    input_rtl = sys.argv[1]

    result = verified_repair_workflow(
        input_rtl=input_rtl,
    )

    print(
        "\nFinal result:"
    )

    print(result)

    if result.get(
        "success",
        False,
    ):
        sys.exit(0)

    sys.exit(1)


if __name__ == "__main__":
    main()