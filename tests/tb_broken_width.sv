`timescale 1ns/1ps

module tb_broken_width;

    logic [7:0] a;
    logic [7:0] b;
    logic [7:0] result;

    broken_width dut (
        .a(a),
        .b(b),
        .result(result)
    );

    initial begin
        a = 8'd10;
        b = 8'd5;
        #1;

        if (result !== 8'd15) begin
            $display(
                "TEST_FAIL: expected 15 got %0d",
                result
            );
            $finish;
        end

        a = 8'd100;
        b = 8'd20;
        #1;

        if (result !== 8'd120) begin
            $display(
                "TEST_FAIL: expected 120 got %0d",
                result
            );
            $finish;
        end

        a = 8'd200;
        b = 8'd30;
        #1;

        if (result !== 8'd230) begin
            $display(
                "TEST_FAIL: expected 230 got %0d",
                result
            );
            $finish;
        end

        $display(
            "TEST_PASS: broken_width functional verification passed"
        );

        $finish;
    end

endmodule