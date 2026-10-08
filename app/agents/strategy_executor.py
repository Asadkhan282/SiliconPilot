import re
from pathlib import Path

from app.agents.repair_strategy import route_repairs
from app.tools.diagnostic_classifier import classify_diagnostics


# =========================================================
# SEQUENTIAL ASSIGNMENT REPAIR
# =========================================================

def repair_sequential_assignments(
    rtl_code: str,
) -> str:
    """
    Convert blocking assignments (=) to nonblocking
    assignments (<=) inside always_ff blocks.
    """

    lines = rtl_code.splitlines()
    fixed_lines = []

    inside_always_ff = False
    begin_depth = 0

    for line in lines:
        stripped = line.strip()

        if re.search(
            r"\balways_ff\b",
            stripped,
        ):
            inside_always_ff = True

        if inside_always_ff:
            begin_depth += len(
                re.findall(
                    r"\bbegin\b",
                    stripped,
                )
            )

            begin_depth -= len(
                re.findall(
                    r"\bend\b",
                    stripped,
                )
            )

            line = re.sub(
                r"(?<![<>=!])"
                r"\b([A-Za-z_][A-Za-z0-9_]*)"
                r"\s*="
                r"(?!=)",
                r"\1 <=",
                line,
            )

            if (
                begin_depth <= 0
                and re.search(
                    r"\bend\b",
                    stripped,
                )
            ):
                inside_always_ff = False
                begin_depth = 0

        fixed_lines.append(line)

    return "\n".join(fixed_lines)


# =========================================================
# WIDTH MISMATCH REPAIR
# =========================================================

def repair_width_mismatch(
    rtl_code: str,
    diagnostics: list,
) -> str:
    """
    Repair WIDTH_MISMATCH diagnostics.

    Supports:

        output logic [7:0] result;

    and:

        logic [7:0] result_reg;
    """

    lines = rtl_code.splitlines()

    for diagnostic in diagnostics:
        if (
            diagnostic["category"]
            != "WIDTH_MISMATCH"
        ):
            continue

        message = diagnostic["message"]

        width_match = re.search(
            r"generates\s+(\d+)\s+bits",
            message,
        )

        if not width_match:
            width_match = re.search(
                r"expects\s+(\d+)\s+bits",
                message,
            )

        if not width_match:
            print(
                "Width repair: could not determine "
                "required width"
            )
            continue

        required_width = int(
            width_match.group(1)
        )

        signal_name = None

        line_number = diagnostic.get(
            "line",
            0,
        )

        # -------------------------------------------------
        # First try the diagnostic source line.
        # -------------------------------------------------

        if (
            1
            <= line_number
            <= len(lines)
        ):
            source_line = lines[
                line_number - 1
            ]

            lhs_match = re.search(
                r"\b([A-Za-z_][A-Za-z0-9_]*)"
                r"\s*(?:=|<=)",
                source_line,
            )

            if lhs_match:
                signal_name = (
                    lhs_match.group(1)
                )

        # -------------------------------------------------
        # Fallback search.
        # -------------------------------------------------

        if signal_name is None:
            rtl_text = "\n".join(lines)

            for line in lines:
                lhs_match = re.search(
                    r"\b([A-Za-z_][A-Za-z0-9_]*)"
                    r"\s*(?:=|<=)",
                    line,
                )

                if not lhs_match:
                    continue

                candidate = (
                    lhs_match.group(1)
                )

                declaration_exists = re.search(
                    rf"\b(?:output\s+)?logic\s*"
                    rf"(?:\[[^\]]+\])?"
                    rf"\s+{re.escape(candidate)}\b",
                    rtl_text,
                )

                if declaration_exists:
                    signal_name = candidate
                    break

        if signal_name is None:
            print(
                "Width repair: could not identify "
                "target signal"
            )
            continue

        print(
            f"Width repair target: "
            f"{signal_name}, "
            f"required width: "
            f"{required_width}"
        )

        rtl_text = "\n".join(lines)

        declaration_pattern = (
            rf"((?:output\s+)?logic\s*)"
            rf"\[[^\]]+\]"
            rf"(\s+{re.escape(signal_name)}\b)"
        )

        new_range = (
            f"[{required_width - 1}:0]"
        )

        updated_code, count = re.subn(
            declaration_pattern,
            rf"\g<1>{new_range}\g<2>",
            rtl_text,
            count=1,
        )

        if count != 1:
            print(
                "Width repair FAILED: declaration for "
                f"{signal_name} was not found"
            )
            continue

        print(
            f"Width repair: "
            f"{signal_name} changed to "
            f"{required_width} bits"
        )

        # -------------------------------------------------
        # Update sized constants in nonblocking
        # assignments.
        # -------------------------------------------------

        nonblocking_pattern = (
            rf"(\b{re.escape(signal_name)}"
            rf"\b\s*<=\s*)"
            rf"(\d+)"
            rf"('(?:d|h|b|o)"
            rf"[0-9a-fA-F_xXzZ]+)"
        )

        updated_code = re.sub(
            nonblocking_pattern,
            rf"\g<1>{required_width}\g<3>",
            updated_code,
        )

        # -------------------------------------------------
        # Update sized constants in blocking assignments.
        # -------------------------------------------------

        blocking_pattern = (
            rf"(\b{re.escape(signal_name)}"
            rf"\b\s*=\s*)"
            rf"(\d+)"
            rf"('(?:d|h|b|o)"
            rf"[0-9a-fA-F_xXzZ]+)"
        )

        updated_code = re.sub(
            blocking_pattern,
            rf"\g<1>{required_width}\g<3>",
            updated_code,
        )

        lines = updated_code.splitlines()

    return "\n".join(lines)


