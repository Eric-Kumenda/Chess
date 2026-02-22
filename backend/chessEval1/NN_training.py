import tensorflow as tf
from tensorflow.keras import layers, Model, optimizers
import pandas as pd
import chess
import numpy as np

piece_to_index = {
    'P': 0, 'N': 1, 'B': 2, 'R': 3, 'Q': 4, 'K': 5,
    'p': 6, 'n': 7, 'b': 8, 'r': 9, 'q': 10, 'k': 11
}

# 1
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

#2
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
            # Converting checkmate to large positive/negative values
            if evaluation[1] == '-':
                # Negative checkmate (opponent checkmating)
                evaluation = -10000.0  # Arbitrary large negative value
            else:
                # Positive checkmate (current player checkmating)
                evaluation = 10000.0  # Arbitrary large positive value
        else:
            # Standard centipawn evaluation to float
            evaluation = float(evaluation)
        
        evaluations.append(evaluation)

    boards = np.array(boards)
    active_players = np.array(active_players)
    halfmove_clocks = np.array(halfmove_clocks)
    evaluations = np.array(evaluations)
    return boards, active_players, halfmove_clocks, evaluations


#3 - Distinguish between black & white turns to play when training the model
# Custom Conditional Batch Norm Layer
class ConditionalBatchNorm(layers.Layer):
    def __init__(self, num_features, num_conditions):
        super().__init__()
        self.num_features = num_features
        self.bn = layers.BatchNormalization(center=False, scale=False)
        self.gamma = layers.Embedding(num_conditions, num_features, embeddings_initializer='ones')
        self.beta = layers.Embedding(num_conditions, num_features, embeddings_initializer='zeros')

    def call(self, x, condition):
        normalized = self.bn(x)
        gamma = self.gamma(condition)[:, tf.newaxis, tf.newaxis, :]
        beta = self.beta(condition)[:, tf.newaxis, tf.newaxis, :]
        return gamma * normalized + beta
    
#4 (a)
""" Original pure CNN architecture:¶
    This version used a convultional network with a kernel size of 3
    to learn the position's features. IN theory, useful for local features
    identification like pawn chains and structures, but can't make sense of
    long range relationships like threats, pins and attacks. """
# Model Architecture
class ChessEvaluationCNN(Model):
    def __init__(self, num_piece_channels=13, num_classes=1, num_conditions=2):
        super(ChessEvaluationCNN, self).__init__()
        
        # Convolutional layers
        self.conv1 = layers.Conv2D(64, kernel_size=3, padding='same')
        self.cbn1 = ConditionalBatchNorm(64, num_conditions)
        self.conv2 = layers.Conv2D(128, kernel_size=3, padding='same')
        self.cbn2 = ConditionalBatchNorm(128, num_conditions)
        self.conv3 = layers.Conv2D(256, kernel_size=3, padding='same')
        self.cbn3 = ConditionalBatchNorm(256, num_conditions)
        
        # Fully connected layers
        self.flatten = layers.Flatten()
        self.fc1 = layers.Dense(1024, activation='relu')
        self.fc2 = layers.Dense(num_classes)

    def call(self, inputs):
        board_tensor, active_player, halfmove_clock = inputs

        # Forward pass
        x = self.conv1(board_tensor)
        x = self.cbn1(x, active_player)
        x = tf.nn.relu(x)

        x = self.conv2(x)
        x = self.cbn2(x, active_player)
        x = tf.nn.relu(x)

        x = self.conv3(x)
        x = self.cbn3(x, active_player)
        x = tf.nn.relu(x)
        
        # Global average pooling
        x = tf.reduce_mean(x, axis=[1, 2])  # (batch_size, 256)
        
        # Fully connected layer with halfmove clock
        x = tf.concat([self.fc1(x), tf.expand_dims(halfmove_clock, -1)], axis=1)
        output = self.fc2(x)
        
        return output
    
#3 (b)
"""
    CNN + VIT
    using a hybrid architecture consisting of convolutional network + vision
    transformer with the added benefit of self attention, giving the model
    the ability to learn long range piece relationships, highly scalable. """
