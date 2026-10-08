`timescale 1ns/1ps

module tb_unseen_controller_01;

    logic        clk;
    logic        reset;
    logic        enable;
    logic [15:0] data_a;
    logic [15:0] data_b;
    logic [1:0]  opcode;

    logic [15:0] result;
    logic        valid;


    unseen_controller_01 dut (
        .clk(clk),
        .reset(reset),
        .enable(enable),
        .data_a(data_a),
        .data_b(data_b),
        .opcode(opcode),
        .result(result),
        .valid(valid)
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
        enable = 1'b0;
        data_a = 16'd0;
        data_b = 16'd0;
        opcode = 2'b00;


        // -------------------------------------------------
        // RESET
        // -------------------------------------------------

        @(posedge clk);
        #1;

        reset = 1'b0;


        // -------------------------------------------------
        // ADD
        // opcode = 00
        // enable = 1
        // -------------------------------------------------

        enable = 1'b1;
        opcode = 2'b00;

        data_a = 16'd1000;
        data_b = 16'd500;

        #1;

        if (result !== 16'd1500) begin
            $display(
                "TEST_FAIL: ADD expected 1500 got %0d",
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
        // ADD DISABLED
        // Should produce safe default
        // -------------------------------------------------

        enable = 1'b0;

        #1;

        if (valid !== 1'b0) begin
            $display(
                "TEST_FAIL: disabled ADD valid expected 0"
            );
            $finish;
        end

        if (result !== 16'd0) begin
            $display(
                "TEST_FAIL: disabled ADD result expected 0 got %0d",
                result
            );
            $finish;
        end


        // -------------------------------------------------
        // SUBTRACT
        // opcode = 01
        // -------------------------------------------------

        enable = 1'b1;
        opcode = 2'b01;

        data_a = 16'd900;
        data_b = 16'd250;

        #1;

        if (result !== 16'd650) begin
            $display(
                "TEST_FAIL: SUB expected 650 got %0d",
                result
            );
            $finish;
        end

        if (valid !== 1'b1) begin
            $display(
                "TEST_FAIL: SUB valid expected 1"
            );
            $finish;
        end


        // -------------------------------------------------
        // SUBTRACT DISABLED
        // -------------------------------------------------

        enable = 1'b0;

        #1;

        if (valid !== 1'b0) begin
            $display(
                "TEST_FAIL: disabled SUB valid expected 0"
            );
            $finish;
        end

        if (result !== 16'd0) begin
            $display(
                "TEST_FAIL: disabled SUB result expected 0 got %0d",
                result
            );
            $finish;
        end


        // -------------------------------------------------
        // BITWISE AND
        // opcode = 10
        //
        // This operation does not depend on enable
        // in the original RTL.
        // -------------------------------------------------

        opcode = 2'b10;
        enable = 1'b0;

        data_a = 16'h00FF;
        data_b = 16'h0F0F;

        #1;

        if (result !== 16'h000F) begin
            $display(
                "TEST_FAIL: AND expected 0x000F got 0x%04h",
                result
            );
            $finish;
        end

        if (valid !== 1'b1) begin
            $display(
                "TEST_FAIL: AND valid expected 1"
            );
            $finish;
        end


        // -------------------------------------------------
        // DEFAULT OPCODE
        // opcode = 11
        // -------------------------------------------------

        opcode = 2'b11;

        #1;

        if (valid !== 1'b0) begin
            $display(
                "TEST_FAIL: default opcode valid expected 0"
            );
            $finish;
        end

        if (result !== 16'd0) begin
            $display(
                "TEST_FAIL: default opcode result expected 0 got %0d",
                result
            );
            $finish;
        end


        // -------------------------------------------------
        // LARGE ADD
        // Confirm repaired 16-bit output
        // -------------------------------------------------

        opcode = 2'b00;
        enable = 1'b1;

        data_a = 16'd20000;
        data_b = 16'd10000;

        #1;

        if (result !== 16'd30000) begin
            $display(
                "TEST_FAIL: large ADD expected 30000 got %0d",
                result
            );
            $finish;
        end


        // -------------------------------------------------
        // PASS
        // -------------------------------------------------

        $display(
            "TEST_PASS: unseen_controller_01 functional verification passed"
        );

        $finish;

    end

endmodule