# =========================================================
# LATCH REPAIR
# =========================================================

def repair_latch_risk(
    rtl_code: str,
    diagnostics: list,
) -> str:
    """
    Repair latch risks by inserting unconditional defaults
    at the beginning of an always_comb block.

    Supports multiple latch signals.
    """

    lines = rtl_code.splitlines()

    for diagnostic in diagnostics:
        if (
            diagnostic["category"]
            != "LATCH_RISK"
        ):
            continue

        message = diagnostic["message"]

        signal_match = re.search(
            r"[Ss]ignal\s+'([^']+)'",
            message,
        )

        if not signal_match:
            print(
                "Latch repair: could not identify signal"
            )
            continue

        signal_path = (
            signal_match.group(1)
        )

        signal_name = (
            signal_path.split(".")[-1]
        )

        print(
            f"Latch repair target: "
            f"{signal_name}"
        )

        rtl_text = "\n".join(lines)

        declaration_match = re.search(
            rf"\b(?:output\s+)?logic\s*"
            rf"(?:\[(\d+)\s*:\s*(\d+)\])?"
            rf"\s+{re.escape(signal_name)}\b",
            rtl_text,
        )

        if not declaration_match:
            print(
                f"Latch repair: declaration for "
                f"{signal_name} not found"
            )
            continue

        msb = declaration_match.group(1)
        lsb = declaration_match.group(2)

        if (
            msb is not None
            and lsb is not None
        ):
            width = (
                abs(
                    int(msb)
                    - int(lsb)
                )
                + 1
            )

            default_value = (
                f"{width}'d0"
            )

        else:
            default_value = "1'b0"

        default_assignment = (
            f"    {signal_name} = "
            f"{default_value};"
        )

        always_index = None
        begin_index = None

        for index, line in enumerate(
            lines
        ):
            if not re.search(
                r"\balways_comb\b",
                line,
            ):
                continue

            always_index = index

            if "begin" in line:
                begin_index = index

            else:
                for next_index in range(
                    index + 1,
                    len(lines),
                ):
                    if re.search(
                        r"\bbegin\b",
                        lines[next_index],
                    ):
                        begin_index = (
                            next_index
                        )
                        break

            break

        if (
            always_index is None
            or begin_index is None
        ):
            print(
                "Latch repair: always_comb "
                "block not found"
            )
            continue

        default_already_present = False
        scan_index = begin_index + 1

        while scan_index < len(lines):
            stripped = (
                lines[scan_index].strip()
            )

            if stripped == "":
                scan_index += 1
                continue

            if (
                re.match(
                    r"if\b",
                    stripped,
                )
                or re.match(
                    r"case\b",
                    stripped,
                )
                or re.match(
                    r"unique\s+case\b",
                    stripped,
                )
                or re.match(
                    r"priority\s+case\b",
                    stripped,
                )
                or re.match(
                    r"for\b",
                    stripped,
                )
                or re.match(
                    r"while\b",
                    stripped,
                )
            ):
                break

            if re.match(
                rf"{re.escape(signal_name)}"
                rf"\s*=\s*",
                stripped,
            ):
                default_already_present = True
                break

            scan_index += 1

        if default_already_present:
            print(
                f"Latch repair: "
                f"{signal_name} already has "
                f"unconditional default"
            )
            continue

        insert_index = begin_index + 1

        while insert_index < len(lines):
            stripped = (
                lines[insert_index].strip()
            )

            if stripped == "":
                insert_index += 1
                continue

            if re.match(
                r"[A-Za-z_][A-Za-z0-9_]*"
                r"\s*=",
                stripped,
            ):
                insert_index += 1
                continue

            break

        lines.insert(
            insert_index,
            default_assignment,
        )

        print(
            f"Latch repair: inserted default "
            f"{signal_name} = "
            f"{default_value}"
        )

    return "\n".join(lines)


