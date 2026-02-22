import os
import chess
import numpy as np
import tensorflow as tf

# Function to convert a chess board to a tensor representation
# The tensor shape is (8, 8, 17) where:
# - 8x8 for the board squares
# - 17 channels for different pieces and game state information
#   (12 piece types + 1 side to move + 4 castling rights)
def board_to_tensor(board):
    tensor = np.zeros((8, 8, 17), dtype=np.int8)

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            piece_type = piece.piece_type  # 1 (pawn) to 6 (king)
            color = int(piece.color)       # 0 for white, 1 for black
            idx = piece_type - 1 + (6 * color)

            row = 7 - (square // 8)  # Flip rank: 0 (a1..h1) becomes 7
            col = square % 8         # File stays the same
            tensor[row, col, idx] = 1

    # Add side to move in channel 12
    tensor[:, :, 12] = 1 if board.turn == chess.WHITE else 0
    # Add castling rights in channels 13-16
    tensor[:, :, 13] = int(board.has_kingside_castling_rights(chess.WHITE))
    tensor[:, :, 14] = int(board.has_queenside_castling_rights(chess.WHITE))
    tensor[:, :, 15] = int(board.has_kingside_castling_rights(chess.BLACK))
    tensor[:, :, 16] = int(board.has_queenside_castling_rights(chess.BLACK))

    return tensor


def select_by_confidence(inputs):
    score, checkmate = inputs
    # If checkmate output is > 15000, trust checkmate model, else trust score model
    threshold = 15000.0
    use_checkmate = tf.abs(checkmate) > threshold
    return tf.where(use_checkmate, checkmate, score)


# Load the model
model_path = os.path.join(os.path.dirname(__file__), 'models', 'model_combined.keras')
model_path = os.path.abspath(model_path)
model = tf.keras.models.load_model(model_path, custom_objects={'select_by_confidence': select_by_confidence})
