import chess
import math


class Chess_AI:
    def __init__(self):
        self.PIECE_VALUES = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
            chess.KING: 0
        }
        self.transposition_table = {}

    def evaluate_board(self, board):
        """Basic material count evaluation from White's perspective."""
        value = 0
        for piece_type in self.PIECE_VALUES:
            value += len(board.pieces(piece_type, chess.WHITE)) * self.PIECE_VALUES[piece_type]
            value -= len(board.pieces(piece_type, chess.BLACK)) * self.PIECE_VALUES[piece_type]
        return value
    
    def order_moves(self, board):
        """Order moves: captures first, then others."""
        moves = list(board.legal_moves)
        moves.sort(key=lambda move: board.is_capture(move), reverse=True)
        return moves
    
    def minimax(self, board, depth, alpha, beta, is_maximizing):
        """Minimax with alpha-beta pruning."""
        board_fen = board.fen()

        # Cache check
        if (board_fen, depth, is_maximizing) in self.transposition_table:
            return self.transposition_table[(board_fen, depth, is_maximizing)]
        
        if depth == 0 or board.is_game_over():
            eval_value = self.evaluate_board(board)
            self.transposition_table[(board_fen, depth, is_maximizing)] = eval_value
            return eval_value

        legal_moves = self.order_moves(board)

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
            self.transposition_table[(board_fen, depth, is_maximizing)] = max_eval
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
            self.transposition_table[(board_fen, depth, is_maximizing)] = min_eval
            return min_eval
        
    def find_best_move(self, board, depth):
        """Returns best move for current player."""
        best_move = None
        best_value = -math.inf if board.turn == chess.WHITE else math.inf

        for move in self.order_moves(board):
            board.push(move)
            board_value = self.minimax(
                board, depth - 1, -math.inf, math.inf, board.turn == chess.BLACK
            )
            board.pop()

            if board.turn == chess.WHITE:  # If it was White's turn before push
                if board_value > best_value:
                    best_value = board_value
                    best_move = move
            else:
                if board_value < best_value:
                    best_value = board_value
                    best_move = move

        return best_move