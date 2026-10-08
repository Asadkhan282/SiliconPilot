module mixed_fsm_datapath (
    input  logic        clk,
    input  logic        reset,
    input  logic        start,
    input  logic        done,
    input  logic [15:0] a,
    input  logic [15:0] b,
    output logic [7:0]  result,
    output logic        busy
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
    next_state = state;
    busy = 1'b0;
    result = 8'd0;

    case (state)

        IDLE: begin
            if (start)
                next_state = RUN;
        end

        RUN: begin
            busy = 1'b1;
            result = a + b;

            if (done)
                next_state = DONE;
        end

        DONE: begin
            next_state = IDLE;
        end

        default: begin
            next_state = IDLE;
        end

    endcase
end

endmodule