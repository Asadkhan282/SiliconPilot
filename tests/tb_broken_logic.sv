`timescale 1ns/1ps

module tb_broken_logic;

    logic       clk;
    logic       reset;
    logic       en;
    logic [7:0] data_in;
    logic [7:0] data_out;
    logic       valid;

    broken_logic dut (
        .clk(clk),
        .reset(reset),
        .en(en),
        .data_in(data_in),
        .data_out(data_out),
        .valid(valid)
    );

    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end

    initial begin
        reset   = 1;
        en      = 0;
        data_in = 8'h00;

        @(posedge clk);
        #1;

        if (data_out !== 8'h00) begin
            $display(
                "TEST_FAIL: reset data_out expected 00 got %0h",
                data_out
            );
            $finish;
        end

        if (valid !== 1'b0) begin
            $display(
                "TEST_FAIL: reset valid expected 0 got %0b",
                valid
            );
            $finish;
        end

        reset = 0;

        // Test normal data load
        en      = 1;
        data_in = 8'h25;

        @(posedge clk);
        #1;

        if (data_out !== 8'h25) begin
            $display(
                "TEST_FAIL: data_out expected 25 got %0h",
                data_out
            );
            $finish;
        end

        // Test valid assertion
        data_in = 8'hFF;

        @(posedge clk);
        #1;

        if (data_out !== 8'hFF) begin
            $display(
                "TEST_FAIL: data_out expected FF got %0h",
                data_out
            );
            $finish;
        end

        if (valid !== 1'b1) begin
            $display(
                "TEST_FAIL: valid expected 1 got %0b",
                valid
            );
            $finish;
        end

        // Test hold behavior when enable is low
        en      = 0;
        data_in = 8'h10;

        @(posedge clk);
        #1;

        if (data_out !== 8'hFF) begin
            $display(
                "TEST_FAIL: data_out should hold FF got %0h",
                data_out
            );
            $finish;
        end

        if (valid !== 1'b1) begin
            $display(
                "TEST_FAIL: valid should remain asserted"
            );
            $finish;
        end

        $display(
            "TEST_PASS: broken_logic functional verification passed"
        );

        $finish;
    end

endmodule