# =========================================================
# UNDRIVEN SIGNAL REPAIR
# =========================================================

def repair_undriven_signal(
    rtl_code: str,
    diagnostics: list,
) -> str:
    """
    Repair simple undriven output signals.
    """

    lines = rtl_code.splitlines()
    rtl_text = "\n".join(lines)

    for diagnostic in diagnostics:
        if (
            diagnostic["category"]
            != "UNDRIVEN_SIGNAL"
        ):
            continue

        message = diagnostic["message"]

        signal_match = re.search(
            r"Signal is not driven:\s*'([^']+)'",
            message,
        )

        if not signal_match:
            print(
                "Undriven repair: could not "
                "identify signal"
            )
            continue

        signal_name = (
            signal_match.group(1)
        )

        print(
            f"Undriven repair target: "
            f"{signal_name}"
        )

        output_match = re.search(
            rf"\boutput\s+logic"
            rf"(?:\s*\[[^\]]+\])?"
            rf"\s+{re.escape(signal_name)}\b",
            rtl_text,
        )

        if not output_match:
            print(
                "Undriven repair: target is not "
                "a recognized output logic signal"
            )
            continue

        control_signal = None

        if signal_name.lower() == "valid":
            for candidate in [
                "enable",
                "en",
            ]:
                if re.search(
                    rf"\binput\s+logic"
                    rf"(?:\s*\[[^\]]+\])?"
                    rf"\s+{candidate}\b",
                    rtl_text,
                ):
                    control_signal = (
                        candidate
                    )
                    break

        if control_signal is not None:
            assignment = (
                f"assign {signal_name} = "
                f"{control_signal};"
            )

            print(
                f"Undriven repair: "
                f"{signal_name} driven by "
                f"{control_signal}"
            )

        else:
            assignment = (
                f"assign {signal_name} = "
                f"1'b0;"
            )

            print(
                f"Undriven repair: "
                f"{signal_name} assigned "
                f"safe default 0"
            )

        if re.search(
            rf"\bassign\s+"
            rf"{re.escape(signal_name)}"
            rf"\s*=",
            rtl_text,
        ):
            continue

        inserted = False

        for index in range(
            len(lines) - 1,
            -1,
            -1,
        ):
            if (
                lines[index].strip()
                == "endmodule"
            ):
                lines.insert(
                    index,
                    "",
                )

                lines.insert(
                    index + 1,
                    assignment,
                )

                inserted = True
                break

        if not inserted:
            print(
                "Undriven repair: "
                "endmodule not found"
            )

        rtl_text = "\n".join(lines)

    return "\n".join(lines)


