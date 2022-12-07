import pprint
import json
from fastapi import FastAPI
import chess
from stockfish import Stockfish

# endpoints
# Realizar uma jogada:
# http://somosicev.com/icevchallenge/jogar/{id}/{token}/{src}/{dest}
# Obter tabuleiro:
# http://somosicev.com/icevchallenge/{id}
# Oferecer empate:
# http://somosicev.com/icevchallenge/empate/{id}/{token}
# Aceitar empate:
# http://somosicev.com/icevchallenge/empate/aceitar/{id}/{token}
# Desistir da partida:
# http://somosicev.com/icevchallenge/desistir/{id}/{token}

app = FastAPI()
board = chess.Board()
test = "{\"pieces\":[{\"type\":\"Pawn\",\"row\":1,\"col\":0,\"white\":false},{\"type\":\"Pawn\",\"row\":6,\"col\":0,\"white\":true},{\"type\":\"Pawn\",\"row\":1,\"col\":1,\"white\":false},{\"type\":\"Pawn\",\"row\":6,\"col\":1,\"white\":true},{\"type\":\"Pawn\",\"row\":1,\"col\":2,\"white\":false},{\"type\":\"Pawn\",\"row\":6,\"col\":2,\"white\":true},{\"type\":\"Pawn\",\"row\":1,\"col\":3,\"white\":false},{\"type\":\"Pawn\",\"row\":4,\"col\":3,\"white\":false},{\"type\":\"Pawn\",\"row\":4,\"col\":4,\"white\":true},{\"type\":\"Pawn\",\"row\":1,\"col\":5,\"white\":false},{\"type\":\"Pawn\",\"row\":6,\"col\":5,\"white\":true},{\"type\":\"Pawn\",\"row\":1,\"col\":6,\"white\":false},{\"type\":\"Pawn\",\"row\":6,\"col\":6,\"white\":true},{\"type\":\"Pawn\",\"row\":1,\"col\":7,\"white\":false},{\"type\":\"Pawn\",\"row\":6,\"col\":7,\"white\":true},{\"type\":\"Rook\",\"row\":0,\"col\":0,\"white\":false},{\"type\":\"Rook\",\"row\":0,\"col\":7,\"white\":false},{\"type\":\"Rook\",\"row\":7,\"col\":0,\"white\":true},{\"type\":\"Rook\",\"row\":7,\"col\":7,\"white\":true},{\"type\":\"Knight\",\"row\":0,\"col\":1,\"white\":false},{\"type\":\"Knight\",\"row\":0,\"col\":6,\"white\":false},{\"type\":\"Knight\",\"row\":7,\"col\":1,\"white\":true},{\"type\":\"Knight\",\"row\":7,\"col\":6,\"white\":true},{\"type\":\"Bishop\",\"row\":0,\"col\":2,\"white\":false},{\"type\":\"Bishop\",\"row\":0,\"col\":5,\"white\":false},{\"type\":\"Bishop\",\"row\":7,\"col\":2,\"white\":true},{\"type\":\"Bishop\",\"row\":7,\"col\":5,\"white\":true},{\"type\":\"Queen\",\"row\":0,\"col\":3,\"white\":false},{\"type\":\"Queen\",\"row\":7,\"col\":3,\"white\":true},{\"type\":\"King\",\"row\":0,\"col\":4,\"white\":false},{\"type\":\"King\",\"row\":7,\"col\":4,\"white\":true}],\"player1\":{\"side\":0,\"codigo\":\"6788CDE2\"},\"player2\":{\"side\":1,\"codigo\":\"8F79AE\"}}"
stockfish = Stockfish("stockfish_15.1_win_x64_avx2/stockfish-windows-2022-x86-64-avx2.exe")
stockfish.set_depth(20)
stockfish.set_skill_level(20)


@app.get("/")
async def evaluation():
    initial_board = board.fen()
    stockfish.set_fen_position(initial_board)
    best_plays = stockfish.get_best_move()
    try:
        board.push_san(best_plays)
    except Exception as e:
        pass
    if board.is_stalemate():
        return {"jogada": str(best_plays),
                "mensagem": "Oferecer empate"}
    elif board.is_check():
        return {"jogada": str(best_plays),
                "mensagem": "Check"}
    elif board.is_checkmate():
        return {"jogada": str(best_plays),
                "mensagem": "CheckMate"}
    board.set_fen(initial_board)

    return {"jogada": str(best_plays)}


@app.get("otimizado/")
async def optimize_evaluation():
    initial_board = board.fen()
    stockfish.set_fen_position(initial_board)
    best_plays = stockfish.get_best_move()
    try:
        board.push_san(best_plays)
    except Exception as e:
        pass
    if board.is_stalemate():
        return {"jogada": str(best_plays),
                "mensagem": "Oferecer empate"}
    elif board.is_check():
        return {"jogada": str(best_plays),
                "mensagem": "Check"}
    elif board.is_checkmate():
        return {"jogada": str(best_plays),
                "mensagem": "CheckMate"}

    return {"jogada": str(best_plays)}


@app.post("/jogada/{move}")
async def jogada(move: str):
    try:
        jogada = chess.Move.from_uci(move)
        if board.is_legal(jogada):
            board.push_san(move)
        else:
            return {"mensagem": "Jogada Ilegal"}
    except Exception as e:
        return {"error": str(e)}
    if board.is_stalemate():
        return {"mensagem": "Oferecer Empate"}

    return {"move": str(move)}


@app.post("/enemy/{move}")
async def enemy_play(move: str):
    try:
        a = await jogada(move)
        if 'mensagem' in a:
            if a['mensagem'] == "Jogada Ilegal":
                raise Exception('Jogada Ilegal do Inimigo')
    except Exception as e:
        return {"error": str(e)}
    our = await optimize_evaluation()
    print(board)
    return {"move": str(move),
            "our": our}
