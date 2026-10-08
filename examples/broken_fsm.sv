module broken_fsm (
    input  logic clk,
    input  logic reset,
    input  logic start,
    input  logic done,
    output logic busy,
    output logic complete
);

typedef enum logic [1:0] {
    IDLE = 2'b00,
    RUN  = 2'b01,
    DONE = 2'b10
} state_t;

state_t state;
state_t next_state;

always_ff @(posedge clk) begin
    if (reset)
        state <= IDLE;
    else
        state = next_state;
end

always_comb begin

    busy = 1'b0;

    case (state)

        IDLE: begin
            complete = 1'b0;

            if (start)
                next_state = RUN;
        end

        RUN: begin
            busy = 1'b1;
            complete = 1'b0;

            if (done)
                next_state = DONE;
        end

        DONE: begin
            complete = 1'b1;
            next_state = IDLE;
        end

        default: begin
            next_state = IDLE;
            complete = 1'b0;
        end

    endcase

end

endmodule