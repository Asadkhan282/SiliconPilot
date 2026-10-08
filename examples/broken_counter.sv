module broken_counter (
    input  logic clk,
    input  logic reset,
    output logic [3:0] count
);

always_ff @(posedge clk) begin
    if (reset)
        count <= 4'd0;
    else
        count = count + 1;
end

endmodule