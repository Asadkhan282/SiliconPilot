module broken_latch (
    input  logic       enable,
    input  logic [7:0] data_in,
    output logic [7:0] data_out
);

always_comb begin
    if (enable)
        data_out = data_in;
end

endmodule