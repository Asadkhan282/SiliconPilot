`timescale 1ns/1ps

module tb_mixed_fsm_datapath;

    logic clk;
    logic reset;
    logic start;
    logic done;

    logic [15:0] a;
    logic [15:0] b;

    logic [15:0] result;
    logic busy;

    mixed_fsm_datapath dut (
        .clk(clk),
        .reset(reset),
        .start(start),
        .done(done),
        .a(a),
        .b(b),
        .result(result),
        .busy(busy)
    );

    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end

    initial begin
        reset = 1;
        start = 0;
        done = 0;

        a = 16'd1000;
        b = 16'd500;

        @(posedge clk);
        #1;

        reset = 0;
        start = 1;

        @(posedge clk);
        #1;

        start = 0;

        if (busy !== 1'b1) begin
            $display("TEST_FAIL: FSM did not enter RUN");
            $finish;
        end

        if (result !== 16'd1500) begin
            $display(
                "TEST_FAIL: expected result 1500 got %0d",
                result
            );
            $finish;
        end

        a = 16'd20000;
        b = 16'd10000;

        #1;

        if (result !== 16'd30000) begin
            $display(
                "TEST_FAIL: expected result 30000 got %0d",
                result
            );
            $finish;
        end

        done = 1;

        @(posedge clk);
        #1;

        done = 0;

        @(posedge clk);
        #1;

        if (busy !== 1'b0) begin
            $display("TEST_FAIL: FSM did not return to IDLE");
            $finish;
        end

        $display(
            "TEST_PASS: mixed_fsm_datapath functional verification passed"
        );

        $finish;
    end

endmodule