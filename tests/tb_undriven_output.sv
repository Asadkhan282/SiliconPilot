`timescale 1ns/1ps

module tb_undriven_output;

    logic enable;
    logic [7:0] data_in;

    logic [7:0] data_out;
    logic valid;

    undriven_output dut (
        .enable(enable),
        .data_in(data_in),
        .data_out(data_out),
        .valid(valid)
    );

    initial begin
        enable = 0;
        data_in = 8'h00;

        #1;

        if (data_out !== 8'h00) begin
            $display(
                "TEST_FAIL: disabled data_out expected 00 got %0h",
                data_out
            );
            $finish;
        end

        if (valid !== 1'b0) begin
            $display(
                "TEST_FAIL: valid expected 0 when disabled"
            );
            $finish;
        end

        enable = 1;
        data_in = 8'hA5;

        #1;

        if (data_out !== 8'hA5) begin
            $display(
                "TEST_FAIL: data_out expected A5 got %0h",
                data_out
            );
            $finish;
        end

        if (valid !== 1'b1) begin
            $display(
                "TEST_FAIL: valid expected 1 when enabled"
            );
            $finish;
        end

        $display(
            "TEST_PASS: undriven_output functional verification passed"
        );

        $finish;
    end

endmodule