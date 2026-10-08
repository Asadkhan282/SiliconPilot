`timescale 1ns/1ps

module tb_unseen_nested_05;

    logic        clk;
    logic        reset;
    logic        enable;
    logic [1:0]  mode;
    logic [15:0] data_a;
    logic [15:0] data_b;
    logic [11:0] data_c;

    logic [15:0] result_main;
    logic [11:0] result_aux;
    logic        valid;


    unseen_nested_05 dut (
        .clk(clk),
        .reset(reset),
        .enable(enable),
        .mode(mode),
        .data_a(data_a),
        .data_b(data_b),
        .data_c(data_c),
        .result_main(result_main),
        .result_aux(result_aux),
        .valid(valid)
    );


    initial begin
        clk = 1'b0;
        forever #5 clk = ~clk;
    end


    initial begin

        reset      = 1'b1;
        enable     = 1'b0;
        mode       = 2'b00;

        data_a     = 16'd0;
        data_b     = 16'd0;
        data_c     = 12'd0;


        // -------------------------------------------------
        // RESET
        // -------------------------------------------------

        @(posedge clk);
        #1;

        reset = 1'b0;


        // -------------------------------------------------
        // MODE 00 + ENABLE
        // ADD path
        // -------------------------------------------------

        mode   = 2'b00;
        enable = 1'b1;

        data_a = 16'd500;
        data_b = 16'd250;

        #1;

        if (result_main !== 16'd750) begin
            $display(
                "TEST_FAIL: result_main expected 750 got %0d",
                result_main
            );
            $finish;
        end

        if (valid !== 1'b1) begin
            $display(
                "TEST_FAIL: valid expected 1 in mode 00"
            );
            $finish;
        end


        // -------------------------------------------------
        // MODE 01
        // AUX path
        // -------------------------------------------------

        mode   = 2'b01;
        enable = 1'b0;
        data_c = 12'hABC;

        #1;

        if (result_aux !== 12'hABC) begin
            $display(
                "TEST_FAIL: result_aux expected 0xABC got 0x%03h",
                result_aux
            );
            $finish;
        end

        if (valid !== 1'b1) begin
            $display(
                "TEST_FAIL: valid expected 1 in mode 01"
            );
            $finish;
        end


        // -------------------------------------------------
        // MODE 10
        // AND path + AUX path
        // -------------------------------------------------

        mode   = 2'b10;
        enable = 1'b1;

        data_a = 16'h00FF;
        data_b = 16'h0F0F;
        data_c = 12'h321;

        #1;

        if (result_main !== 16'h000F) begin
            $display(
                "TEST_FAIL: AND expected 0x000F got 0x%04h",
                result_main
            );
            $finish;
        end

        if (result_aux !== 12'h321) begin
            $display(
                "TEST_FAIL: AUX expected 0x321 got 0x%03h",
                result_aux
            );
            $finish;
        end

        if (valid !== 1'b1) begin
            $display(
                "TEST_FAIL: valid expected 1 in mode 10"
            );
            $finish;
        end


        // -------------------------------------------------
        // MODE 00 DISABLED
        // Should fall back to safe defaults
        // -------------------------------------------------

        mode   = 2'b00;
        enable = 1'b0;

        #1;

        if (valid !== 1'b0) begin
            $display(
                "TEST_FAIL: valid expected 0 when disabled"
            );
            $finish;
        end


        // -------------------------------------------------
        // DEFAULT MODE
        // -------------------------------------------------

        mode = 2'b11;

        #1;

        if (valid !== 1'b0) begin
            $display(
                "TEST_FAIL: valid expected 0 in default mode"
            );
            $finish;
        end


        $display(
            "TEST_PASS: unseen_nested_05 functional verification passed"
        );

        $finish;

    end

endmodule