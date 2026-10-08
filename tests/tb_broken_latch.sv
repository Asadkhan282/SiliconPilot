`timescale 1ns/1ps

module tb_broken_latch;

    logic       enable;
    logic [7:0] data_in;
    logic [7:0] data_out;

    broken_latch dut (
        .enable(enable),
        .data_in(data_in),
        .data_out(data_out)
    );

    initial begin
        enable  = 0;
        data_in = 8'h55;
        #1;

        if (data_out !== 8'h00) begin
            $display(
                "TEST_FAIL: default output expected 00 got %0h",
                data_out
            );
            $finish;
        end

        enable  = 1;
        data_in = 8'hA5;
        #1;

        if (data_out !== 8'hA5) begin
            $display(
                "TEST_FAIL: enabled output expected A5 got %0h",
                data_out
            );
            $finish;
        end

        enable  = 0;
        data_in = 8'h3C;
        #1;

        if (data_out !== 8'h00) begin
            $display(
                "TEST_FAIL: disabled output expected 00 got %0h",
                data_out
            );
            $finish;
        end

        $display(
            "TEST_PASS: broken_latch functional verification passed"
        );

        $finish;
    end

endmodule