# =========================================================
# PROCEDURAL BLOCK HELPERS
# =========================================================

def _find_always_block(
    lines: list,
    target_index: int,
):
    """
    Find always_ff or always_comb block containing
    target_index.
    """

    candidate_start = None

    for index in range(
        target_index,
        -1,
        -1,
    ):
        if re.search(
            r"\balways_(?:ff|comb)\b",
            lines[index],
        ):
            candidate_start = index
            break

    if candidate_start is None:
        return None

    begin_depth = 0
    seen_begin = False

    for index in range(
        candidate_start,
        len(lines),
    ):
        line = lines[index]

        begin_count = len(
            re.findall(
                r"\bbegin\b",
                line,
            )
        )

        end_count = len(
            re.findall(
                r"\bend\b",
                line,
            )
        )

        if begin_count > 0:
            seen_begin = True

        begin_depth += begin_count
        begin_depth -= end_count

        if (
            seen_begin
            and begin_depth == 0
        ):
            if (
                candidate_start
                <= target_index
                <= index
            ):
                return (
                    candidate_start,
                    index,
                )

            return None

    return None


def _line_is_standalone_assignment(
    line: str,
    signal_name: str,
) -> bool:
    """
    Check for a standalone procedural assignment.
    """

    pattern = (
        rf"^\s*"
        rf"{re.escape(signal_name)}"
        rf"\s*(?:<=|=)"
        rf".*;"
        rf"\s*(?://.*)?$"
    )

    return bool(
        re.match(
            pattern,
            line,
        )
    )


def _previous_significant_line(
    lines: list,
    index: int,
):
    """
    Return previous non-empty, non-comment line.
    """

    for previous_index in range(
        index - 1,
        -1,
        -1,
    ):
        stripped = (
            lines[previous_index].strip()
        )

        if stripped == "":
            continue

        if stripped.startswith("//"):
            continue

        return stripped

    return None


def _safe_to_remove_assignment_line(
    lines: list,
    index: int,
    signal_name: str,
) -> bool:
    """
    Avoid deleting the only statement under an unbraced
    if/else/for/while.
    """

    if not _line_is_standalone_assignment(
        lines[index],
        signal_name,
    ):
        return False

    previous = _previous_significant_line(
        lines,
        index,
    )

    if previous is None:
        return True

    unbraced_control_patterns = [
        r"^if\b.*\)\s*$",
        r"^else\s*$",
        r"^else\s+if\b.*\)\s*$",
        r"^for\b.*\)\s*$",
        r"^while\b.*\)\s*$",
    ]

    for pattern in unbraced_control_patterns:
        if re.match(
            pattern,
            previous,
        ):
            return False

    return True


# =========================================================
# UNUSED INTERNAL SIGNAL CLEANUP
# =========================================================

