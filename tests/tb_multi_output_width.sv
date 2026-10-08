`timescale 1ns/1ps

module tb_multi_output_width;

    logic [15:0] a;
    logic [15:0] b;

    logic [11:0] c;
    logic [11:0] d;

    logic [15:0] result_ab;
    logic [11:0] result_cd;

    multi_output_width dut (
        .a(a),
        .b(b),
        .c(c),
        .d(d),
        .result_ab(result_ab),
        .result_cd(result_cd)
    );

    initial begin

        a = 16'd1000;
        b = 16'd500;

        c = 12'd100;
        d = 12'd50;

        #1;

        if (result_ab !== 16'd1500) begin
            $display(
                "TEST_FAIL: result_ab expected 1500 got %0d",
                result_ab
            );
            $finish;
        end

        if (result_cd !== 12'd150) begin
            $display(
                "TEST_FAIL: result_cd expected 150 got %0d",
                result_cd
            );
            $finish;
        end

        a = 16'd20000;
        b = 16'd10000;

        c = 12'd2000;
        d = 12'd1000;

        #1;

        if (result_ab !== 16'd30000) begin
            $display(
                "TEST_FAIL: result_ab expected 30000 got %0d",
                result_ab
            );
            $finish;
        end

        if (result_cd !== 12'd3000) begin
            $display(
                "TEST_FAIL: result_cd expected 3000 got %0d",
                result_cd
            );
            $finish;
        end

        $display(
            "TEST_PASS: multi_output_width functional verification passed"
        );

        $finish;

    end

endmodule