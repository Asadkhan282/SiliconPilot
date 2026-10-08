`timescale 1ns/1ps

module tb_unseen_latch_fsm_06;

    logic        clk;
    logic        reset;
    logic        start;
    logic        enable;
    logic [1:0]  mode;
    logic [15:0] data_a;
    logic [15:0] data_b;

    logic [15:0] result;
    logic        valid;
    logic        busy;


    unseen_latch_fsm_06 dut (
        .clk(clk),
        .reset(reset),
        .start(start),
        .enable(enable),
        .mode(mode),
        .data_a(data_a),
        .data_b(data_b),
        .result(result),
        .valid(valid),
        .busy(busy)
    );


    // -----------------------------------------------------
    // Clock
    // -----------------------------------------------------

    initial begin
        clk = 1'b0;

        forever #5 clk = ~clk;
    end


    // -----------------------------------------------------
    // Test sequence
    // -----------------------------------------------------

    initial begin

        reset = 1'b1;
        start = 1'b0;
        enable = 1'b0;
        mode = 2'b00;

        data_a = 16'd100;
        data_b = 16'd50;


        // -------------------------------------------------
        // RESET
        // -------------------------------------------------

        @(posedge clk);
        #1;

        reset = 1'b0;

        if (busy !== 1'b0) begin
            $display(
                "TEST_FAIL: busy should be 0 after reset"
            );
            $finish;
        end


        // -------------------------------------------------
        // IDLE
        // -------------------------------------------------

        #1;

        if (busy !== 1'b0) begin
            $display(
                "TEST_FAIL: IDLE busy expected 0"
            );
            $finish;
        end


        // -------------------------------------------------
        // Start transaction
        // IDLE -> RUN
        // -------------------------------------------------

        start = 1'b1;

        @(posedge clk);
        #1;

        start = 1'b0;


        // -------------------------------------------------
        // RUN
        // MODE 00 + ENABLE
        // result = data_a + data_b
        // -------------------------------------------------

        mode = 2'b00;
        enable = 1'b1;

        data_a = 16'd1000;
        data_b = 16'd500;

        #1;

        if (busy !== 1'b1) begin
            $display(
                "TEST_FAIL: RUN busy expected 1"
            );
            $finish;
        end

        if (result !== 16'd1500) begin
            $display(
                "TEST_FAIL: ADD result expected 1500 got %0d",
                result
            );
            $finish;
        end

        if (valid !== 1'b1) begin
            $display(
                "TEST_FAIL: ADD valid expected 1"
            );
            $finish;
        end


        // -------------------------------------------------
        // Advance RUN -> DONE
        // -------------------------------------------------

        @(posedge clk);
        #1;

        if (busy !== 1'b0) begin
            $display(
                "TEST_FAIL: DONE busy expected 0"
            );
            $finish;
        end

        if (valid !== 1'b1) begin
            $display(
                "TEST_FAIL: DONE valid expected 1"
            );
            $finish;
        end


        // -------------------------------------------------
        // Advance DONE -> IDLE
        // -------------------------------------------------

        @(posedge clk);
        #1;

        if (busy !== 1'b0) begin
            $display(
                "TEST_FAIL: returned IDLE busy expected 0"
            );
            $finish;
        end


        // -------------------------------------------------
        // Start second transaction
        // -------------------------------------------------

        start = 1'b1;

        @(posedge clk);
        #1;

        start = 1'b0;


        // -------------------------------------------------
        // MODE 01
        // result = data_a & data_b
        // -------------------------------------------------

        mode = 2'b01;
        enable = 1'b0;

        data_a = 16'h00FF;
        data_b = 16'h0F0F;

        #1;

        if (busy !== 1'b1) begin
            $display(
                "TEST_FAIL: MODE01 busy expected 1"
            );
            $finish;
        end

        if (result !== 16'h000F) begin
            $display(
                "TEST_FAIL: AND expected 0x000F got 0x%04h",
                result
            );
            $finish;
        end

        if (valid !== 1'b1) begin
            $display(
                "TEST_FAIL: MODE01 valid expected 1"
            );
            $finish;
        end


        // -------------------------------------------------
        // Advance to DONE and then IDLE
        // -------------------------------------------------

        @(posedge clk);
        #1;

        @(posedge clk);
        #1;


        // -------------------------------------------------
        // Third transaction:
        // MODE 00 but ENABLE = 0
        //
        // We expect no valid result.
        // This test is important because it may expose
        // incomplete combinational assignment behavior.
        // -------------------------------------------------

        start = 1'b1;

        @(posedge clk);
        #1;

        start = 1'b0;

        mode = 2'b00;
        enable = 1'b0;

        #1;

        if (busy !== 1'b1) begin
            $display(
                "TEST_FAIL: disabled RUN busy expected 1"
            );
            $finish;
        end

        if (valid !== 1'b0) begin
            $display(
                "TEST_FAIL: disabled RUN valid expected 0"
            );
            $finish;
        end


        // -------------------------------------------------
        // PASS
        // -------------------------------------------------

        $display(
            "TEST_PASS: unseen_latch_fsm_06 functional verification passed"
        );

        $finish;

    end

endmodule