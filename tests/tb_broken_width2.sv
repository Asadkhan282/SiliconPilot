`timescale 1ns/1ps

module tb_broken_width2;

    logic [15:0] a;
    logic [15:0] b;
    logic [15:0] result;

    broken_width2 dut (
        .a(a),
        .b(b),
        .result(result)
    );

    initial begin
        a = 16'd1000;
        b = 16'd500;
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

        $display(
            "TEST_PASS: broken_width2 functional verification passed"
        );

        $finish;
    end

endmodule