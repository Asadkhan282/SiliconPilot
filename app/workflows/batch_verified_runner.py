from pathlib import Path

from app.workflows.verified_repair_workflow import (
    verified_repair_workflow,
)


def batch_verified_runner(
    unseen_dir: str = "unseen_tests",
    tests_dir: str = "tests",
) -> dict:
    """
    Run SiliconPilot verified repair workflow across all
    unseen RTL designs that have matching testbenches.

    Matching convention:

        RTL:
            unseen_tests/design_name.sv

        Testbench:
            tests/tb_design_name.sv
    """

    print(
        "=== SiliconPilot Batch Verified Runner ==="
    )

    unseen_path = Path(unseen_dir)
    tests_path = Path(tests_dir)

    # =====================================================
    # BASIC CHECKS
    # =====================================================

    if not unseen_path.exists():

        print(
            f"ERROR: unseen directory not found: "
            f"{unseen_path}"
        )

        return {
            "status": "UNSEEN_DIR_NOT_FOUND",
            "success": False,
        }

    rtl_files = sorted(
        unseen_path.glob("*.sv")
    )

    if not rtl_files:

        print(
            "No unseen RTL files found."
        )

        return {
            "status": "NO_RTL_FILES",
            "success": False,
        }

    # =====================================================
    # RESULT STORAGE
    # =====================================================

    results = []

    # -----------------------------------------------------
    # Status counters
    # -----------------------------------------------------

    verified_pass_count = 0
    verified_with_review_count = 0
    review_required_count = 0
    functional_fail_count = 0
    simulation_compile_fail_count = 0
    lint_fail_count = 0
    no_testbench_count = 0
    other_count = 0

    # -----------------------------------------------------
    # Verification counters
    # -----------------------------------------------------

    lint_pass_count = 0
    lint_clean_count = 0

    simulation_run_count = 0
    simulation_pass_count = 0

    print(
        f"\nDiscovered RTL designs: "
        f"{len(rtl_files)}"
    )

    # =====================================================
    # RUN EACH DESIGN
    # =====================================================

    for index, rtl_file in enumerate(
        rtl_files,
        start=1,
    ):

        stem = rtl_file.stem

        testbench = (
            tests_path
            / f"tb_{stem}.sv"
        )

        print(
            "\n"
            + "=" * 60
        )

        print(
            f"[{index}/{len(rtl_files)}] "
            f"{rtl_file.name}"
        )

        print(
            "=" * 60
        )

        # -------------------------------------------------
        # No testbench
        # -------------------------------------------------

        if not testbench.exists():

            print(
                f"Testbench not found: "
                f"{testbench}"
            )

            result = {
                "design": stem,
                "input_rtl": str(
                    rtl_file
                ),
                "testbench": str(
                    testbench
                ),
                "status": "NO_TESTBENCH",
                "success": False,
                "lint_passed": None,
                "lint_clean": None,
                "simulation_passed": None,
                "simulation_ran": False,
                "final_errors": None,
                "final_warnings": None,
            }

            results.append(
                result
            )

            no_testbench_count += 1

            continue

        # -------------------------------------------------
        # Run verified repair workflow
        # -------------------------------------------------

        workflow_result = (
            verified_repair_workflow(
                input_rtl=str(
                    rtl_file
                ),
                testbench=str(
                    testbench
                ),
            )
        )

        status = workflow_result.get(
            "status",
            "UNKNOWN",
        )

        lint_passed = workflow_result.get(
            "lint_passed",
            False,
        )

        lint_clean = workflow_result.get(
            "lint_clean",
            False,
        )

        simulation_ran = workflow_result.get(
            "simulation_ran",
            False,
        )

        simulation_passed = (
            workflow_result.get(
                "simulation_passed",
                False,
            )
        )

        final_errors = workflow_result.get(
            "final_errors"
        )

        final_warnings = workflow_result.get(
            "final_warnings"
        )

        # -------------------------------------------------
        # Verification statistics
        # -------------------------------------------------

        if lint_passed:
            lint_pass_count += 1

        if lint_clean:
            lint_clean_count += 1

        if simulation_ran:
            simulation_run_count += 1

        if simulation_passed:
            simulation_pass_count += 1

        # -------------------------------------------------
        # Status accounting
        # -------------------------------------------------

        if status == "VERIFIED_PASS":

            verified_pass_count += 1

        elif status == "VERIFIED_WITH_REVIEW":

            verified_with_review_count += 1

        elif status == "REVIEW_REQUIRED":

            review_required_count += 1

        elif status == "FUNCTIONAL_FAIL":

            functional_fail_count += 1

        elif status == "SIMULATION_COMPILE_FAIL":

            simulation_compile_fail_count += 1

        elif (
            status == "FAIL"
            or status == "LINT_FAIL"
        ):

            lint_fail_count += 1

        else:

            other_count += 1

        # -------------------------------------------------
        # Store result
        # -------------------------------------------------

        results.append(
            {
                "design": stem,
                "input_rtl": str(
                    rtl_file
                ),
                "testbench": str(
                    testbench
                ),
                "status": status,
                "success": (
                    workflow_result.get(
                        "success",
                        False,
                    )
                ),
                "lint_passed": lint_passed,
                "lint_clean": lint_clean,
                "simulation_ran": simulation_ran,
                "simulation_passed": (
                    simulation_passed
                ),
                "final_errors": (
                    final_errors
                ),
                "final_warnings": (
                    final_warnings
                ),
            }
        )

    # =====================================================
    # STATISTICS
    # =====================================================

    total_designs = len(
        rtl_files
    )

    designs_with_tb = (
        total_designs
        - no_testbench_count
    )

    verified_total = (
        verified_pass_count
        + verified_with_review_count
    )

    # -----------------------------------------------------
    # Rates across ALL discovered designs
    # -----------------------------------------------------

    if total_designs > 0:

        verified_rate = (
            verified_total
            / total_designs
            * 100.0
        )

        lint_pass_rate = (
            lint_pass_count
            / total_designs
            * 100.0
        )

        lint_clean_rate = (
            lint_clean_count
            / total_designs
            * 100.0
        )

    else:

        verified_rate = 0.0
        lint_pass_rate = 0.0
        lint_clean_rate = 0.0

    # -----------------------------------------------------
    # Rates among designs WITH a testbench
    # -----------------------------------------------------

    if designs_with_tb > 0:

        verified_tested_rate = (
            verified_total
            / designs_with_tb
            * 100.0
        )

    else:

        verified_tested_rate = 0.0

    # -----------------------------------------------------
    # Simulation pass rate among simulations actually run
    # -----------------------------------------------------

    if simulation_run_count > 0:

        simulation_pass_rate = (
            simulation_pass_count
            / simulation_run_count
            * 100.0
        )

    else:

        simulation_pass_rate = 0.0

    # =====================================================
    # FINAL SUMMARY
    # =====================================================

    print(
        "\n"
        + "=" * 60
    )

    print(
        "SILICONPILOT UNSEEN VALIDATION SUMMARY"
    )

    print(
        "=" * 60
    )

    print(
        f"Designs discovered: "
        f"{total_designs}"
    )

    print(
        f"Designs with testbench: "
        f"{designs_with_tb}"
    )

    print()

    print(
        f"VERIFIED_PASS: "
        f"{verified_pass_count}"
    )

    print(
        f"VERIFIED_WITH_REVIEW: "
        f"{verified_with_review_count}"
    )

    print(
        f"REVIEW_REQUIRED: "
        f"{review_required_count}"
    )

    print(
        f"FUNCTIONAL_FAIL: "
        f"{functional_fail_count}"
    )

    print(
        f"SIMULATION_COMPILE_FAIL: "
        f"{simulation_compile_fail_count}"
    )

    print(
        f"LINT_FAIL: "
        f"{lint_fail_count}"
    )

    print(
        f"NO_TESTBENCH: "
        f"{no_testbench_count}"
    )

    print(
        f"OTHER: "
        f"{other_count}"
    )

    print()

    print(
        f"Verified rate "
        f"(all discovered): "
        f"{verified_rate:.1f}%"
    )

    print(
        f"Verified rate "
        f"(with testbench): "
        f"{verified_tested_rate:.1f}%"
    )

    print(
        f"Lint-pass rate: "
        f"{lint_pass_rate:.1f}%"
    )

    print(
        f"Lint-clean rate: "
        f"{lint_clean_rate:.1f}%"
    )

    print(
        f"Simulation pass rate: "
        f"{simulation_pass_rate:.1f}%"
    )

    # =====================================================
    # PER-DESIGN RESULTS
    # =====================================================

    print(
        "\nPer-design results:"
    )

    print(
        "-" * 90
    )

    for result in results:

        design = result[
            "design"
        ]

        status = result[
            "status"
        ]

        lint_value = result.get(
            "lint_passed"
        )

        lint_clean_value = result.get(
            "lint_clean"
        )

        sim_ran_value = result.get(
            "simulation_ran"
        )

        sim_value = result.get(
            "simulation_passed"
        )

        # ---------------------------------------------
        # Lint text
        # ---------------------------------------------

        if lint_value is True:

            lint_text = "PASS"

        elif lint_value is False:

            lint_text = "FAIL"

        else:

            lint_text = "N/A"

        # ---------------------------------------------
        # Lint-clean text
        # ---------------------------------------------

        if lint_clean_value is True:

            lint_clean_text = "YES"

        elif lint_clean_value is False:

            lint_clean_text = "NO"

        else:

            lint_clean_text = "N/A"

        # ---------------------------------------------
        # Simulation text
        # ---------------------------------------------

        if sim_ran_value is False:

            simulation_text = "N/A"

        elif sim_value is True:

            simulation_text = "PASS"

        elif sim_value is False:

            simulation_text = "FAIL"

        else:

            simulation_text = "N/A"

        print(
            f"{design:<28} "
            f"{status:<25} "
            f"Lint={lint_text:<4} "
            f"Clean={lint_clean_text:<3} "
            f"Sim={simulation_text}"
        )

    print(
        "-" * 90
    )

    # =====================================================
    # OVERALL BATCH STATUS
    # =====================================================

    overall_success = (
        functional_fail_count == 0
        and simulation_compile_fail_count == 0
        and lint_fail_count == 0
    )

    if overall_success:

        batch_status = (
            "BATCH_COMPLETE"
        )

    else:

        batch_status = (
            "BATCH_COMPLETE_WITH_FAILURES"
        )

    # =====================================================
    # RETURN RESULT
    # =====================================================

    return {
        "status": batch_status,
        "success": overall_success,

        "total_designs": (
            total_designs
        ),

        "designs_with_testbench": (
            designs_with_tb
        ),

        "verified_pass": (
            verified_pass_count
        ),

        "verified_with_review": (
            verified_with_review_count
        ),

        "verified_total": (
            verified_total
        ),

        "review_required": (
            review_required_count
        ),

        "functional_fail": (
            functional_fail_count
        ),

        "simulation_compile_fail": (
            simulation_compile_fail_count
        ),

        "lint_fail": (
            lint_fail_count
        ),

        "no_testbench": (
            no_testbench_count
        ),

        "other": (
            other_count
        ),

        "lint_pass_count": (
            lint_pass_count
        ),

        "lint_clean_count": (
            lint_clean_count
        ),

        "simulation_run_count": (
            simulation_run_count
        ),

        "simulation_pass_count": (
            simulation_pass_count
        ),

        "verified_rate": (
            verified_rate
        ),

        "verified_tested_rate": (
            verified_tested_rate
        ),

        "lint_pass_rate": (
            lint_pass_rate
        ),

        "lint_clean_rate": (
            lint_clean_rate
        ),

        "simulation_pass_rate": (
            simulation_pass_rate
        ),

        "results": (
            results
        ),
    }


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":

    batch_verified_runner()