# Helper function to create patches for ViT
def create_patches(x, patch_size):
    # Dynamically get batch size and input dimensions
    batch_size = tf.shape(x)[0]  # Dynamically fetch the actual batch size at runtime
    channels = x.shape[1]  # Channels are known statically (13)
    height = x.shape[2]     # Known statically (8)
    width = x.shape[3]      # Known statically (8)

    # Ensure the input is in the expected shape
    if height != 8 or width != 8:
        raise ValueError("Input dimensions for chessboard must be (None, 13, 8, 8)")

    # Reshape the input tensor to create patches
    patches = tf.image.extract_patches(
        images=tf.transpose(x, [0, 2, 3, 1]),  
        sizes=[1, patch_size, patch_size, 1],
        strides=[1, patch_size, patch_size, 1],
        rates=[1, 1, 1, 1],
        padding='VALID'
    )

    # Reshape the patches into (batch_size, num_patches, patch_dim)
    patch_dim = patch_size * patch_size * channels 
    num_patches = (height // patch_size) * (width // patch_size)
    
    # Use static shape where possible to avoid runtime errors during XLA compilation
    patches = tf.reshape(patches, [-1, num_patches, patch_dim])  # Use -1 for dynamic batch_size

    return patches

class ViTBlock(layers.Layer):
    def __init__(self, num_heads, embed_dim, ff_dim):
        super(ViTBlock, self).__init__()
        self.attention = layers.MultiHeadAttention(num_heads=num_heads, key_dim=embed_dim)
        self.ffn = tf.keras.Sequential([
            layers.Dense(ff_dim, activation='relu'),
            layers.Dense(embed_dim)
        ])
        self.layernorm1 = layers.LayerNormalization(epsilon=1e-6)
        self.layernorm2 = layers.LayerNormalization(epsilon=1e-6)

    def call(self, inputs):
        attn_output = self.attention(inputs, inputs)
        out1 = self.layernorm1(inputs + attn_output)
        ffn_output = self.ffn(out1)
        out2 = self.layernorm2(out1 + ffn_output)
        return out2

# Hybrid model definition (CNN + ViT)
from keras.saving import register_keras_serializable

@register_keras_serializable(package="ChessModel")
class ChessEvaluationHybridModel(Model):
    def __init__(self, num_piece_channels=13, num_classes=1, num_conditions=2, patch_size=2):
        super(ChessEvaluationHybridModel, self).__init__()
        
        self.num_piece_channels=num_piece_channels
        self.num_classes=num_classes
        self.num_conditions=num_conditions
        self.patch_size=patch_size
        
        # CNN layers
        self.conv1 = layers.Conv2D(64, kernel_size=3, padding='same')
        self.cbn1 = ConditionalBatchNorm(64, num_conditions)
        self.conv2 = layers.Conv2D(128, kernel_size=3, padding='same')
        self.cbn2 = ConditionalBatchNorm(128, num_conditions)
        self.conv3 = layers.Conv2D(256, kernel_size=3, padding='same')
        self.cbn3 = ConditionalBatchNorm(256, num_conditions)
        
        # ViT layers
        self.patch_size = patch_size
        self.embedding_dim = (patch_size * patch_size) * num_piece_channels
        self.vit_proj = layers.Dense(self.embedding_dim)  # Project patches into embedding space
        
        self.vit_block1 = ViTBlock(num_heads=4, embed_dim=self.embedding_dim, ff_dim=512)
        self.vit_block2 = ViTBlock(num_heads=4, embed_dim=self.embedding_dim, ff_dim=512)
        
        self.flatten = layers.Flatten()
        
        # Fully connected layers
        self.fc1 = layers.Dense(1024, activation='relu')
        self.fc2 = layers.Dense(num_classes)

    def call(self, inputs):
        board_tensor, active_player, halfmove_clock = inputs

        # CNN forward pass
        x = self.conv1(board_tensor)
        x = self.cbn1(x, active_player)
        x = tf.nn.relu(x)

        x = self.conv2(x)
        x = self.cbn2(x, active_player)
        x = tf.nn.relu(x)

        x = self.conv3(x)
        x = self.cbn3(x, active_player)
        x = tf.nn.relu(x)
        
        # ViT forward pass
        patches = create_patches(board_tensor, self.patch_size)
        patches = self.vit_proj(patches)
        vit_out = self.vit_block1(patches)
        vit_out = self.vit_block2(vit_out)
        vit_out = tf.reduce_mean(vit_out, axis=1)  # Global average pooling for patches

        # Combine CNN and ViT outputs
        x = tf.concat([self.flatten(x), vit_out], axis=1)
        
        # Fully connected layers with halfmove clock
        x = tf.concat([self.fc1(x), tf.expand_dims(halfmove_clock, -1)], axis=1)
        output = self.fc2(x)
        
        return output
    @classmethod
    def from_config(cls, config):
        # Manually pass in the parameters here
        return cls(
            num_piece_channels=config['num_piece_channels'],
            num_classes=config['num_classes'],
            num_conditions=config['num_conditions'],
            patch_size=config['patch_size']
        )

    def get_config(self):
        config = super().get_config()
        # Include the custom arguments in the config dictionary
        config.update({
            'num_piece_channels': self.num_piece_channels,
            'num_classes': self.num_classes,
            'num_conditions': self.num_conditions,
            'patch_size': self.patch_size
        })
        return config
    

#5
# # Model Training
# class LossHistory(tf.keras.callbacks.Callback):
#     def __init__(self):
#         super().__init__()
#         self.losses = []

#     def on_epoch_end(self, epoch, logs=None):
#         # Append the loss at the end of each epoch
        # self.losses.append(logs.get('loss'))

# # Prepare TensorFlow dataset
# SAMPLE_SIZE=1000000
# EPOCHS=2#200
# BATCH_SIZE=512
# boards, active_players, halfmove_clocks, evaluations = load_data('models/random_evals.csv',sample_size=SAMPLE_SIZE)

# inputs = (boards, active_players, halfmove_clocks)
# targets = evaluations
# dataset = tf.data.Dataset.from_tensor_slices((inputs, targets))
# dataset = dataset.shuffle(buffer_size=2048).batch(BATCH_SIZE)

# loss_history = LossHistory()

# from datetime import datetime
# import tensorflow.keras as keras
# from tensorflow.keras.callbacks import ModelCheckpoint


# checkpoint_filepath = "model.keras"#f'checkpoint{now}.model.keras'
# model_checkpoint_callback = keras.callbacks.ModelCheckpoint(
#     filepath=checkpoint_filepath,
#     monitor='loss',
#     mode='min',
#     save_best_only=True)


# lr_schedule = tf.keras.optimizers.schedules.ExponentialDecay(
#     initial_learning_rate=0.005,
#     decay_steps=20000,
#     decay_rate=0.9)

# optimizer=optimizers.Adam(learning_rate=lr_schedule)


# Compile and train the model
# model = ChessEvaluationHybridModel()

# model.compile(optimizer=optimizer, loss='mse')

# model.load_weights(saved_model)


# model.fit(dataset,epochs=EPOCHS, callbacks=[loss_history,model_checkpoint_callback])

# #6
# from datetime import datetime
# now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
# model.save(f'models/kaggle/working/{now}.keras')