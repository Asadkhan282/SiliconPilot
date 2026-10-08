from pathlib import Path

from app.tools.rtl_diagnostics import analyze_rtl
from app.workflows.iterative_repair_loop import iterative_repair
from app.tools.iverilog_tool import run_iverilog_simulation
from app.tools.testbench_registry import get_testbench


BENCHMARK_CASES = [
    "broken_alu.sv",
    "broken_logic.sv",
    "broken_width.sv",
    "broken_latch.sv",
    "broken_seq2.sv",
    "broken_width2.sv",
    "mixed_seq_width.sv",
    "mixed_latch_width.sv",
    "mixed_seq_latch.sv",
    "multi_fault_datapath.sv",
    "broken_fsm.sv",
    "mixed_fsm_datapath.sv",
    "undriven_output.sv",
    "multi_output_width.sv",
    "nested_control_fault.sv",
    "final_multi_fault.sv",
]


def run_benchmark():
    results = []

    for filename in BENCHMARK_CASES:
        input_path = Path("examples") / filename
        output_path = Path("outputs") / filename

        print(f"\n=== {filename} ===")

        # Analyze original RTL
        initial = analyze_rtl(
            str(input_path)
        )

        initial_errors = (
            initial["diagnostics"]["error_count"]
        )

        initial_warnings = (
            initial["diagnostics"]["warning_count"]
        )

        # Run iterative repair loop
        repair_result = iterative_repair(
            str(input_path),
            str(output_path),
            max_iterations=5,
        )

        # Analyze repaired RTL
        final = analyze_rtl(
            str(output_path)
        )

        final_errors = (
            final["diagnostics"]["error_count"]
        )

        final_warnings = (
            final["diagnostics"]["warning_count"]
        )

        lint_pass = (
            final_errors == 0
            and final_warnings == 0
        )

        # Find functional testbench
        testbench = get_testbench(
            filename
        )

        simulation_pass = False
        simulation_status = "not_configured"

        if testbench is not None:
            simulation_output = (
                Path("outputs")
                / f"{Path(filename).stem}_benchmark_sim"
            )

            simulation = run_iverilog_simulation(
                str(output_path),
                testbench,
                str(simulation_output),
            )

            simulation_pass = simulation["passed"]
            simulation_status = simulation["status"]

        # Overall verification
        overall_pass = (
            lint_pass
            and simulation_pass
        )

        result = {
            "file": filename,
            "initial_errors": initial_errors,
            "initial_warnings": initial_warnings,
            "final_errors": final_errors,
            "final_warnings": final_warnings,
            "lint_pass": lint_pass,
            "simulation_status": simulation_status,
            "simulation_pass": simulation_pass,
            "overall_pass": overall_pass,
            "repair_success": repair_result["success"],
            "repair_history": repair_result["history"],
        }

        results.append(result)

        print(
            f"Initial: "
            f"{initial_errors} error(s), "
            f"{initial_warnings} warning(s)"
        )

        print(
            f"Final: "
            f"{final_errors} error(s), "
            f"{final_warnings} warning(s)"
        )

        print(
            f"Lint: "
            f"{'PASS' if lint_pass else 'FAIL'}"
        )

        print(
            f"Simulation: "
            f"{'PASS' if simulation_pass else 'FAIL'}"
        )

        print(
            f"Overall: "
            f"{'PASS' if overall_pass else 'FAIL'}"
        )

    return results


def print_summary(results):
    total = len(results)

    lint_passes = sum(
        1
        for item in results
        if item["lint_pass"]
    )

    simulation_passes = sum(
        1
        for item in results
        if item["simulation_pass"]
    )

    overall_passes = sum(
        1
        for item in results
        if item["overall_pass"]
    )

    lint_rate = (
        100 * lint_passes / total
        if total
        else 0
    )

    simulation_rate = (
        100 * simulation_passes / total
        if total
        else 0
    )

    overall_rate = (
        100 * overall_passes / total
        if total
        else 0
    )

    print("\n==============================")
    print("SILICONPILOT BENCHMARK SUMMARY")
    print("==============================")

    print(
        f"Designs tested: {total}"
    )

    print(
        f"Lint passes: "
        f"{lint_passes}/{total} "
        f"({lint_rate:.1f}%)"
    )

    print(
        f"Simulation passes: "
        f"{simulation_passes}/{total} "
        f"({simulation_rate:.1f}%)"
    )

    print(
        f"Fully verified repairs: "
        f"{overall_passes}/{total} "
        f"({overall_rate:.1f}%)"
    )


if __name__ == "__main__":
    benchmark_results = run_benchmark()

    print_summary(
        benchmark_results
    )