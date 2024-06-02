#!/bin/env python3
import sqlite3
import datetime
import asyncio
import json
from websockets.server import serve
import base64
import libtetris

DBNAME = "leaderboard"

con = sqlite3.connect("leaderboard.db")
cur = con.cursor()

connections = []

res = cur.execute("SELECT name FROM sqlite_master")
try:
    res = cur.execute(f"CREATE TABLE {DBNAME}(name, time, difficulty, date)")
    print("Created leaderboard")
except sqlite3.OperationalError:
    print("Loading leaderboard")


def post_score(name, time):
    cur.execute(
        f"INSERT INTO {DBNAME} VALUES ('{name}', {time}, 'default', '{datetime.datetime.now()}')")
    con.commit()


def get_scores(difficulty):
    return cur.execute(
        """
        SELECT
            name, MAX(CAST(time AS INTEGER))
        FROM
            {DBNAME}
        WHERE
            difficulty = '{difficulty}'
        GROUP BY
            name
        ORDER BY
            CAST(time AS INTEGER) DESC
        """.format(DBNAME=DBNAME, difficulty=difficulty)
    ).fetchmany(20)


async def broadcast():
    scores = get_scores("default")
    for c in connections:
        try:
            await c.send(json.dumps(scores))
        except:
            connections.remove(c)


def decode_transactions(transactions, length):
    sz = len(transactions) // length
    mv = memoryview(transactions).cast('B', shape=[length, sz])
    lst = mv.tolist()
    transactions = [libtetris.Transaction(params=libtetris.Params(
        inputs=libtetris.Inputs(
            rotate_cw=t[0],
            rotate_ccw=t[1],
            hold=t[2],
            down=t[3],
            left=t[4],
            right=t[5],
            space=t[6]
        ),
        delta_time=memoryview(bytearray(t[8:16])).cast('i').tolist()[0]
    )) for t in lst]

    return (libtetris.Transaction * length)(*transactions)


async def handle(websocket):
    connections.append(websocket)
    async for message in websocket:
        info = json.loads(message)
        if not isinstance(info, dict):
            continue
        if info["type"] == "submit":
            transactions = info.get('transactions')
            if transactions is None:
                continue
            game = libtetris.Tetris(seed=info["seed"])
            decoded = base64.b64decode(transactions["b64"])
            length = transactions["length"]
            game.run_transactions(decode_transactions(decoded, length), length)
            game.print()
            print(f"score: {game.score}")
            post_score(info["name"], game.score)
            await broadcast()
        elif info["type"] == "get":
            await websocket.send(json.dumps(get_scores("default")))
    connections.remove(websocket)


async def main():
    async with serve(handle, "localhost", 8763):
        await asyncio.Future()


asyncio.run(main())

con.close()
