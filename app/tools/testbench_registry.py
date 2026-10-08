from pathlib import Path

TESTBENCH_REGISTRY = {
    "broken_alu.sv": "tests/tb_broken_alu.sv",
    "broken_logic.sv": "tests/tb_broken_logic.sv",
    "broken_width.sv": "tests/tb_broken_width.sv",
    "broken_latch.sv": "tests/tb_broken_latch.sv",
    "broken_seq2.sv": "tests/tb_broken_seq2.sv",
    "broken_width2.sv": "tests/tb_broken_width2.sv",
    "mixed_seq_width.sv": "tests/tb_mixed_seq_width.sv",
    "mixed_latch_width.sv": "tests/tb_mixed_latch_width.sv",
    "mixed_seq_latch.sv": "tests/tb_mixed_seq_latch.sv",
    "multi_fault_datapath.sv": "tests/tb_multi_fault_datapath.sv",
    "broken_fsm.sv": "tests/tb_broken_fsm.sv",
    "mixed_fsm_datapath.sv": "tests/tb_mixed_fsm_datapath.sv",
    "undriven_output.sv": "tests/tb_undriven_output.sv",
    "multi_output_width.sv": "tests/tb_multi_output_width.sv",
    "nested_control_fault.sv": "tests/tb_nested_control_fault.sv",
    "final_multi_fault.sv": "tests/tb_final_multi_fault.sv",
}

def get_testbench(rtl_filename: str):
    safe_name = Path(rtl_filename).name

    return TESTBENCH_REGISTRY.get(
        safe_name
    )