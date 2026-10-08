`timescale 1ns/1ps

module tb_nested_control_fault;

    logic mode;
    logic enable;

    logic [7:0] data_a;
    logic [7:0] data_b;

    logic [7:0] result;
    logic valid;

    nested_control_fault dut (
        .mode(mode),
        .enable(enable),
        .data_a(data_a),
        .data_b(data_b),
        .result(result),
        .valid(valid)
    );

    initial begin

        data_a = 8'hA5;
        data_b = 8'h3C;

        mode = 0;
        enable = 0;

        #1;

        if (result !== 8'h3C) begin
            $display(
                "TEST_FAIL: mode=0 result expected 3C got %0h",
                result
            );
            $finish;
        end

        if (valid !== 1'b0) begin
            $display(
                "TEST_FAIL: mode=0 valid expected 0"
            );
            $finish;
        end

        mode = 1;
        enable = 1;

        #1;

        if (result !== 8'hA5) begin
            $display(
                "TEST_FAIL: enabled result expected A5 got %0h",
                result
            );
            $finish;
        end

        if (valid !== 1'b1) begin
            $display(
                "TEST_FAIL: enabled valid expected 1"
            );
            $finish;
        end

        mode = 1;
        enable = 0;

        #1;

        if (result !== 8'h00) begin
            $display(
                "TEST_FAIL: disabled nested result expected 00 got %0h",
                result
            );
            $finish;
        end

        if (valid !== 1'b0) begin
            $display(
                "TEST_FAIL: disabled nested valid expected 0"
            );
            $finish;
        end

        $display(
            "TEST_PASS: nested_control_fault functional verification passed"
        );

        $finish;

    end

endmodule