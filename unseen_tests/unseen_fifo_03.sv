module unseen_fifo_03 (
    input  logic        clk,
    input  logic        reset,
    input  logic        push,
    input  logic        pop,
    input  logic [15:0] data_in,

    output logic [7:0]  data_out,
    output logic        full,
    output logic        empty
);

logic [15:0] mem [0:3];

logic [1:0] wr_ptr;
logic [1:0] rd_ptr;
logic [2:0] count;

always_comb begin
    full = 1'b0;
    empty = 1'b0;

    if (count == 3'd4)
        full = 1'b1;

    if (count == 3'd0)
        empty = 1'b1;

    data_out = mem[rd_ptr];
end


always_ff @(posedge clk) begin

    if (reset) begin
        wr_ptr <= 2'd0;
        rd_ptr <= 2'd0;
        count <= 3'd0;
    end
    else begin

        if (push && !full) begin
            mem[wr_ptr] <= data_in;
            wr_ptr = wr_ptr + 1'b1;
            count = count + 1'b1;
        end

        if (pop && !empty) begin
            rd_ptr = rd_ptr + 1'b1;
            count = count - 1'b1;
        end

    end

end

endmodule