def repair_unused_signal(
    rtl_code: str,
    diagnostics: list,
) -> str:
    """
    Conservatively clean dead internal logic.
    """

    lines = rtl_code.splitlines()

    for diagnostic in diagnostics:
        if (
            diagnostic["category"]
            != "UNUSED_SIGNAL"
        ):
            continue

        message = diagnostic["message"]

        signal_match = re.search(
            r"Signal is not used:\s*'([^']+)'",
            message,
        )

        if not signal_match:
            print(
                "Unused repair: could not "
                "identify signal"
            )
            continue

        signal_name = (
            signal_match.group(1)
        )

        print(
            f"Unused repair target: "
            f"{signal_name}"
        )

        port_pattern = (
            rf"^\s*(?:input|output|inout)\b"
            rf".*\b{re.escape(signal_name)}\b"
        )

        is_port = any(
            re.search(
                port_pattern,
                line,
            )
            for line in lines
        )

        if is_port:
            print(
                f"Unused repair: "
                f"{signal_name} is a port; "
                f"leaving for review"
            )
            continue

        declaration_pattern = re.compile(
            rf"^\s*logic\s*"
            rf"(?:\[[^\]]+\]\s*)?"
            rf"{re.escape(signal_name)}"
            rf"\s*;\s*$"
        )

        declaration_index = None

        for index, line in enumerate(
            lines
        ):
            if declaration_pattern.match(
                line
            ):
                declaration_index = index
                break

        if declaration_index is None:
            print(
                f"Unused repair: internal "
                f"declaration for "
                f"{signal_name} not found; "
                f"leaving for review"
            )
            continue

        occurrence_indices = []

        for index, line in enumerate(
            lines
        ):
            if re.search(
                rf"\b{re.escape(signal_name)}\b",
                line,
            ):
                occurrence_indices.append(
                    index
                )

        assignment_indices = []
        unsafe_reference = False

        for index in occurrence_indices:
            if index == declaration_index:
                continue

            stripped = (
                lines[index].strip()
            )

            assignment_match = re.match(
                rf"{re.escape(signal_name)}"
                rf"\s*(?:<=|=)",
                stripped,
            )

            if assignment_match:
                assignment_indices.append(
                    index
                )
                continue

            unsafe_reference = True

            print(
                f"Unused repair: "
                f"{signal_name} has a "
                f"non-assignment reference; "
                f"leaving for review"
            )

            break

        if unsafe_reference:
            continue

        if not assignment_indices:
            print(
                f"Unused repair: "
                f"{signal_name} has no recognized "
                f"assignments; leaving for review"
            )
            continue

        block_map = {}
        safe_to_remove = True

        for assignment_index in (
            assignment_indices
        ):
            block = _find_always_block(
                lines,
                assignment_index,
            )

            if block is None:
                print(
                    f"Unused repair: assignment to "
                    f"{signal_name} is outside a "
                    f"recognized procedural block; "
                    f"leaving for review"
                )

                safe_to_remove = False
                break

            if block not in block_map:
                block_map[block] = []

            block_map[block].append(
                assignment_index
            )

        if not safe_to_remove:
            continue

        blocks_to_remove = set()
        assignment_lines_to_remove = set()

        for block, signal_assignments in (
            block_map.items()
        ):
            block_start, block_end = (
                block
            )

            block_lhs_signals = set()

            for block_line_index in range(
                block_start,
                block_end + 1,
            ):
                block_line = (
                    lines[block_line_index]
                )

                lhs_match = re.search(
                    r"^\s*"
                    r"([A-Za-z_][A-Za-z0-9_]*)"
                    r"\s*(?:<=|=)",
                    block_line,
                )

                if lhs_match:
                    block_lhs_signals.add(
                        lhs_match.group(1)
                    )

            if block_lhs_signals == {
                signal_name
            }:
                print(
                    f"Unused repair: removing dead "
                    f"procedural block for "
                    f"{signal_name}"
                )

                blocks_to_remove.add(
                    block
                )
                continue

            print(
                f"Unused repair: procedural block "
                f"for {signal_name} also drives "
                f"live signals"
            )

            for assignment_index in (
                signal_assignments
            ):
                if not _safe_to_remove_assignment_line(
                    lines,
                    assignment_index,
                    signal_name,
                ):
                    print(
                        f"Unused repair: assignment to "
                        f"{signal_name} cannot be safely "
                        f"removed individually; "
                        f"leaving for review"
                    )

                    safe_to_remove = False
                    break

                assignment_lines_to_remove.add(
                    assignment_index
                )

            if not safe_to_remove:
                break

        if not safe_to_remove:
            continue

        filtered_assignment_lines = set()

        for assignment_index in (
            assignment_lines_to_remove
        ):
            inside_removed_block = False

            for (
                block_start,
                block_end,
            ) in blocks_to_remove:
                if (
                    block_start
                    <= assignment_index
                    <= block_end
                ):
                    inside_removed_block = True
                    break

            if not inside_removed_block:
                filtered_assignment_lines.add(
                    assignment_index
                )

        deletion_ranges = []

        for (
            block_start,
            block_end,
        ) in blocks_to_remove:
            deletion_ranges.append(
                (
                    block_start,
                    block_end,
                    "block",
                )
            )

        for assignment_index in (
            filtered_assignment_lines
        ):
            deletion_ranges.append(
                (
                    assignment_index,
                    assignment_index,
                    "assignment",
                )
            )

        deletion_ranges.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        for (
            start_index,
            end_index,
            deletion_type,
        ) in deletion_ranges:

            if deletion_type == "assignment":
                print(
                    f"Unused repair: removing dead "
                    f"assignment to "
                    f"{signal_name}"
                )

            del lines[
                start_index:
                end_index + 1
            ]

        declaration_index = None

        for index, line in enumerate(
            lines
        ):
            if declaration_pattern.match(
                line
            ):
                declaration_index = index
                break

        if declaration_index is None:
            print(
                f"Unused repair: declaration for "
                f"{signal_name} disappeared "
                f"unexpectedly"
            )
            continue

        remaining_references = []

        for index, line in enumerate(
            lines
        ):
            if index == declaration_index:
                continue

            if re.search(
                rf"\b{re.escape(signal_name)}\b",
                line,
            ):
                remaining_references.append(
                    (
                        index,
                        line,
                    )
                )

        if remaining_references:
            print(
                f"Unused repair: references to "
                f"{signal_name} remain after cleanup; "
                f"keeping declaration for review"
            )
            continue

        print(
            f"Unused repair: removing declaration "
            f"for {signal_name}"
        )

        del lines[
            declaration_index
        ]

    return "\n".join(lines)


