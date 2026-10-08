`timescale 1ns/1ps

module tb_broken_fsm;

    logic clk;
    logic reset;
    logic start;
    logic done;

    logic busy;
    logic complete;

    broken_fsm dut (
        .clk(clk),
        .reset(reset),
        .start(start),
        .done(done),
        .busy(busy),
        .complete(complete)
    );

    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end

    initial begin

        reset = 1;
        start = 0;
        done = 0;

        @(posedge clk);
        #1;

        reset = 0;

        #1;

        if (busy !== 1'b0) begin
            $display(
                "TEST_FAIL: busy should be 0 in IDLE"
            );
            $finish;
        end

        if (complete !== 1'b0) begin
            $display(
                "TEST_FAIL: complete should be 0 in IDLE"
            );
            $finish;
        end

        start = 1;

        @(posedge clk);
        #1;

        start = 0;

        if (busy !== 1'b1) begin
            $display(
                "TEST_FAIL: busy should be 1 in RUN"
            );
            $finish;
        end

        done = 1;

        @(posedge clk);
        #1;

        done = 0;

        if (complete !== 1'b1) begin
            $display(
                "TEST_FAIL: complete should be 1 in DONE"
            );
            $finish;
        end

        @(posedge clk);
        #1;

        if (busy !== 1'b0) begin
            $display(
                "TEST_FAIL: busy should return to 0"
            );
            $finish;
        end

        if (complete !== 1'b0) begin
            $display(
                "TEST_FAIL: complete should return to 0"
            );
            $finish;
        end

        $display(
            "TEST_PASS: broken_fsm functional verification passed"
        );

        $finish;

    end

endmodule