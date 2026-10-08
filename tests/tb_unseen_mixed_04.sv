`timescale 1ns/1ps

module tb_unseen_mixed_04;

    logic        clk;
    logic        reset;
    logic        start;
    logic        enable;
    logic [15:0] data_a;
    logic [15:0] data_b;

    logic [15:0] result;
    logic        busy;
    logic        done;


    unseen_mixed_04 dut (
        .clk(clk),
        .reset(reset),
        .start(start),
        .enable(enable),
        .data_a(data_a),
        .data_b(data_b),
        .result(result),
        .busy(busy),
        .done(done)
    );


    // =====================================================
    // CLOCK
    // =====================================================

    initial begin
        clk = 1'b0;
        forever #5 clk = ~clk;
    end


    // =====================================================
    // TEST SEQUENCE
    // =====================================================

    initial begin

        reset  = 1'b1;
        start  = 1'b0;
        enable = 1'b0;

        data_a = 16'd0;
        data_b = 16'd0;


        // -------------------------------------------------
        // RESET
        // -------------------------------------------------

        @(posedge clk);
        #1;

        reset = 1'b0;

        #1;

        if (busy !== 1'b0) begin
            $display(
                "TEST_FAIL: busy should be 0 after reset"
            );
            $finish;
        end

        if (done !== 1'b0) begin
            $display(
                "TEST_FAIL: done should be 0 after reset"
            );
            $finish;
        end


        // -------------------------------------------------
        // IDLE -> RUN
        // -------------------------------------------------

        start = 1'b1;

        @(posedge clk);
        #1;

        start = 1'b0;


        // -------------------------------------------------
        // RUN WITH ENABLE
        // -------------------------------------------------

        enable = 1'b1;

        data_a = 16'd700;
        data_b = 16'd300;

        #1;

        if (busy !== 1'b1) begin
            $display(
                "TEST_FAIL: busy expected 1 in RUN"
            );
            $finish;
        end

        if (result !== 16'd1000) begin
            $display(
                "TEST_FAIL: result expected 1000 got %0d",
                result
            );
            $finish;
        end


        // -------------------------------------------------
        // RUN -> FINISH
        // -------------------------------------------------

        @(posedge clk);
        #1;

        enable = 1'b0;

        if (busy !== 1'b0) begin
            $display(
                "TEST_FAIL: busy expected 0 in FINISH"
            );
            $finish;
        end

        if (done !== 1'b1) begin
            $display(
                "TEST_FAIL: done expected 1 in FINISH"
            );
            $finish;
        end


        // -------------------------------------------------
        // FINISH -> IDLE
        // -------------------------------------------------

        @(posedge clk);
        #1;

        if (done !== 1'b0) begin
            $display(
                "TEST_FAIL: done expected 0 after return to IDLE"
            );
            $finish;
        end

        if (busy !== 1'b0) begin
            $display(
                "TEST_FAIL: busy expected 0 after return to IDLE"
            );
            $finish;
        end


        // -------------------------------------------------
        // SECOND TRANSACTION
        // Different data
        // -------------------------------------------------

        data_a = 16'd1234;
        data_b = 16'd4321;

        start = 1'b1;

        @(posedge clk);
        #1;

        start = 1'b0;

        enable = 1'b1;

        #1;

        if (busy !== 1'b1) begin
            $display(
                "TEST_FAIL: second transaction busy expected 1"
            );
            $finish;
        end

        if (result !== 16'd5555) begin
            $display(
                "TEST_FAIL: second result expected 5555 got %0d",
                result
            );
            $finish;
        end


        // -------------------------------------------------
        // PASS
        // -------------------------------------------------

        $display(
            "TEST_PASS: unseen_mixed_04 functional verification passed"
        );

        $finish;

    end

endmodule