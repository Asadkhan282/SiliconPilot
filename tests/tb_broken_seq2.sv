`timescale 1ns/1ps

module tb_broken_seq2;

    logic clk;
    logic reset;
    logic [7:0] data_in;
    logic [7:0] data_out;
    logic [7:0] counter;

    broken_seq2 dut (
        .clk(clk),
        .reset(reset),
        .data_in(data_in),
        .data_out(data_out),
        .counter(counter)
    );

    initial begin
        clk = 0;
        forever #5 clk = ~clk;
    end

    initial begin
        reset = 1;
        data_in = 8'h00;

        @(posedge clk);
        #1;

        if (data_out !== 8'h00 || counter !== 8'h00) begin
            $display("TEST_FAIL: reset behavior incorrect");
            $finish;
        end

        reset = 0;
        data_in = 8'h25;

        @(posedge clk);
        #1;

        if (data_out !== 8'h25) begin
            $display(
                "TEST_FAIL: expected data_out 25 got %0h",
                data_out
            );
            $finish;
        end

        if (counter !== 8'd1) begin
            $display(
                "TEST_FAIL: expected counter 1 got %0d",
                counter
            );
            $finish;
        end

        data_in = 8'hA5;

        @(posedge clk);
        #1;

        if (data_out !== 8'hA5) begin
            $display(
                "TEST_FAIL: expected data_out A5 got %0h",
                data_out
            );
            $finish;
        end

        if (counter !== 8'd2) begin
            $display(
                "TEST_FAIL: expected counter 2 got %0d",
                counter
            );
            $finish;
        end

        $display(
            "TEST_PASS: broken_seq2 functional verification passed"
        );

        $finish;
    end

endmodule