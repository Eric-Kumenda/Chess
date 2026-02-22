import tensorflow as tf
import chess
import numpy as np
from chessEval1.CNN_only_training import ChessEvaluationCNN, ConditionalBatchNorm, fen_to_tensor
from chessEval1.NN_training import ChessEvaluationHybridModel, ConditionalBatchNorm
# import os
# os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
# tf.config.experimental.set_memory_growth(tf.config.list_physical_devices('GPU')[0], True)

# Load model once at startup
model = tf.keras.models.load_model(
    # "chessEval1/models/CNN-only.keras",
    "chessEval1/models/model.keras",
    custom_objects={"ChessEvaluationHybridModel": ChessEvaluationHybridModel,"ConditionalBatchNorm": ConditionalBatchNorm},
    # custom_objects={"ChessEvaluationCNN": ChessEvaluationCNN},
        compile=False
)

def evaluate_board_with_model(boardFen):
    board_tensor, active_player, halfmove_clock = fen_to_tensor(boardFen)

    # Expand dims to make it a batch of 1
    board_tensor = np.expand_dims(board_tensor, axis=0)         # shape: (1, 13, 8, 8)
    active_player = np.array([active_player], dtype=np.int32)   # shape: (1,)
    halfmove_clock = np.array([halfmove_clock], dtype=np.float32)  # shape: (1,)

    prediction = model.predict((board_tensor, active_player, halfmove_clock))
    # print(prediction)
    return prediction[0][0]

def find_best_move_with_model(board: chess.Board):
    best_move = None
    best_value = -np.inf if board.turn == chess.WHITE else np.inf

    for move in board.legal_moves:
        board.push(move)
        value = evaluate_board_with_model(board.fen())
        board.pop()

        if board.turn == chess.WHITE:
            if value > best_value:
                best_value = value
                best_move = move
        else:
            if value < best_value:
                best_value = value
                best_move = move

    return best_move


def order_moves(board: chess.Board) -> list:
    """
    Simple heuristic:  
    1. Captures first (most valuable victim – least valuable attacker)  
    2. Then promotions  
    3. Then other moves
    """
    moves = list(board.legal_moves)

    def move_score(move):
        # MVV-LVA (Most Valuable Victim - Least Valuable Attacker)
        if board.is_capture(move):
            victim = board.piece_at(move.to_square)
            attacker = board.piece_at(move.from_square)
            victim_value = piece_value(victim.piece_type) if victim else 0
            attacker_value = piece_value(attacker.piece_type) if attacker else 0
            return 10_000 + (victim_value * 10 - attacker_value)
        if move.promotion:
            return 5_000
        return 0  # non-captures last

    def piece_value(piece_type):
        values = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3,
                  chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0}
        return values.get(piece_type, 0)

    return sorted(moves, key=move_score, reverse=True)


def minimax(board: chess.Board, depth: int, alpha: float, beta: float, maximizing: bool) -> float:
    if depth == 0 or board.is_game_over():
        return evaluate_board_with_model(board.fen())

    if maximizing:
        max_eval = -np.inf
        for move in order_moves(board):
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = np.inf
        for move in order_moves(board):
            board.push(move)
            eval = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval


# def find_best_move_with_model(board: chess.Board, depth: int = 2):
#     best_move = None
#     if board.turn == chess.WHITE:
#         best_value = -np.inf
#         for move in order_moves(board):
#             board.push(move)
#             value = minimax(board, depth - 1, -np.inf, np.inf, False)
#             board.pop()
#             if value > best_value:
#                 best_value = value
#                 best_move = move
#     else:
#         best_value = np.inf
#         for move in order_moves(board):
#             board.push(move)
#             value = minimax(board, depth - 1, -np.inf, np.inf, True)
#             board.pop()
#             if value < best_value:
#                 best_value = value
#                 best_move = move
#     return best_move
