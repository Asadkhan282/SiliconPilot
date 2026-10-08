`timescale 1ns/1ps

module tb_final_multi_fault;

    logic clk;
    logic reset;
    logic enable;
    logic mode;

    logic [15:0] a;
    logic [15:0] b;

    logic [15:0] comb_result;
    logic [15:0] registered_result;
    logic valid;

    final_multi_fault dut (
        .clk(clk),
        .reset(reset),
        .enable(enable),
        .mode(mode),
        .a(a),
        .b(b),
        .comb_result(comb_result),
        .registered_result(registered_result),
        .valid(valid)
    );

    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end

    initial begin
        reset = 1;
        enable = 0;
        mode = 0;

        a = 16'd1000;
        b = 16'd500;

        @(posedge clk);
        #1;

        if (registered_result !== 16'd0) begin
            $display(
                "TEST_FAIL: reset registered_result expected 0"
            );
            $finish;
        end

        reset = 0;

        mode = 0;
        enable = 0;

        #1;

        if (comb_result !== 16'd0) begin
            $display(
                "TEST_FAIL: mode=0 comb_result expected 0"
            );
            $finish;
        end

        if (valid !== 1'b0) begin
            $display(
                "TEST_FAIL: mode=0 valid expected 0"
            );
            $finish;
        end

        mode = 1;
        enable = 1;

        a = 16'd1000;
        b = 16'd500;

        #1;

        if (comb_result !== 16'd1500) begin
            $display(
                "TEST_FAIL: comb_result expected 1500 got %0d",
                comb_result
            );
            $finish;
        end

        if (valid !== 1'b1) begin
            $display(
                "TEST_FAIL: valid expected 1"
            );
            $finish;
        end

        @(posedge clk);
        #1;

        if (registered_result !== 16'd1500) begin
            $display(
                "TEST_FAIL: registered_result expected 1500 got %0d",
                registered_result
            );
            $finish;
        end

        a = 16'd20000;
        b = 16'd10000;

        #1;

        if (comb_result !== 16'd30000) begin
            $display(
                "TEST_FAIL: comb_result expected 30000 got %0d",
                comb_result
            );
            $finish;
        end

        @(posedge clk);
        #1;

        if (registered_result !== 16'd30000) begin
            $display(
                "TEST_FAIL: registered_result expected 30000 got %0d",
                registered_result
            );
            $finish;
        end

        enable = 0;

        #1;

        if (comb_result !== 16'd0) begin
            $display(
                "TEST_FAIL: disabled comb_result expected 0"
            );
            $finish;
        end

        if (valid !== 1'b0) begin
            $display(
                "TEST_FAIL: disabled valid expected 0"
            );
            $finish;
        end

        $display(
            "TEST_PASS: final_multi_fault functional verification passed"
        );

        $finish;
    end

endmodule