# =========================================================
# MISSING COMBINATIONAL DEFAULT REPAIR
# =========================================================

def repair_missing_comb_defaults(
    rtl_code: str,
) -> str:
    """
    Add safe zero defaults for module output logic signals
    assigned inside always_comb but not assigned
    unconditionally before control flow begins.

    This is intentionally restricted to module outputs.
    """

    lines = rtl_code.splitlines()
    rtl_text = "\n".join(lines)

    # -----------------------------------------------------
    # Discover output logic declarations and widths.
    # -----------------------------------------------------

    output_widths = {}

    output_pattern = re.compile(
        r"\boutput\s+logic\s*"
        r"(?:\[(\d+)\s*:\s*(\d+)\])?"
        r"\s+([A-Za-z_][A-Za-z0-9_]*)"
    )

    for match in output_pattern.finditer(
        rtl_text
    ):
        msb = match.group(1)
        lsb = match.group(2)
        signal_name = match.group(3)

        if (
            msb is not None
            and lsb is not None
        ):
            width = (
                abs(
                    int(msb)
                    - int(lsb)
                )
                + 1
            )

        else:
            width = 1

        output_widths[
            signal_name
        ] = width

    if not output_widths:
        return rtl_code

    index = 0

    while index < len(lines):

        if not re.search(
            r"\balways_comb\b",
            lines[index],
        ):
            index += 1
            continue

        block_start = index

        # -------------------------------------------------
        # Find end of this always_comb block.
        # -------------------------------------------------

        begin_depth = 0
        seen_begin = False
        block_end = None

        scan = block_start

        while scan < len(lines):
            current_line = lines[scan]

            begin_count = len(
                re.findall(
                    r"\bbegin\b",
                    current_line,
                )
            )

            end_count = len(
                re.findall(
                    r"\bend\b",
                    current_line,
                )
            )

            if begin_count > 0:
                seen_begin = True

            begin_depth += begin_count
            begin_depth -= end_count

            if (
                seen_begin
                and begin_depth == 0
            ):
                block_end = scan
                break

            scan += 1

        if block_end is None:
            index += 1
            continue

        # -------------------------------------------------
        # Identify output signals assigned anywhere in
        # this always_comb block.
        # -------------------------------------------------

        assigned_outputs = set()

        for block_index in range(
            block_start,
            block_end + 1,
        ):
            assignment_match = re.search(
                r"^\s*"
                r"([A-Za-z_][A-Za-z0-9_]*)"
                r"\s*=",
                lines[block_index],
            )

            if not assignment_match:
                continue

            signal_name = (
                assignment_match.group(1)
            )

            if signal_name in output_widths:
                assigned_outputs.add(
                    signal_name
                )

        if not assigned_outputs:
            index = block_end + 1
            continue

        # -------------------------------------------------
        # Find the begin line.
        # -------------------------------------------------

        begin_index = block_start

        if "begin" not in lines[
            block_start
        ]:
            for search_index in range(
                block_start + 1,
                block_end + 1,
            ):
                if re.search(
                    r"\bbegin\b",
                    lines[search_index],
                ):
                    begin_index = (
                        search_index
                    )
                    break

        # -------------------------------------------------
        # Determine which outputs already have
        # unconditional defaults at the beginning.
        # -------------------------------------------------

        existing_defaults = set()

        scan_index = (
            begin_index + 1
        )

        while scan_index < block_end:
            stripped = (
                lines[scan_index].strip()
            )

            if stripped == "":
                scan_index += 1
                continue

            if (
                re.match(
                    r"if\b",
                    stripped,
                )
                or re.match(
                    r"case\b",
                    stripped,
                )
                or re.match(
                    r"unique\s+case\b",
                    stripped,
                )
                or re.match(
                    r"priority\s+case\b",
                    stripped,
                )
                or re.match(
                    r"for\b",
                    stripped,
                )
                or re.match(
                    r"while\b",
                    stripped,
                )
            ):
                break

            default_match = re.match(
                r"([A-Za-z_][A-Za-z0-9_]*)"
                r"\s*=",
                stripped,
            )

            if default_match:
                signal_name = (
                    default_match.group(1)
                )

                if signal_name in output_widths:
                    existing_defaults.add(
                        signal_name
                    )

                scan_index += 1
                continue

            break

        missing_defaults = (
            assigned_outputs
            - existing_defaults
        )

        if not missing_defaults:
            index = block_end + 1
            continue

        # -------------------------------------------------
        # Insert after existing top-level assignments.
        # -------------------------------------------------

        insert_index = (
            begin_index + 1
        )

        while insert_index < block_end:
            stripped = (
                lines[insert_index].strip()
            )

            if stripped == "":
                insert_index += 1
                continue

            if re.match(
                r"[A-Za-z_][A-Za-z0-9_]*"
                r"\s*=",
                stripped,
            ):
                insert_index += 1
                continue

            break

        defaults_to_insert = []

        for signal_name in sorted(
            missing_defaults
        ):
            width = output_widths[
                signal_name
            ]

            if width == 1:
                default_value = "1'b0"

            else:
                default_value = (
                    f"{width}'d0"
                )

            defaults_to_insert.append(
                f"    {signal_name} = "
                f"{default_value};"
            )

            print(
                "Comb default repair: inserted "
                f"{signal_name} = "
                f"{default_value}"
            )

        for offset, default_line in enumerate(
            defaults_to_insert
        ):
            lines.insert(
                insert_index + offset,
                default_line,
            )

        index = (
            block_end
            + len(defaults_to_insert)
            + 1
        )

    return "\n".join(lines)


