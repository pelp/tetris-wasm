# tetris
A simple tetris game made with WASM and C.

All the game logic is written in C and compiled to WASM using emscripten.

To build the game simply run:
```bash
  make
```
The files you need to host are located under `output/www`.

A version of the game is hosted on https://tetris.toastyfiles.com

To make the leaderboard work you can start the database by running:
```bash
  make start
```

When running over https wss://<domain>/ws needs to point to the server running the leaderboard on port 8763. When running over http the game will try to connect to ws://<domain>:8763
