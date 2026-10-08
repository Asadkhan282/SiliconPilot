`timescale 1ns/1ps

module tb_unseen_fsm_02;

    logic        clk;
    logic        reset;
    logic        start;
    logic [15:0] data_a;
    logic [15:0] data_b;

    logic [15:0] result;
    logic        busy;
    logic        done;

    unseen_fsm_02 dut (
        .clk(clk),
        .reset(reset),
        .start(start),
        .data_a(data_a),
        .data_b(data_b),
        .result(result),
        .busy(busy),
        .done(done)
    );

    initial begin
        clk = 1'b0;
        forever #5 clk = ~clk;
    end

    initial begin

        reset  = 1'b1;
        start  = 1'b0;
        data_a = 16'd100;
        data_b = 16'd50;

        // Reset
        @(posedge clk);
        #1;

        reset = 1'b0;

        if (busy !== 1'b0) begin
            $display(
                "TEST_FAIL: busy expected 0 after reset"
            );
            $finish;
        end

        // Start FSM
        start = 1'b1;

        @(posedge clk);
        #1;

        start = 1'b0;

        // RUN state should be active
        if (busy !== 1'b1) begin
            $display(
                "TEST_FAIL: busy expected 1 in RUN"
            );
            $finish;
        end

        if (result !== 16'd150) begin
            $display(
                "TEST_FAIL: result expected 150 got %0d",
                result
            );
            $finish;
        end

        // Advance to DONE
        @(posedge clk);
        #1;

        if (done !== 1'b1) begin
            $display(
                "TEST_FAIL: done expected 1"
            );
            $finish;
        end

        // Advance back to IDLE
        @(posedge clk);
        #1;

        if (busy !== 1'b0) begin
            $display(
                "TEST_FAIL: busy expected 0 in IDLE"
            );
            $finish;
        end

        $display(
            "TEST_PASS: unseen_fsm_02 functional verification passed"
        );

        $finish;

    end

endmodule