# =========================================================
# STYLE REPAIR
# =========================================================

def repair_style(
    rtl_code: str,
) -> str:
    """
    Ensure RTL ends with exactly one newline.
    """

    return (
        rtl_code.rstrip()
        + "\n"
    )


# =========================================================
# EXECUTE SELECTED STRATEGIES
# =========================================================

def execute_strategies(
    input_file: str,
    output_file: str,
) -> dict:
    """
    Analyze diagnostics, route repair strategies,
    apply selected repairs, and write repaired RTL.
    """

    print(
        "=== SiliconPilot Strategy Executor ==="
    )

    input_path = Path(
        input_file
    )

    output_path = Path(
        output_file
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    rtl_code = input_path.read_text(
        encoding="utf-8",
    )

    classified = classify_diagnostics(
        str(input_path)
    )

    diagnostics = classified[
        "diagnostics"
    ]

    routing = route_repairs(
        str(input_path)
    )

    strategies = routing.get(
        "strategies",
        [],
    )

    print(
        "\nSelected strategies:"
    )

    if not strategies:
        print(
            "- No repair required"
        )

    for item in strategies:
        print(
            f"- {item['category']} "
            f"→ {item['strategy']}"
        )

    repaired_code = rtl_code

    strategy_names = {
        item["strategy"]
        for item in strategies
    }

    # -----------------------------------------------------
    # 1. Sequential assignment repair
    # -----------------------------------------------------

    if (
        "repair_sequential_assignments"
        in strategy_names
    ):
        repaired_code = (
            repair_sequential_assignments(
                repaired_code
            )
        )

    # -----------------------------------------------------
    # 2. Width mismatch repair
    # -----------------------------------------------------

    if (
        "repair_width_mismatch"
        in strategy_names
    ):
        repaired_code = (
            repair_width_mismatch(
                repaired_code,
                diagnostics,
            )
        )

    # -----------------------------------------------------
    # 3. Latch repair
    # -----------------------------------------------------

    if (
        "repair_combinational_latch"
        in strategy_names
    ):
        repaired_code = (
            repair_latch_risk(
                repaired_code,
                diagnostics,
            )
        )

    # -----------------------------------------------------
    # 4. Undriven output repair
    # -----------------------------------------------------

    if (
        "repair_undriven_signal"
        in strategy_names
    ):
        repaired_code = (
            repair_undriven_signal(
                repaired_code,
                diagnostics,
            )
        )

    # -----------------------------------------------------
    # 5. Unused internal signal cleanup
    # -----------------------------------------------------

    if (
        "review_unused_signal"
        in strategy_names
    ):
        repaired_code = (
            repair_unused_signal(
                repaired_code,
                diagnostics,
            )
        )

    # -----------------------------------------------------
    # 6. Missing combinational defaults
    #
    # Always run this safety pass because functional
    # simulation can expose incomplete combinational
    # behavior even when lint reports no latch warning.
    # -----------------------------------------------------

    repaired_code = (
        repair_missing_comb_defaults(
            repaired_code
        )
    )

    # -----------------------------------------------------
    # 7. Style repair
    # -----------------------------------------------------

    if (
        "repair_style"
        in strategy_names
    ):
        repaired_code = (
            repair_style(
                repaired_code
            )
        )

    # -----------------------------------------------------
    # Always finish with one newline.
    # -----------------------------------------------------

    repaired_code = (
        repaired_code.rstrip()
        + "\n"
    )

    output_path.write_text(
        repaired_code,
        encoding="utf-8",
    )

    print(
        "\nRepaired RTL saved to: "
        f"{output_path}"
    )

    return {
        "input_file": str(
            input_path
        ),
        "output_file": str(
            output_path
        ),
        "strategies": strategies,
        "repaired_code": repaired_code,
    }


# =========================================================
# MANUAL TEST
# =========================================================

if __name__ == "__main__":
    execute_strategies(
        "unseen_tests/unseen_latch_fsm_06.sv",
        "unseen_outputs/unseen_latch_fsm_06.sv",
    )