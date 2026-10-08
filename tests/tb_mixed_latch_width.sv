`timescale 1ns/1ps

module tb_mixed_latch_width;

    logic        enable;
    logic [15:0] a;
    logic [15:0] b;
    logic [15:0] result;

    mixed_latch_width dut (
        .enable(enable),
        .a(a),
        .b(b),
        .result(result)
    );

    initial begin
        enable = 0;
        a = 16'd1000;
        b = 16'd500;

        #1;

        if (result !== 16'd0) begin
            $display(
                "TEST_FAIL: disabled output expected 0 got %0d",
                result
            );
            $finish;
        end

        enable = 1;

        #1;

        if (result !== 16'd1500) begin
            $display(
                "TEST_FAIL: expected 1500 got %0d",
                result
            );
            $finish;
        end

        a = 16'd20000;
        b = 16'd10000;

        #1;

        if (result !== 16'd30000) begin
            $display(
                "TEST_FAIL: expected 30000 got %0d",
                result
            );
            $finish;
        end

        enable = 0;

        #1;

        if (result !== 16'd0) begin
            $display(
                "TEST_FAIL: disabled output expected 0 got %0d",
                result
            );
            $finish;
        end

        $display(
            "TEST_PASS: mixed_latch_width functional verification passed"
        );

        $finish;
    end

endmodule