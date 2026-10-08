`timescale 1ns/1ps

module tb_broken_alu;

    logic clk;
    logic reset;
    logic [7:0] a;
    logic [7:0] b;
    logic [1:0] op;
    logic [7:0] result;

    broken_alu dut (
        .clk(clk),
        .reset(reset),
        .a(a),
        .b(b),
        .op(op),
        .result(result)
    );

    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end

    initial begin
        reset = 1;
        a = 0;
        b = 0;
        op = 0;

        @(posedge clk);
        #1;

        if (result !== 8'd0) begin
            $display("TEST_FAIL: reset expected 0 got %0d", result);
            $finish;
        end

        reset = 0;

        a = 8'd10;
        b = 8'd5;
        op = 2'b00;

        @(posedge clk);
        #1;

        if (result !== 8'd15) begin
            $display("TEST_FAIL: add expected 15 got %0d", result);
            $finish;
        end

        a = 8'd10;
        b = 8'd5;
        op = 2'b01;

        @(posedge clk);
        #1;

        if (result !== 8'd5) begin
            $display("TEST_FAIL: subtract expected 5 got %0d", result);
            $finish;
        end

        a = 8'hF0;
        b = 8'h0F;
        op = 2'b10;

        @(posedge clk);
        #1;

        if (result !== 8'h00) begin
            $display("TEST_FAIL: AND expected 0 got %0h", result);
            $finish;
        end

        $display("TEST_PASS: broken_alu functional verification passed");
        $finish;
    end

endmodule