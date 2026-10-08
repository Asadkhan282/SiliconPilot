module unseen_mixed_04 (
    input  logic        clk,
    input  logic        reset,
    input  logic        start,
    input  logic        enable,
    input  logic [15:0] data_a,
    input  logic [15:0] data_b,

    output logic [7:0]  result,
    output logic        busy,
    output logic        done
);

typedef enum logic [1:0] {
    IDLE,
    RUN,
    FINISH
} state_t;

state_t state;
state_t next_state;

logic [7:0] temp_reg;

always_comb begin

    busy = 1'b0;
    done = 1'b0;

    case (state)

        IDLE: begin
            if (start)
                next_state = RUN;
            else
                next_state = IDLE;
        end

        RUN: begin
            busy = 1'b1;

            if (enable)
                result = data_a + data_b;

            next_state = FINISH;
        end

        FINISH: begin
            done = 1'b1;
            next_state = IDLE;
        end

        default: begin
            next_state = IDLE;
        end

    endcase
end


always_ff @(posedge clk) begin
    if (reset) begin
        state <= IDLE;
        temp_reg <= 8'd0;
    end
    else begin
        state = next_state;
        temp_reg = result;
    end
end

endmodule