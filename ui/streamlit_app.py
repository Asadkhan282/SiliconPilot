import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
from pathlib import Path
import difflib

import streamlit as st

from app.tools.rtl_diagnostics import analyze_rtl
from app.tools.diagnostic_classifier import classify_diagnostics
from app.agents.repair_strategy import route_repairs
from app.agents.strategy_executor import execute_strategies
from app.tools.iverilog_tool import run_iverilog_simulation
from app.tools.testbench_registry import get_testbench
from app.workflows.benchmark_runner import run_benchmark


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="SiliconPilot",
    page_icon="🧠",
    layout="wide",
)


# ---------------------------------------------------------
# CUSTOM STYLING
# ---------------------------------------------------------

st.markdown(
    """
    <style>
    .main-title {
        font-size: 48px;
        font-weight: 800;
        margin-bottom: 0px;
    }

    .subtitle {
        font-size: 21px;
        opacity: 0.8;
        margin-bottom: 25px;
    }

    .pipeline-box {
        padding: 18px;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.15);
        margin-bottom: 20px;
    }

    .section-divider {
        margin-top: 25px;
        margin-bottom: 25px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------

st.markdown(
    '<div class="main-title">SiliconPilot</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    'Autonomous RTL Analysis, Repair & Verification Agent'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="pipeline-box">
    RTL Upload → Verilator Analysis → Diagnostic Classification →
    Repair Strategy → RTL Repair → Verilator Verification →
    Functional Simulation
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# BENCHMARK DASHBOARD
# ---------------------------------------------------------

st.markdown("## Benchmark Dashboard")

st.caption(
    "Run the complete SiliconPilot benchmark suite across "
    "the currently registered RTL repair cases."
)

if st.button(
    "Run Full Benchmark",
    use_container_width=True,
):
    with st.spinner(
        "Running SiliconPilot benchmark suite..."
    ):
        benchmark_results = run_benchmark()

    total = len(benchmark_results)

    lint_passes = sum(
        1
        for item in benchmark_results
        if item["lint_pass"]
    )

    simulation_passes = sum(
        1
        for item in benchmark_results
        if item["simulation_pass"]
    )

    overall_passes = sum(
        1
        for item in benchmark_results
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

    b1, b2, b3, b4 = st.columns(4)

    b1.metric(
        "Designs Tested",
        total,
    )

    b2.metric(
        "Lint Pass Rate",
        f"{lint_rate:.1f}%",
    )

    b3.metric(
        "Simulation Pass Rate",
        f"{simulation_rate:.1f}%",
    )

    b4.metric(
        "Overall Verified",
        f"{overall_rate:.1f}%",
    )

    st.markdown("### Benchmark Results")

    for item in benchmark_results:
        status = (
            "PASS"
            if item["overall_pass"]
            else "FAIL"
        )

        st.write(
            f"**{item['file']}** "
            f"— Lint: "
            f"{'PASS' if item['lint_pass'] else 'FAIL'} "
            f"| Simulation: "
            f"{'PASS' if item['simulation_pass'] else 'FAIL'} "
            f"| Overall: **{status}**"
        )

    if total > 0 and overall_passes == total:
        st.success(
            f"All {total} benchmark designs passed "
            "lint and functional verification."
        )
    elif total > 0:
        st.warning(
            f"{overall_passes}/{total} benchmark designs "
            "passed full verification."
        )
    else:
        st.info(
            "No benchmark cases were executed."
        )


st.divider()


# ---------------------------------------------------------
# SINGLE RTL ANALYSIS
# ---------------------------------------------------------

st.markdown("## Analyze RTL")

uploaded_file = st.file_uploader(
    "Upload SystemVerilog RTL",
    type=["sv", "v"],
)


if uploaded_file is not None:
    source_code = uploaded_file.getvalue().decode(
        "utf-8"
    )

    st.markdown("### Input RTL")

    st.code(
        source_code,
        language="systemverilog",
    )

    if st.button(
        "Run SiliconPilot",
        type="primary",
        use_container_width=True,
    ):
        safe_name = Path(
            uploaded_file.name
        ).name

        input_path = (
            Path("examples") / safe_name
        )

        output_path = (
            Path("outputs") / safe_name
        )

        input_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        input_path.write_text(
            source_code,
            encoding="utf-8",
        )

        # -------------------------------------------------
        # INITIAL ANALYSIS
        # -------------------------------------------------

        with st.spinner(
            "Running Verilator and analyzing RTL..."
        ):
            initial = analyze_rtl(
                str(input_path)
            )

            classified = classify_diagnostics(
                str(input_path)
            )

            routing = route_repairs(
                str(input_path)
            )

        st.markdown("## Initial Analysis")

        c1, c2, c3 = st.columns(3)

        initial_errors = (
            initial["diagnostics"]["error_count"]
        )

        initial_warnings = (
            initial["diagnostics"]["warning_count"]
        )

        c1.metric(
            "Initial Errors",
            initial_errors,
        )

        c2.metric(
            "Initial Warnings",
            initial_warnings,
        )

        initial_clean = (
            initial_errors == 0
            and initial_warnings == 0
        )

        c3.metric(
            "Initial Status",
            (
                "PASS"
                if initial_clean
                else "ISSUES FOUND"
            ),
        )


        # -------------------------------------------------
        # DIAGNOSTIC CATEGORIES
        # -------------------------------------------------

        st.markdown(
            "## Detected Problem Categories"
        )

        if classified["category_summary"]:
            category_columns = st.columns(
                max(
                    1,
                    len(
                        classified[
                            "category_summary"
                        ]
                    ),
                )
            )

            for index, (
                category,
                count,
            ) in enumerate(
                classified[
                    "category_summary"
                ].items()
            ):
                category_columns[
                    index
                ].metric(
                    category,
                    count,
                )

        else:
            st.success(
                "No diagnostic categories detected."
            )


        # -------------------------------------------------
        # REPAIR PLAN
        # -------------------------------------------------

        st.markdown("## Repair Plan")

        if routing["strategies"]:
            for item in routing["strategies"]:
                st.write(
                    f"**{item['category']}** "
                    f"→ `{item['strategy']}` "
                    f"({item['diagnostic_count']} "
                    f"diagnostic(s))"
                )

        else:
            st.success(
                "No repair strategy required."
            )


        # -------------------------------------------------
        # RAW VERILATOR DIAGNOSTICS
        # -------------------------------------------------

        with st.expander(
            "View Verilator diagnostics",
            expanded=False,
        ):
            if classified["diagnostics"]:
                for item in (
                    classified["diagnostics"]
                ):
                    severity = (
                        item["severity"].upper()
                    )

                    st.markdown(
                        f"### {severity} — "
                        f"{item['code']}"
                    )

                    st.write(
                        item["message"]
                    )

                    st.caption(
                        f"Line {item['line']} | "
                        f"Column {item['column']} | "
                        f"Category: "
                        f"{item['category']}"
                    )

                    st.divider()

            else:
                st.success(
                    "No Verilator diagnostics."
                )


        # -------------------------------------------------
        # REPAIR FLOW
        # -------------------------------------------------

        if not initial_clean:
            st.markdown(
                "## Autonomous Repair"
            )

            with st.spinner(
                "Applying repair strategies..."
            ):
                execute_strategies(
                    str(input_path),
                    str(output_path),
                )

            repaired_code = (
                output_path.read_text(
                    encoding="utf-8",
                )
            )

            # ---------------------------------------------
            # FINAL LINT
            # ---------------------------------------------

            final = analyze_rtl(
                str(output_path)
            )


            # ---------------------------------------------
            # FUNCTIONAL SIMULATION
            # ---------------------------------------------

            simulation_result = None

            testbench_path = get_testbench(
                safe_name
            )

            if testbench_path is not None:
                simulation_output_path = (
                    Path("outputs")
                    / (
                        f"{Path(safe_name).stem}"
                        "_sim_ui"
                    )
                )

                simulation_result = (
                    run_iverilog_simulation(
                        str(output_path),
                        testbench_path,
                        str(
                            simulation_output_path
                        ),
                    )
                )


            # ---------------------------------------------
            # BEFORE / AFTER
            # ---------------------------------------------

            st.markdown(
                "## Before vs After"
            )

            left, right = st.columns(2)

            with left:
                st.markdown(
                    "### Original RTL"
                )

                st.code(
                    source_code,
                    language="systemverilog",
                )

            with right:
                st.markdown(
                    "### Repaired RTL"
                )

                st.code(
                    repaired_code,
                    language="systemverilog",
                )


            # ---------------------------------------------
            # RTL DIFF
            # ---------------------------------------------

            st.markdown(
                "## RTL Changes"
            )

            original_lines = (
                source_code.splitlines()
            )

            repaired_lines = (
                repaired_code.splitlines()
            )

            diff = difflib.ndiff(
                original_lines,
                repaired_lines,
            )

            meaningful_changes = []

            for line in diff:
                if line.startswith("- "):
                    code = (
                        line[2:].rstrip()
                    )

                    if code.strip():
                        meaningful_changes.append(
                            f"- {code}"
                        )

                elif line.startswith("+ "):
                    code = (
                        line[2:].rstrip()
                    )

                    if code.strip():
                        meaningful_changes.append(
                            f"+ {code}"
                        )

            diff_text = "\n".join(
                meaningful_changes
            )

            if diff_text:
                st.code(
                    diff_text,
                    language="diff",
                )

            else:
                st.info(
                    "No meaningful RTL "
                    "changes detected."
                )


            # ---------------------------------------------
            # LINT VERIFICATION
            # ---------------------------------------------

            st.markdown(
                "## Verification"
            )

            v1, v2, v3 = st.columns(3)

            final_errors = (
                final[
                    "diagnostics"
                ]["error_count"]
            )

            final_warnings = (
                final[
                    "diagnostics"
                ]["warning_count"]
            )

            v1.metric(
                "Final Errors",
                final_errors,
                delta=(
                    final_errors
                    - initial_errors
                ),
            )

            v2.metric(
                "Final Warnings",
                final_warnings,
                delta=(
                    final_warnings
                    - initial_warnings
                ),
            )

            final_clean = (
                final_errors == 0
                and final_warnings == 0
            )

            v3.metric(
                "Lint Result",
                (
                    "PASS"
                    if final_clean
                    else "FAIL"
                ),
            )

            if final_clean:
                st.success(
                    "Verilator lint "
                    "verification: PASS"
                )

            else:
                st.error(
                    "Verilator lint "
                    "verification: FAIL"
                )

                with st.expander(
                    "Remaining diagnostics"
                ):
                    st.text(
                        final["raw_output"]
                    )


            # ---------------------------------------------
            # FUNCTIONAL VERIFICATION
            # ---------------------------------------------

            st.markdown(
                "## Functional Simulation"
            )

            if simulation_result is not None:
                s1, s2 = st.columns(2)

                simulation_passed = (
                    simulation_result[
                        "passed"
                    ]
                )

                s1.metric(
                    "Simulation Result",
                    (
                        "PASS"
                        if simulation_passed
                        else "FAIL"
                    ),
                )

                s2.metric(
                    "Simulator",
                    "Icarus Verilog",
                )

                if simulation_passed:
                    st.success(
                        "Functional "
                        "Simulation: PASS"
                    )

                else:
                    st.error(
                        "Functional "
                        "Simulation: FAIL"
                    )

                with st.expander(
                    "View simulation output"
                ):
                    compile_output = (
                        simulation_result[
                            "compile_output"
                        ]
                    )

                    if compile_output:
                        st.markdown(
                            "### Compile Output"
                        )

                        st.text(
                            compile_output
                        )

                    st.markdown(
                        "### Simulation Output"
                    )

                    st.text(
                        simulation_result[
                            "simulation_output"
                        ]
                    )

            else:
                st.info(
                    "No functional testbench "
                    "configured for this RTL file yet."
                )


            # ---------------------------------------------
            # FINAL STATUS
            # ---------------------------------------------

            st.markdown(
                "## Final Status"
            )

            simulation_verified = (
                simulation_result is not None
                and simulation_result["passed"]
            )

            if simulation_result is None:
                overall_pass = final_clean
            else:
                overall_pass = (
                    final_clean
                    and simulation_verified
                )

            if overall_pass:
                st.success(
                    "SiliconPilot successfully "
                    "repaired and verified the RTL."
                )

            else:
                st.error(
                    "SiliconPilot verification "
                    "did not fully pass."
                )


            # ---------------------------------------------
            # DOWNLOAD
            # ---------------------------------------------

            st.download_button(
                label="Download Repaired RTL",
                data=repaired_code,
                file_name=safe_name,
                mime="text/plain",
                use_container_width=True,
            )

        else:
            st.success(
                "RTL is already clean. "
                "No repair required."
            )