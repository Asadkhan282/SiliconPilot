`timescale 1ns/1ps

module tb_mixed_seq_width;

    logic clk;
    logic reset;
    logic [15:0] a;
    logic [15:0] b;
    logic [15:0] result;
    logic [7:0] count;

    mixed_seq_width dut (
        .clk(clk),
        .reset(reset),
        .a(a),
        .b(b),
        .result(result),
        .count(count)
    );

    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end

    initial begin
        reset = 1;
        a = 16'd0;
        b = 16'd0;

        @(posedge clk);
        #1;

        if (result !== 16'd0 || count !== 8'd0) begin
            $display("TEST_FAIL: reset behavior incorrect");
            $finish;
        end

        reset = 0;
        a = 16'd1000;
        b = 16'd500;

        @(posedge clk);
        #1;

        if (result !== 16'd1500) begin
            $display(
                "TEST_FAIL: expected result 1500 got %0d",
                result
            );
            $finish;
        end

        if (count !== 8'd1) begin
            $display(
                "TEST_FAIL: expected count 1 got %0d",
                count
            );
            $finish;
        end

        a = 16'd20000;
        b = 16'd10000;

        @(posedge clk);
        #1;

        if (result !== 16'd30000) begin
            $display(
                "TEST_FAIL: expected result 30000 got %0d",
                result
            );
            $finish;
        end

        if (count !== 8'd2) begin
            $display(
                "TEST_FAIL: expected count 2 got %0d",
                count
            );
            $finish;
        end

        $display(
            "TEST_PASS: mixed_seq_width functional verification passed"
        );

        $finish;
    end

endmodule