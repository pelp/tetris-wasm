#include <libtetris.h>
#include <stdio.h>
#include <time.h>
#include <emscripten/emscripten.h>

EMSCRIPTEN_KEEPALIVE tetris_t game;
EMSCRIPTEN_KEEPALIVE char *interface = NULL;
EMSCRIPTEN_KEEPALIVE time_us_t g_fall_interval = 0;

EMSCRIPTEN_KEEPALIVE void js_init(
        int width,
        int height,
        int fall_interval,
        int delayed_auto_shift,
        int automatic_repeat_rate
) {
    g_fall_interval = fall_interval;
    init(&game, width, height, fall_interval, delayed_auto_shift, automatic_repeat_rate);
}

EMSCRIPTEN_KEEPALIVE void js_restart() {
    game.seed = 0;
    init(&game, game.width, game.height, g_fall_interval, game.delayed_auto_shift, game.automatic_repeat_rate);
}

EMSCRIPTEN_KEEPALIVE int js_lines() {
    return get_lines(&game);
}

EMSCRIPTEN_KEEPALIVE char *js_get() {
    // Allocate interface buffer
    if (interface == NULL) {
        interface = malloc(sizeof(char) * game.framebuffer.width * game.framebuffer.height);
    }

    // Filter the data
    for (int i = 0; i < game.framebuffer.height; i++) {
        for (int j = 0; j < game.framebuffer.width; j++) {
            char state = read_game(&game, j, i);
            interface[i * game.framebuffer.width + j] = state;
        }
    }
    return interface;
}

EMSCRIPTEN_KEEPALIVE int js_next_width(int index) {
    if (index >= 0 && index < NUM_NEXT_PIECES) {
        return get_piece_width(game.bag.next[index]);
    }
    return 0;
}

EMSCRIPTEN_KEEPALIVE int js_next_height(int index) {
    if (index >= 0 && index < NUM_NEXT_PIECES) {
        return get_piece_height(game.bag.next[index]);
    }
    return 0;
}

EMSCRIPTEN_KEEPALIVE const piece_id_t* js_next_blocks(int index) {
    if (index >= 0 && index < NUM_NEXT_PIECES) {
        return get_piece_blocks(game.bag.next[index]);
    }
    return NULL;
}

EMSCRIPTEN_KEEPALIVE int js_hold_width() {
    return game.hold != PIECE_EMPTY ? get_piece_width(game.hold) : 0;
}

EMSCRIPTEN_KEEPALIVE int js_hold_height() {
    return game.hold != PIECE_EMPTY ? get_piece_height(game.hold) : 0;
}

EMSCRIPTEN_KEEPALIVE const piece_id_t* js_hold_blocks() {
    return game.hold != PIECE_EMPTY ? get_piece_blocks(game.hold) : NULL;
}

EMSCRIPTEN_KEEPALIVE void js_set_fall_interval(int fall_interval) {
    game.fall_interval = fall_interval;
}

EMSCRIPTEN_KEEPALIVE int js_tick(
        bool space,
        bool down,
        bool left,
        bool right,
        bool rotate_cw,
        bool rotate_ccw,
        bool hold,
        int delta_time
) {
    return tick(&game, (tetris_params_t) {
            .inputs = (tetris_inputs_t) {
                    .space = space,
                    .down = down,
                    .left = left,
                    .right = right,
                    .rotate_ccw = rotate_ccw,
                    .rotate_cw = rotate_cw,
                    .hold = hold
            },
            .delta_time = delta_time
    });
}

EMSCRIPTEN_KEEPALIVE uint64_t js_get_seed() {
    return game.seed;
}

EMSCRIPTEN_KEEPALIVE uint64_t js_get_num_transactions() {
    return read_transactions(&game).used_size;
}

EMSCRIPTEN_KEEPALIVE uint64_t js_get_transaction_size() {
    return sizeof(tetris_transaction_t);
}

EMSCRIPTEN_KEEPALIVE tetris_transaction_t* js_get_transactions() {
    return read_transactions(&game).transactions;
}