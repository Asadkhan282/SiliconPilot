`timescale 1ns/1ps

module tb_mixed_seq_latch;

    logic clk;
    logic reset;
    logic enable;
    logic [7:0] data_in;
    logic [7:0] data_reg;
    logic [7:0] selected_data;

    mixed_seq_latch dut (
        .clk(clk),
        .reset(reset),
        .enable(enable),
        .data_in(data_in),
        .data_reg(data_reg),
        .selected_data(selected_data)
    );

    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end

    initial begin
        reset = 1;
        enable = 0;
        data_in = 8'h00;

        @(posedge clk);
        #1;

        if (data_reg !== 8'h00) begin
            $display(
                "TEST_FAIL: reset data_reg expected 00 got %0h",
                data_reg
            );
            $finish;
        end

        if (selected_data !== 8'h00) begin
            $display(
                "TEST_FAIL: disabled selected_data expected 00 got %0h",
                selected_data
            );
            $finish;
        end

        reset = 0;
        data_in = 8'h5A;

        @(posedge clk);
        #1;

        if (data_reg !== 8'h5A) begin
            $display(
                "TEST_FAIL: data_reg expected 5A got %0h",
                data_reg
            );
            $finish;
        end

        enable = 1;
        #1;

        if (selected_data !== 8'h5A) begin
            $display(
                "TEST_FAIL: selected_data expected 5A got %0h",
                selected_data
            );
            $finish;
        end

        enable = 0;
        #1;

        if (selected_data !== 8'h00) begin
            $display(
                "TEST_FAIL: selected_data expected 00 when disabled got %0h",
                selected_data
            );
            $finish;
        end

        $display(
            "TEST_PASS: mixed_seq_latch functional verification passed"
        );

        $finish;
    end

endmodule