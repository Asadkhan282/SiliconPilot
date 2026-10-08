`timescale 1ns/1ps

module tb_unseen_fifo_03;

    logic        clk;
    logic        reset;
    logic        push;
    logic        pop;
    logic [15:0] data_in;

    logic [15:0] data_out;
    logic        full;
    logic        empty;


    unseen_fifo_03 dut (
        .clk(clk),
        .reset(reset),
        .push(push),
        .pop(pop),
        .data_in(data_in),
        .data_out(data_out),
        .full(full),
        .empty(empty)
    );


    // =====================================================
    // CLOCK
    // =====================================================

    initial begin
        clk = 1'b0;
        forever #5 clk = ~clk;
    end


    // =====================================================
    // TEST
    // =====================================================

    initial begin

        reset   = 1'b1;
        push    = 1'b0;
        pop     = 1'b0;
        data_in = 16'd0;


        // -------------------------------------------------
        // RESET
        // -------------------------------------------------

        @(posedge clk);
        #1;

        reset = 1'b0;

        #1;

        if (empty !== 1'b1) begin
            $display(
                "TEST_FAIL: FIFO should be empty after reset"
            );
            $finish;
        end

        if (full !== 1'b0) begin
            $display(
                "TEST_FAIL: FIFO should not be full after reset"
            );
            $finish;
        end


        // -------------------------------------------------
        // PUSH FIRST VALUE
        // -------------------------------------------------

        data_in = 16'h1234;
        push = 1'b1;

        @(posedge clk);
        #1;

        push = 1'b0;

        if (empty !== 1'b0) begin
            $display(
                "TEST_FAIL: FIFO should not be empty after first push"
            );
            $finish;
        end


        // -------------------------------------------------
        // PUSH SECOND VALUE
        // -------------------------------------------------

        data_in = 16'hABCD;
        push = 1'b1;

        @(posedge clk);
        #1;

        push = 1'b0;


        // -------------------------------------------------
        // CHECK FIRST FIFO VALUE BEFORE POP
        // -------------------------------------------------

        #1;

        if (data_out !== 16'h1234) begin
            $display(
                "TEST_FAIL: first FIFO value expected 0x1234 got 0x%04h",
                data_out
            );
            $finish;
        end


        // -------------------------------------------------
        // POP FIRST VALUE
        // -------------------------------------------------

        pop = 1'b1;

        @(posedge clk);
        #1;

        pop = 1'b0;


        // -------------------------------------------------
        // CHECK SECOND FIFO VALUE
        // -------------------------------------------------

        #1;

        if (data_out !== 16'hABCD) begin
            $display(
                "TEST_FAIL: second FIFO value expected 0xABCD got 0x%04h",
                data_out
            );
            $finish;
        end


        // -------------------------------------------------
        // POP SECOND VALUE
        // -------------------------------------------------

        pop = 1'b1;

        @(posedge clk);
        #1;

        pop = 1'b0;


        // -------------------------------------------------
        // FIFO MUST NOW BE EMPTY
        // -------------------------------------------------

        #1;

        if (empty !== 1'b1) begin
            $display(
                "TEST_FAIL: FIFO should be empty after two pops"
            );
            $finish;
        end

        if (full !== 1'b0) begin
            $display(
                "TEST_FAIL: FIFO should not be full"
            );
            $finish;
        end


        // -------------------------------------------------
        // PUSH THIRD VALUE AFTER EMPTY
        // -------------------------------------------------

        data_in = 16'h55AA;
        push = 1'b1;

        @(posedge clk);
        #1;

        push = 1'b0;

        #1;

        if (empty !== 1'b0) begin
            $display(
                "TEST_FAIL: FIFO should contain third value"
            );
            $finish;
        end

        if (data_out !== 16'h55AA) begin
            $display(
                "TEST_FAIL: third FIFO value expected 0x55AA got 0x%04h",
                data_out
            );
            $finish;
        end


        // -------------------------------------------------
        // PASS
        // -------------------------------------------------

        $display(
            "TEST_PASS: unseen_fifo_03 functional verification passed"
        );

        $finish;

    end

endmodule