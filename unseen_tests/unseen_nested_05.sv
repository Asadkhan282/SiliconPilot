module unseen_nested_05 (
    input  logic        clk,
    input  logic        reset,
    input  logic        enable,
    input  logic [1:0]  mode,
    input  logic [15:0] data_a,
    input  logic [15:0] data_b,
    input  logic [11:0] data_c,

    output logic [7:0]  result_main,
    output logic [3:0]  result_aux,
    output logic        valid
);

logic [7:0] shadow_reg;

always_comb begin

    valid = 1'b0;

    case (mode)

        2'b00: begin
            if (enable) begin
                result_main = data_a + data_b;
                valid = 1'b1;
            end
        end

        2'b01: begin
            result_aux = data_c;
            valid = 1'b1;
        end

        2'b10: begin
            if (enable) begin
                result_main = data_a & data_b;
                result_aux = data_c;
                valid = 1'b1;
            end
        end

        default: begin
            valid = 1'b0;
        end

    endcase
end


always_ff @(posedge clk) begin
    if (reset) begin
        shadow_reg <= 8'd0;
    end
    else begin
        shadow_reg = result_main;
    end
end

endmodule