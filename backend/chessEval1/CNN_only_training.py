import tensorflow as tf
from tensorflow.keras import layers, Model, optimizers
import pandas as pd
import chess
import numpy as np

piece_to_index = {
    'P': 0, 'N': 1, 'B': 2, 'R': 3, 'Q': 4, 'K': 5,
    'p': 6, 'n': 7, 'b': 8, 'r': 9, 'q': 10, 'k': 11
}

# Helper functions to convert FEN to tensor
def fen_to_tensor(fen):
    board = chess.Board(fen)
    board_tensor = np.zeros((13, 8, 8), dtype=np.float32)
    
    # Castling mapping
    castling_map = {'K': (7, 6), 'Q': (7, 2), 'k': (0, 6), 'q': (0, 2)}
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            row, col = 7 - chess.square_rank(square), chess.square_file(square)
            board_tensor[piece_to_index[piece.symbol()], row, col] = 1

    # FEN features
    fen_parts = fen.split()
    active_player = 1 if fen_parts[1] == 'w' else 0
    halfmove_clock = float(fen_parts[4]) / 100.0
    en_passant = fen_parts[3]
    castle_rights = fen_parts[2]
    
    # Encode en passant
    if en_passant != '-':
        row, col = 7 - (int(en_passant[1]) - 1), ord(en_passant[0]) - ord('a')
        board_tensor[12, row, col] = 1

    # Encode castling rights
    if castle_rights != '-':
        for right in castle_rights:
            row, col = castling_map[right]
            board_tensor[12, row, col] = 1

    return board_tensor, active_player, halfmove_clock

# Custom Conditional Batch Norm Layer
class ConditionalBatchNorm(tf.keras.layers.Layer):
    def __init__(self, num_features, num_conditions, **kwargs):
        super().__init__(**kwargs)
        self.num_features = num_features
        self.num_conditions = num_conditions
        self.bn = tf.keras.layers.BatchNormalization(center=False, scale=False)
        self.gamma = tf.keras.layers.Embedding(num_conditions, num_features,
                                               embeddings_initializer='ones')
        self.beta = tf.keras.layers.Embedding(num_conditions, num_features,
                                              embeddings_initializer='zeros')

    def call(self, x, condition):
        normalized = self.bn(x)
        gamma = self.gamma(condition)[:, tf.newaxis, tf.newaxis, :]
        beta = self.beta(condition)[:, tf.newaxis, tf.newaxis, :]
        return gamma * normalized + beta

    def get_config(self):
        config = super().get_config()
        config.update({
            "num_features": self.num_features,
            "num_conditions": self.num_conditions
        })
        return config

    @classmethod
    def from_config(cls, config):
        return cls(**config)


# Model Architecture
class ChessEvaluationCNN(tf.keras.Model):
    def __init__(self, num_piece_channels=13, num_classes=1, num_conditions=2, **kwargs):
        super().__init__(**kwargs)
        self.num_piece_channels = num_piece_channels
        self.num_classes = num_classes
        self.num_conditions = num_conditions

        self.conv1 = tf.keras.layers.Conv2D(64, kernel_size=3, padding='same')
        self.cbn1 = ConditionalBatchNorm(64, num_conditions)
        self.conv2 = tf.keras.layers.Conv2D(128, kernel_size=3, padding='same')
        self.cbn2 = ConditionalBatchNorm(128, num_conditions)
        self.conv3 = tf.keras.layers.Conv2D(256, kernel_size=3, padding='same')
        self.cbn3 = ConditionalBatchNorm(256, num_conditions)

        self.flatten = tf.keras.layers.Flatten()
        self.fc1 = tf.keras.layers.Dense(1024, activation='relu')
        self.fc2 = tf.keras.layers.Dense(num_classes)

    def call(self, inputs):
        #board_tensor, active_player, halfmove_clock = inputs
        board_tensor = inputs[0]
        active_player = inputs[1]
        halfmove_clock = inputs[2]
        x = self.conv1(board_tensor)
        x = self.cbn1(x, active_player)
        x = tf.nn.relu(x)

        x = self.conv2(x)
        x = self.cbn2(x, active_player)
        x = tf.nn.relu(x)

        x = self.conv3(x)
        x = self.cbn3(x, active_player)
        x = tf.nn.relu(x)

        x = tf.reduce_mean(x, axis=[1, 2])  # Global average pooling
        x = tf.concat([self.fc1(x), tf.expand_dims(halfmove_clock, -1)], axis=1)
        output = self.fc2(x)
        return output

    def get_config(self):
        config = super().get_config()
        config.update({
            "num_piece_channels": self.num_piece_channels,
            "num_classes": self.num_classes,
            "num_conditions": self.num_conditions
        })
        return config

    @classmethod
    def from_config(cls, config):
        return cls(**config)


# Load dataset from CSV
def load_data(csv_path,sample_size=1000):
    data = pd.read_csv(csv_path)
    data = data.sample(n=sample_size, random_state=42)
    boards, active_players, halfmove_clocks, evaluations = [], [], [], []
    for idx, row in data.iterrows():
        board_tensor, active_player, halfmove_clock = fen_to_tensor(row['FEN'])
        boards.append(board_tensor)
        active_players.append(active_player)
        halfmove_clocks.append(halfmove_clock)
        evaluation=row['Evaluation']

        if evaluation.startswith('#'):
            # Convert checkmate to large positive/negative values
            if evaluation[1] == '-':
                # Negative checkmate (opponent checkmating)
                evaluation = -10000.0  # Arbitrary large negative value
            else:
                # Positive checkmate (current player checkmating)
                evaluation = 10000.0  # Arbitrary large positive value
        else:
            # Standard centipawn evaluation, convert to float
            evaluation = float(evaluation)
        
        evaluations.append(evaluation)

    boards = np.array(boards)
    active_players = np.array(active_players)
    halfmove_clocks = np.array(halfmove_clocks)
    evaluations = np.array(evaluations)
    return boards, active_players, halfmove_clocks, evaluations

class LossHistory(tf.keras.callbacks.Callback):
    def __init__(self):
        super().__init__()
        self.losses = []

    def on_epoch_end(self, epoch, logs=None):
        # Append the loss at the end of each epoch
        self.losses.append(logs.get('loss'))

# Prepare TensorFlow dataset
SAMPLE_SIZE=100000
EPOCHS=10
BATCH_SIZE=32
# boards, active_players, halfmove_clocks, evaluations = load_data('models/random_evals.csv',sample_size=SAMPLE_SIZE)

# inputs = (boards, active_players, halfmove_clocks)
# targets = evaluations
# dataset = tf.data.Dataset.from_tensor_slices((inputs, targets))
# dataset = dataset.shuffle(buffer_size=1024).batch(BATCH_SIZE)

# loss_history = LossHistory()

# # Compile and train the model
# model = ChessEvaluationCNN()
# lr_schedule = tf.keras.optimizers.schedules.ExponentialDecay(
#     initial_learning_rate=0.005,
#     decay_steps=10000,
#     decay_rate=0.9)

# model.compile(optimizer=optimizers.Adam(learning_rate=lr_schedule), loss='mse')
# model.fit(dataset, epochs=EPOCHS, callbacks=[loss_history])

# from datetime import datetime
# now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
# model.save(f'models/kaggle/working/{now}.keras')