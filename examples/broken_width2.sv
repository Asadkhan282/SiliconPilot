module broken_width2 (
    input  logic [15:0] a,
    input  logic [15:0] b,
    output logic [7:0]  result
);

always_comb begin
    result = a + b;
end

endmodule