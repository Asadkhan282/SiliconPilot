`timescale 1ns/1ps

module tb_multi_fault_datapath;

    logic clk;
    logic reset;
    logic enable;
    logic [15:0] a;
    logic [15:0] b;
    logic [15:0] result;
    logic [15:0] result_reg;

    multi_fault_datapath dut (
        .clk(clk),
        .reset(reset),
        .enable(enable),
        .a(a),
        .b(b),
        .result(result),
        .result_reg(result_reg)
    );

    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end

    initial begin
        reset = 1;
        enable = 0;
        a = 16'd0;
        b = 16'd0;

        @(posedge clk);
        #1;

        if (result_reg !== 16'd0) begin
            $display("TEST_FAIL: reset failed");
            $finish;
        end

        reset = 0;
        enable = 1;
        a = 16'd1000;
        b = 16'd500;

        #1;

        if (result !== 16'd1500) begin
            $display(
                "TEST_FAIL: combinational result expected 1500 got %0d",
                result
            );
            $finish;
        end

        @(posedge clk);
        #1;

        if (result_reg !== 16'd1500) begin
            $display(
                "TEST_FAIL: registered result expected 1500 got %0d",
                result_reg
            );
            $finish;
        end

        a = 16'd20000;
        b = 16'd10000;

        #1;

        if (result !== 16'd30000) begin
            $display(
                "TEST_FAIL: combinational result expected 30000 got %0d",
                result
            );
            $finish;
        end

        @(posedge clk);
        #1;

        if (result_reg !== 16'd30000) begin
            $display(
                "TEST_FAIL: registered result expected 30000 got %0d",
                result_reg
            );
            $finish;
        end

        enable = 0;
        #1;

        if (result !== 16'd0) begin
            $display(
                "TEST_FAIL: disabled result expected 0 got %0d",
                result
            );
            $finish;
        end

        $display(
            "TEST_PASS: multi_fault_datapath functional verification passed"
        );

        $finish;
    end

endmodule