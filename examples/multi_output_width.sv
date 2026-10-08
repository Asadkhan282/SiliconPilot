module multi_output_width (
    input  logic [15:0] a,
    input  logic [15:0] b,
    input  logic [11:0] c,
    input  logic [11:0] d,

    output logic [7:0] result_ab,
    output logic [3:0] result_cd
);

always_comb begin
    result_ab = a + b;
    result_cd = c + d;
end

endmodule