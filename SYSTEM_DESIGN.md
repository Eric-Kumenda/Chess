# Chessy — System Design Document

> Comprehensive technical documentation covering architecture, algorithms, models, data pipeline, and frontend design.

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [High-Level Architecture](#2-high-level-architecture)
3. [Backend Architecture](#3-backend-architecture)
    - [Flask API Server](#31-flask-api-server)
    - [Endpoint Specifications](#32-endpoint-specifications)
4. [AI Engines & Algorithms](#4-ai-engines--algorithms)
    - [Random Engine](#41-random-engine)
    - [Minimax with Alpha-Beta Pruning](#42-minimax-with-alpha-beta-pruning)
    - [CNN-Only Evaluation Model (chessEval1)](#43-cnn-only-evaluation-model-chesseval1)
    - [CNN + Vision Transformer Hybrid Model (chessEval1)](#44-cnn--vision-transformer-hybrid-model-chesseval1)
    - [Combined Evaluation Model (chessEval2)](#45-combined-evaluation-model-chesseval2)
    - [Sequence-to-Move Model (chessEval3)](#46-sequence-to-move-model-chesseval3---wip)
    - [Stockfish Integration](#47-stockfish-integration)
5. [Data Pipeline](#5-data-pipeline)
    - [Board Representation — 13-Channel Tensor (Eval1)](#51-board-representation--13-channel-tensor-chesseval1)
    - [Board Representation — 17-Channel Tensor (Eval2)](#52-board-representation--17-channel-tensor-chesseval2)
    - [Data Loading & Preprocessing](#53-data-loading--preprocessing)
    - [Training Pipeline](#54-training-pipeline)
6. [Frontend Architecture](#6-frontend-architecture)
    - [Component Hierarchy](#61-component-hierarchy)
    - [State Management (Redux)](#62-state-management-redux)
    - [Game Flow](#63-game-flow)
    - [UI/UX Features](#64-uiux-features)
7. [Communication Protocol](#7-communication-protocol)
8. [Future Work & Known Limitations](#8-future-work--known-limitations)

---

## 1. System Overview

Chessy is a chess platform that allows a human player to play against multiple AI engines through a web interface. The system is split into two independently running services:

| Service      | Role                                                            | Runtime        |
| ------------ | --------------------------------------------------------------- | -------------- |
| **Backend**  | Hosts AI engines, processes board positions, returns moves      | Python / Flask |
| **Frontend** | Renders the chessboard, manages game state, collects user input | React / Vite   |

The frontend sends the current board state (as a FEN string) to the backend via REST API, the backend computes the best move using the selected AI engine, and returns the move in UCI notation.

---

## 2. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          FRONTEND (React + Vite)                    │
│                                                                     │
│  ┌─────────┐   ┌────────────┐   ┌──────────────┐   ┌────────────┐ │
│  │ App.jsx │──▶│ ChessBoard │──▶│ Redux Store  │──▶│ Async      │ │
│  │ Layout  │   │ Component  │   │ (chessSlice) │   │ Thunks     │ │
│  └─────────┘   └────────────┘   └──────────────┘   └─────┬──────┘ │
│                                                           │        │
└───────────────────────────────────────────────────────────┼────────┘
                                                            │
                                          HTTP POST (JSON)  │
                                          { "fen": "..." }  │
                                                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       BACKEND (Flask :4090)                         │
│                                                                     │
│  ┌──────────────┐   ┌─────────────────────────────────────────────┐│
│  │  server.py   │──▶│  AI Engine Selection                        ││
│  │  (Router)    │   │                                             ││
│  └──────────────┘   │  ┌──────────┐ ┌──────────┐ ┌─────────────┐ ││
│                     │  │ Minimax  │ │ CNN+ViT  │ │ CNN2        │ ││
│                     │  │ main.py  │ │ Eval1    │ │ Eval2       │ ││
│                     │  └──────────┘ └──────────┘ └─────────────┘ ││
│                     └─────────────────────────────────────────────┘│
│                                                                     │
│  Response: { "move": "e2e4", "status": "Active" }                  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Backend Architecture

### 3.1 Flask API Server

**File**: `backend/server.py`

The server is a simple Flask app with CORS enabled. It exposes six POST endpoints, each corresponding to a different AI strategy. The server:

1. Receives a FEN string in the request body
2. Constructs a `chess.Board` from the FEN
3. Checks for game-over state
4. Delegates move computation to the appropriate engine
5. Returns the move in UCI format + game status

**Server Configuration:**

```python
app.run(debug=True, host='0.0.0.0', port='4090')
```

### 3.2 Endpoint Specifications

| Endpoint                           | Handler Function      | Engine                      | Status    |
| ---------------------------------- | --------------------- | --------------------------- | --------- |
| `POST /chess/play`                 | `ai_move()`           | Random (baseline)           | ✅ Active |
| `POST /chess/minimax/play`         | `Minimax()`           | Minimax + alpha-beta        | ✅ Active |
| `POST /chess/model/CNN1+VTT/play`  | `Model1Game()`        | CNN+ViT hybrid (chessEval1) | ✅ Active |
| `POST /chess/model/CNN2/play`      | `Model2Game()`        | Combined model (chessEval2) | ✅ Active |
| `POST /chess/model/2m/play`        | `Model2MinimaxGame()` | CNN2 + Minimax              | ⚠ Stub    |
| `POST /chess/model/stockfish/play` | `StockfishGame()`     | Stockfish engine            | ⚠ Stub    |

**Request Format:**

```json
POST /chess/minimax/play
Content-Type: application/json

{ "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1" }
```

**Response Format:**

```json
{ "move": "e7e5", "status": "Active" }
```

On game over: `{ "move": "", "status": "Game Over" }`

---

## 4. AI Engines & Algorithms

### 4.1 Random Engine

**File**: `backend/server.py` (inline in `ai_move()`)

The simplest baseline. Selects a uniformly random legal move from the current position. Useful for testing and as a reference point for evaluating other engines.

```python
legal_moves = list(board.legal_moves)
move = random.choice(legal_moves)
```

---

### 4.2 Minimax with Alpha-Beta Pruning

**File**: `backend/main.py` — Class `Chess_AI`

A classical game-tree search algorithm that evaluates all possible move sequences up to a fixed depth and selects the optimal move assuming perfect play by both sides.

#### Algorithm Details

| Parameter           | Value                             |
| ------------------- | --------------------------------- |
| Search Depth        | 3 plies                           |
| Pruning             | Alpha-beta                        |
| Move Ordering       | Captures first (improves pruning) |
| Caching             | Transposition table (dict)        |
| Evaluation Function | Material count (centipawn)        |

#### Piece Values

| Piece  | Value |
| ------ | ----- |
| Pawn   | 1     |
| Knight | 3     |
| Bishop | 3     |
| Rook   | 5     |
| Queen  | 9     |
| King   | 0     |

#### Evaluation Function

Static board evaluation based purely on **material balance** from White's perspective:

```
score = Σ (white_pieces × value) − Σ (black_pieces × value)
```

#### Move Ordering

Captures are sorted first via a simple boolean sort. This significantly improves alpha-beta pruning efficiency by examining high-impact moves early.

#### Transposition Table

A dictionary mapping `(fen, depth, is_maximizing)` → evaluation. This avoids re-evaluating positions that are reached through different move orders (transpositions).

#### Minimax Pseudocode

```
function minimax(board, depth, α, β, maximizing):
    if depth = 0 or game_over:
        return evaluate(board)

    if maximizing:
        max_eval = −∞
        for each move in ordered_moves:
            eval = minimax(board_after_move, depth−1, α, β, false)
            max_eval = max(max_eval, eval)
            α = max(α, eval)
            if β ≤ α: break    ← pruning
        return max_eval
    else:
        min_eval = +∞
        for each move in ordered_moves:
            eval = minimax(board_after_move, depth−1, α, β, true)
            min_eval = min(min_eval, eval)
            β = min(β, eval)
            if β ≤ α: break    ← pruning
        return min_eval
```

---

### 4.3 CNN-Only Evaluation Model (chessEval1)

**File**: `backend/chessEval1/CNN_only_training.py` — Class `ChessEvaluationCNN`

A pure convolutional neural network that acts as a **board evaluation function**, replacing the hand-crafted material-count heuristic.

#### Architecture

```
Input: (batch, 13, 8, 8) board tensor
       (batch,) active player (int: 0 or 1)
       (batch,) halfmove clock (float, normalized)
    │
    ▼
Conv2D(64, 3×3, same) → ConditionalBatchNorm → ReLU
    │
    ▼
Conv2D(128, 3×3, same) → ConditionalBatchNorm → ReLU
    │
    ▼
Conv2D(256, 3×3, same) → ConditionalBatchNorm → ReLU
    │
    ▼
Global Average Pooling (spatial dims)
    │
    ▼
Dense(1024, ReLU) ─concat─ halfmove_clock
    │
    ▼
Dense(1) → Evaluation score (centipawns)
```

#### Key Design Decisions

- **Conditional Batch Normalization**: Uses an `Embedding` layer to produce per-condition γ and β values, allowing the network to learn different normalization parameters for White-to-move vs Black-to-move positions.
- **Global Average Pooling** instead of flattening: Reduces parameter count and provides translation invariance.
- **Halfmove Clock** concatenated before the final layer: Encodes draw-related position information.

#### Limitations

- Kernel size of 3×3 restricts the receptive field to **local patterns** (e.g., pawn chains, adjacent piece interactions).
- Cannot inherently capture **long-range relationships** like pins, skewers, or distant piece coordination without deep stacking.

---

### 4.4 CNN + Vision Transformer Hybrid Model (chessEval1)

**File**: `backend/chessEval1/NN_training.py` — Class `ChessEvaluationHybridModel`

This is the primary evaluation model. It combines **CNNs for local feature extraction** with a **Vision Transformer (ViT) for global attention over the board**, addressing the locality limitation of pure CNNs.

#### Architecture

```
Input: (batch, 13, 8, 8) board tensor
       (batch,) active player
       (batch,) halfmove clock
    │
    ├───── CNN Branch ──────────────────┐
    │  Conv2D(64) → CBN → ReLU         │
    │  Conv2D(128) → CBN → ReLU        │
    │  Conv2D(256) → CBN → ReLU        │
    │  Flatten                          │
    │                                   │
    ├───── ViT Branch ─────────────┐    │
    │  Extract 2×2 patches         │    │
    │  (→ 16 patches, dim=52)      │    │
    │  Linear projection           │    │
    │  ViT Block 1 (4 heads)       │    │
    │  ViT Block 2 (4 heads)       │    │
    │  Global Average Pool         │    │
    │                              │    │
    └──────────────┬───────────────┘    │
                   │                    │
                   ▼                    ▼
            Concatenate (ViT out + CNN out)
                   │
                   ▼
           Dense(1024, ReLU) ─concat─ halfmove_clock
                   │
                   ▼
              Dense(1) → Evaluation
```

#### Vision Transformer Block

Each `ViTBlock` consists of:

1. **Multi-Head Self-Attention** (4 heads) — enables patches to attend to all other patches, capturing long-range piece relationships.
2. **Feed-Forward Network** (Dense → ReLU → Dense, hidden dim 512)
3. **Layer Normalization** + **residual connections** on both sub-layers.

#### Patching Strategy

- Board tensor (13 channels × 8×8) is split into **2×2 patches**.
- Each patch covers a 2×2 region of the board = **16 patches total**.
- Patch dimension = 2 × 2 × 13 = **52 features per patch**.

#### Why Hybrid?

| Feature                      | CNN         | ViT                   |
| ---------------------------- | ----------- | --------------------- |
| Local patterns (pawns, etc.) | ✅ Strong   | ⚠ Requires many heads |
| Long-range relationships     | ⚠ Limited   | ✅ Global attention   |
| Parameter efficiency         | ✅ Moderate | ⚠ Data hungry         |

By concatenating both branches, the model leverages local spatial features (CNN) **and** global board-wide attention (ViT).

#### Training Configuration (from comments)

| Parameter              | Value                                                      |
| ---------------------- | ---------------------------------------------------------- |
| Dataset                | `random_evals.csv` (FEN + centipawn eval)                  |
| Sample Size            | Up to 1,000,000 positions                                  |
| Batch Size             | 512                                                        |
| Epochs                 | 200 (commented default)                                    |
| Loss                   | Mean Squared Error (MSE)                                   |
| Optimizer              | Adam                                                       |
| Learning Rate Schedule | Exponential decay (init: 0.005, decay: 0.9, steps: 20,000) |
| Checkpointing          | Best model by loss (`model.keras`)                         |

---

### 4.5 Combined Evaluation Model (chessEval2)

**File**: `backend/chessEval2/training.py` + `backend/chessEval2/eval_tactic_model.py`

This is a separate model pipeline using a different board tensor encoding and a **confidence-based output selection** mechanism.

#### Board Representation

A **(8, 8, 17)** tensor:

| Channels | Content                                                            |
| -------- | ------------------------------------------------------------------ |
| 0–5      | White pieces (Pawn=0, Knight=1, Bishop=2, Rook=3, Queen=4, King=5) |
| 6–11     | Black pieces (same order, offset by 6)                             |
| 12       | Side to move (1 = White, 0 = Black) — full plane                   |
| 13       | White kingside castling rights — full plane                        |
| 14       | White queenside castling rights — full plane                       |
| 15       | Black kingside castling rights — full plane                        |
| 16       | Black queenside castling rights — full plane                       |

#### Confidence-Based Selection

The model outputs are post-processed by a `select_by_confidence` function:

```python
def select_by_confidence(inputs):
    score, checkmate = inputs
    threshold = 15000.0
    use_checkmate = tf.abs(checkmate) > threshold
    return tf.where(use_checkmate, checkmate, score)
```

This suggests the saved model (`model_combined.keras`) has **dual output heads**:

- A **score head** for standard centipawn evaluation
- A **checkmate head** for mate detection

If the checkmate head outputs an absolute value > 15,000, its output is trusted; otherwise the score head is used.

#### CombinedEngine Inference

**Class**: `CombinedEngine` (in `eval_tactic_model.py`)

Provides two inference modes:

1. **Direct Evaluation** (`get_best_move`): Evaluates each legal move by applying the model to the resulting position. Selects the move with the highest (White) or lowest (Black) evaluation.

2. **Minimax + Model** (`get_best_move_minimax`): Uses the CNN model as the leaf evaluation function within a minimax tree search, making it a hybrid search-and-learn approach.

---

### 4.6 Sequence-to-Move Model (chessEval3) — WIP

**File**: `backend/chessEval3/notes.txt` + `backend/chessEval3/trainer.py`

This is a **research/work-in-progress** module exploring a fundamentally different approach: **predicting the best move directly from the move history**, rather than evaluating board positions.

#### Concept

- **Input**: Last N moves + side to move
- **Output**: Best next move (classification over a move vocabulary)
- **Training data**: Only moves from the **winning side** of completed games
- **Dataset**: `games.csv` from Lichess (~7.6 MB, columns include `rated`, `winner`, `moves`, ratings, etc.)

#### Proposed Architecture (from notes)

```
Input: (samples, 5, 1) — 4 move tokens + turn indicator
    │
Conv1D(64, kernel=2, ReLU)
    │
Conv1D(64, kernel=2, ReLU)
    │
Flatten
    │
Dense(128, ReLU) → Dropout(0.3) → Dense(vocab_size, softmax)
```

#### Status

- `trainer.py` contains only data exploration code (reading and printing CSV columns).
- `notes.txt` contains the full design plan but no runnable training code.
- Suggested future improvements: Embedding layers, LSTMs, Transformers, longer sequence lengths.

---

### 4.7 Stockfish Integration

**File**: `backend/server.py` (in `StockfishGame()`)

The Stockfish endpoint is currently **commented out / stubbed**. When complete, it would:

1. Open a UCI engine process at the configured path
2. Set skill level to 1 (easy)
3. Request a move with a 0.5 second time limit
4. Return the move in UCI format

The `STOCKFISH_PATH` is hardcoded for Windows; it must be updated for the target OS.

---

## 5. Data Pipeline

### 5.1 Board Representation — 13-Channel Tensor (chessEval1)

**Function**: `fen_to_tensor(fen)` in `NN_training.py` / `CNN_only_training.py`

Converts a FEN string to a `(13, 8, 8)` float32 tensor:

| Channel | Content                                       |
| ------- | --------------------------------------------- |
| 0       | White Pawns (binary: 1 where present)         |
| 1       | White Knights                                 |
| 2       | White Bishops                                 |
| 3       | White Rooks                                   |
| 4       | White Queens                                  |
| 5       | White King                                    |
| 6       | Black Pawns                                   |
| 7       | Black Knights                                 |
| 8       | Black Bishops                                 |
| 9       | Black Rooks                                   |
| 10      | Black Queens                                  |
| 11      | Black King                                    |
| 12      | Metadata: en passant square + castling rights |

**Additional scalar features returned:**

- `active_player`: 1 (White) or 0 (Black)
- `halfmove_clock`: normalized by dividing by 100

#### En Passant Encoding

If an en passant target square exists, the corresponding cell in channel 12 is set to 1.

#### Castling Rights Encoding

Castling rights are encoded at fixed positions in channel 12:

| Right               | Position (row, col) |
| ------------------- | ------------------- |
| K (White kingside)  | (7, 6)              |
| Q (White queenside) | (7, 2)              |
| k (Black kingside)  | (0, 6)              |
| q (Black queenside) | (0, 2)              |

### 5.2 Board Representation — 17-Channel Tensor (chessEval2)

**Function**: `board_to_tensor(board)` in `chessEval2/training.py`

A **(8, 8, 17)** int8 tensor with piece-type channels plus full-plane game state. See [Section 4.5](#45-combined-evaluation-model-chesseval2) for channel breakdown.

Key difference from Eval1: castling and side-to-move information are encoded as **full 8×8 planes** rather than single cells, giving the network access to this information at every spatial position.

### 5.3 Data Loading & Preprocessing

**Function**: `load_data(csv_path, sample_size)` in `NN_training.py` / `CNN_only_training.py`

1. **Load CSV** — reads a CSV with columns `FEN` and `Evaluation`
2. **Sample** — randomly selects `sample_size` rows (default 1,000; training used up to 1M)
3. **Encode board** — converts each FEN to tensor representation
4. **Parse evaluation** — handles two formats:
    - Standard centipawn: `"150"` → `150.0`
    - Checkmate notation: `"#3"` → `10,000.0` / `"#-3"` → `-10,000.0`
5. **Output** — NumPy arrays: `(boards, active_players, halfmove_clocks, evaluations)`

### 5.4 Training Pipeline

```
CSV (FEN + Evaluation)
    │
    ▼
load_data()  →  (boards, players, clocks, evals)
    │
    ▼
tf.data.Dataset.from_tensor_slices()
    │
    ▼
.shuffle(buffer_size=2048) → .batch(BATCH_SIZE)
    │
    ▼
model.compile(optimizer=Adam(ExponentialDecay), loss='mse')
    │
    ▼
model.fit(epochs=EPOCHS, callbacks=[LossHistory, ModelCheckpoint])
    │
    ▼
model.save('models/{timestamp}.keras')
```

---

## 6. Frontend Architecture

### 6.1 Component Hierarchy

```
<Provider store={store}>
  └── <App>
        ├── Sidebar (desktop only, d-none d-md-block)
        │   ├── Avatar + Title
        │   ├── Difficulty buttons (Easy/Medium/Hard)
        │   ├── Time control buttons (3/5/10 min)
        │   ├── Color selector (White/Black)
        │   ├── AI Model dropdown
        │   └── Start button
        │
        ├── Main Area
        │   └── <ChessBoard>
        │         ├── <RemotePlayer>  ← AI info bar (avatar, timer, captures)
        │         ├── <Chessboard>    ← react-chessboard (drag & drop)
        │         └── <LocalPlayer>   ← Human controls (play/pause, undo, redo, timer)
        │               └── <PieceIcon>  ← Captured piece icons
        │
        └── Bottom Nav (fixed)
              ├── Game tab
              ├── Stats tab (placeholder)
              ├── Info tab (placeholder)
              └── Theme tab (placeholder)
```

### 6.2 State Management (Redux)

The application uses **Redux Toolkit** with two slices:

#### `chessSlice` — Game State

| State Key       | Type      | Description                                                         |
| --------------- | --------- | ------------------------------------------------------------------- |
| `gameFen`       | `string`  | Current board position in FEN notation                              |
| `gamePgn`       | `string`  | Full game in PGN notation                                           |
| `undoStack`     | `array`   | Stack of undone moves for redo functionality                        |
| `timer`         | `{w, b}`  | Per-side countdown timers (seconds)                                 |
| `lastMove`      | `object`  | Last move played                                                    |
| `gameOver`      | `boolean` | Whether the game has ended                                          |
| `gameStatus`    | `string`  | `"Inactive"` or `"Active"`                                          |
| `gameHistory`   | `array`   | Array of all serialized moves played                                |
| `selectedModel` | `string`  | Currently selected AI: `"Minimax"`, `"CNN1 + VTT Evaluation"`, etc. |
| `userColor`     | `string`  | `"w"` or `"b"`                                                      |
| `loading`       | `boolean` | Set during async AI move computation                                |
| `error`         | `string`  | Error message from failed AI calls                                  |

**Synchronous Reducers:**

- `makeMove` — updates FEN, PGN, history; manages undo/redo stacks
- `setSelectedModel` — changes AI engine
- `setUserColor` — changes player color
- `setGameStatus` — toggles Active/Inactive
- `resetGame` — restores initial state
- `setTime` — decrements the active player's clock

**Async Thunks** (one per AI engine):

- `minimaxMove` — calls `/chess/minimax/play`
- `CNN1Move` — calls `/chess/model/CNN1+VTT/play`
- `CNN2Move` — calls `/chess/model/CNN2/play`
- `stockFishMove` — calls `/chess/model/stockfish/play`

Each thunk: fetches the move → reconstructs the game from PGN → applies the move → serializes and returns the new state.

#### `themeSlice` — Theme State

| State Key | Type     | Description                   |
| --------- | -------- | ----------------------------- |
| `theme`   | `string` | `"auto"`, `"light"`, `"dark"` |

### 6.3 Game Flow

```
┌──────────┐    User drags     ┌──────────────┐
│  Start   │───piece to move──▶│  onDrop()    │
│  Button  │                   │  validates   │
│ (Active) │                   │  with chess.js│
└──────────┘                   └──────┬───────┘
                                      │ dispatch(makeMove)
                                      ▼
                               ┌──────────────┐
                               │ Redux Store  │
                               │ updates FEN  │
                               └──────┬───────┘
                                      │ useEffect detects turn !== localColor
                                      ▼
                               ┌──────────────┐
                               │ dispatch(    │
                               │ [model]Move) │
                               │ async thunk  │
                               └──────┬───────┘
                                      │ POST /chess/{model}/play
                                      ▼
                               ┌──────────────┐
                               │  Backend AI  │
                               │  computes    │
                               │  best move   │
                               └──────┬───────┘
                                      │ { move: "e7e5" }
                                      ▼
                               ┌──────────────┐
                               │ Redux Store  │
                               │ updates FEN  │
                               │ re-renders   │
                               │ board        │
                               └──────────────┘
```

### 6.4 UI/UX Features

#### Interactive Board

- **Drag and drop** piece movement with validation via `chess.js`
- **Legal move highlighting**: Green overlay on valid target squares when hovering a piece
- **Check highlighting**: Red overlay on the king's square when in check
- **Board orientation**: Flips based on selected color

#### Player Panels

- **Local Player** (bottom): Play/Pause, Undo, Redo, Hint (placeholder), Reset, Resign + timer + captured pieces
- **Remote Player** (top): AI avatar + name + timer + captured pieces

#### Material Advantage

- Computes captured pieces by comparing current board against the starting position
- Displays individual captured piece icons using FontAwesome chess icons
- Shows numerical advantage difference (e.g., "+3")

#### Timer

- 5-minute countdown per side (default)
- Decrements every second for the active player
- Timer pauses when game status is `"Inactive"`

#### Custom Board Theme

- Light squares: pure white `#ffffff`
- Dark squares: crosshatch pattern via CSS `repeating-linear-gradient`

---

## 7. Communication Protocol

### Request/Response Cycle

```
Frontend                          Backend
   │                                 │
   │  POST /chess/{engine}/play      │
   │  { "fen": "rnbq..." }          │
   │────────────────────────────────▶│
   │                                 │
   │  { "move": "e2e4",             │
   │    "status": "Active" }        │
   │◀────────────────────────────────│
   │                                 │
```

### Move Representation

Moves are communicated in **UCI notation** (e.g., `e2e4`, `e7e8q` for promotion). The frontend's `chess.js` library converts these to its internal move format.

### Serialized Move Object (Redux)

Each move stored in the Redux history is serialized as:

```json
{
	"color": "w",
	"from": "e2",
	"to": "e4",
	"piece": "p",
	"san": "e4",
	"flags": "b",
	"captured": null,
	"promotion": null
}
```

---

## 8. Future Work & Known Limitations

### Known Limitations

| Issue                                                   | Details                                                          |
| ------------------------------------------------------- | ---------------------------------------------------------------- |
| Stockfish endpoint is stubbed                           | Engine initialization is commented out; returns a string literal |
| CNN2+Minimax endpoint is stubbed                        | Returns a string instead of computed move                        |
| No en passant in Eval1 tensor when using CNN-only model | En passant and castling share channel 12                         |
| Hardcoded API URL                                       | Frontend thunks use `http://127.0.0.1:4090`                      |
| No move validation on backend                           | Server trusts the FEN string from the client                     |
| Difficulty/time controls are UI-only                    | Easy/Medium/Hard and 3/5/10 min buttons are not wired to logic   |
| Model files not in repo                                 | `.keras` files are gitignored; must be trained separately        |

### Potential Improvements

- **Environment variables** for API URL, Stockfish path, and model paths
- **WebSocket** connection for real-time play instead of polling-like POST requests
- **Opening book** integration for strong early game play
- **Endgame tablebases** (e.g., Syzygy) for perfect endgame play
- **Iterative deepening** for Minimax with time-bounded search
- **NNUE-style incremental evaluation** for faster neural network inference
- **chessEval3 completion**: Train the sequence-to-move model; explore LSTM / Transformer architectures
- **Game persistence**: Save/load games to a database
- **Multiplayer**: WebSocket-based human-vs-human play
- **Mobile-first redesign**: Improve the bottom nav into a full mobile experience
