from flask import Flask, request, jsonify
from flask_cors import CORS
import chess
import chess.engine
import random
from main import Chess_AI
from chessEval1.useModel import find_best_move_with_model
from chessEval2.eval_tactic_model import game
import numpy as np

STOCKFISH_PATH = r"C:\Program Files (x86)\stockfish\stockfish-windows-x86-64-avx2.exe"

app = Flask(__name__)
CORS(app)

@app.route("/chess/play", methods=["POST"])
def ai_move():
    data = request.get_json()
    fen = data.get("fen")

    board = chess.Board(fen)

    if board.is_game_over():
        return jsonify({
        "move": '',
        "status": 'Game Over'})

    # Pick a random legal move for now
    legal_moves = list(board.legal_moves)
    move = random.choice(legal_moves)

    board.push(move)
    
    print(move)

    return jsonify({
        "move": move.uci(),   #->"e2e4",
        "status": 'Active'
    })


@app.route("/chess/minimax/play", methods=["POST"])
def Minimax():
    data = request.get_json()
    fen = data.get("fen")
    board = chess.Board(fen)

    if board.is_game_over():
        return jsonify({
        "move": '',
        "status": 'Game Over'
    })

    chessAi = Chess_AI()
    best_move = chessAi.find_best_move(board, 3)

    return jsonify({
        "move": best_move.uci(),
        "status": 'Active'
    })


@app.route("/chess/model/CNN1+VTT/play", methods=["POST"])
def Model1Game():
    data = request.get_json()
    fen = data.get("fen")
    board = chess.Board(fen)

    if board.is_game_over():
        return jsonify({
        "move": '',
        "status": 'Game Over'
    })

    best_move = find_best_move_with_model(board)

    return jsonify({
        "move": str(best_move),#.uci(),,
        "status": 'Active'
    })

@app.route("/chess/model/CNN2/play", methods=["POST"])
def Model2Game():
    data = request.get_json()
    fen = data.get("fen")
    board = chess.Board(fen)

    if board.is_game_over():
        return jsonify({
        "move": '',
        "status": 'Game Over'
    })

    best_move = game.get_best_move(board.fen())

    return jsonify({
        "move": str(best_move),
        "status": 'Active'
    })

@app.route("/chess/model/2m/play", methods=["POST"])
def Model2MinimaxGame():
    data = request.get_json()
    fen = data.get("fen")
    board = chess.Board(fen)

    if board.is_game_over():
        return jsonify({
        "move": '',
        "status": 'Game Over'
    })

    best_move = "game.get_best_move_minimax(board.fen(), 3)"

    return jsonify({
        "move": str(best_move),
        "status": 'Active'
    })

@app.route("/chess/model/stockfish/play", methods=["POST"])
def StockfishGame():
    data = request.get_json()
    fen = data.get("fen")
    board = chess.Board(fen)

    if board.is_game_over():
        return jsonify({
        "move": '',
        "status": 'Game Over'
    })

    # stockfish_engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
    # stockfish_engine.configure({"Skill Level": 1})
    # # Get best move
    # result = stockfish_engine.play(board, chess.engine.Limit(time=0.5))
    # best_move = result.move.uci()  # Convert move to UCI string
    return "jsonify({'move': best_move,'status': 'Active'})"



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='4090')