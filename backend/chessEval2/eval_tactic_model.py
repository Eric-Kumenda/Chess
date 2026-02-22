import chess
import numpy as np
import math
from .training import board_to_tensor, model

class CombinedEngine:
    def __init__(self, model):
        self.model = model

    def evaluate_position(self, fen):
        board = chess.Board(fen)
        tensor = board_to_tensor(board)
        tensor = np.expand_dims(tensor, axis=0)

        evaluation = self.model.predict(tensor, verbose=0)
        return evaluation[0][0]
    
    def minimax(self, board, depth, alpha, beta, is_maximizing):
        board_fen = board.fen()

        # Cache check
        # if (board_fen, depth, is_maximizing) in self.transposition_table:
        #     return self.transposition_table[(board_fen, depth, is_maximizing)]
        
        if depth == 0 or board.is_game_over():
            eval_value = self.evaluate_position(board.fen())
            # self.transposition_table[(board_fen, depth, is_maximizing)] = eval_value
            return eval_value

        legal_moves = board.legal_moves

        if is_maximizing:
            max_eval = -math.inf
            for move in legal_moves:
                board.push(move)
                eval = self.minimax(board, depth - 1, alpha, beta, False)
                board.pop()
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            # self.transposition_table[(board_fen, depth, is_maximizing)] = max_eval
            return max_eval
        else:
            min_eval = math.inf
            for move in legal_moves:
                board.push(move)
                eval = self.minimax(board, depth - 1, alpha, beta, True)
                board.pop()
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            # self.transposition_table[(board_fen, depth, is_maximizing)] = min_eval
            return min_eval
        

    def get_best_move(self, fen):
        board = chess.Board(fen)
        best_move = None
        best_evaluation = float('-inf') if board.turn == chess.WHITE else float('inf')

        for move in board.legal_moves:
            board.push(move)
            evaluation = self.evaluate_position(board.fen())
            board.pop()

            if board.turn ==chess.WHITE:
                if evaluation > best_evaluation:
                    best_evaluation = evaluation
                    best_move = move
            else:
                if evaluation < best_evaluation:
                    best_evaluation = evaluation
                    best_move = move



        return best_move
    
    def get_best_move_minimax(self, fen,depth):
        board = chess.Board(fen)
        best_move = None
        best_evaluation = float('-inf') if board.turn == chess.WHITE else float('inf')

        for move in board.legal_moves:
            board.push(move)
            evaluation = self.minimax(
                board, depth - 1, -math.inf, math.inf, board.turn == chess.BLACK
            )
            board.pop()


            if board.turn ==chess.WHITE:
                if evaluation > best_evaluation:
                    best_evaluation = evaluation
                    best_move = move
            else:
                if evaluation < best_evaluation:
                    best_evaluation = evaluation
                    best_move = move


        return best_move
    
# Create an instance of the SimpleChessEngine with the loaded model
game = CombinedEngine(model)