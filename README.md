# ♟ Chessy — AI Chess Platform

A full-stack chess application featuring a **React** frontend and a **Python/Flask** backend with multiple AI engines — from classical Minimax with alpha-beta pruning to CNN and hybrid CNN+Vision Transformer deep-learning models.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Setup & Installation](#setup--installation)
    - [Backend](#backend-setup)
    - [Frontend](#frontend-setup)
- [Running the Application](#running-the-application)
- [AI Models](#ai-models)
- [API Reference](#api-reference)
- [Configuration](#configuration)
- [License](#license)

---

## Features

- **Interactive chessboard** with drag-and-drop piece movement
- **Multiple AI opponents** selectable from a dropdown:
    - Minimax (with alpha-beta pruning & transposition tables)
    - CNN + Vision Transformer hybrid evaluation model
    - CNN-only evaluation model
    - Stockfish integration (optional)
- **Game controls**: play/pause, undo/redo, reset
- **Chess clock** with per-side countdown timers (default 5 min)
- **Captured pieces** display with material advantage indicator
- **Color selection** — play as White or Black
- **Theme support** — light and dark modes via CoreUI
- **Responsive layout** — desktop sidebar + mobile-friendly bottom nav

---

## Tech Stack

| Layer    | Technology                                                            |
| -------- | --------------------------------------------------------------------- |
| Frontend | React 19, Vite 7, CoreUI 5, Redux Toolkit, chess.js, react-chessboard |
| Backend  | Python, Flask, Flask-CORS, python-chess                               |
| ML/AI    | TensorFlow / Keras (CNN, Vision Transformer)                          |
| Styling  | SCSS (CoreUI theming), FontAwesome 7 icons                            |
| Fonts    | Nunito (self-hosted TTF)                                              |

---

## Project Structure

```
Chess/
├── backend/
│   ├── main.py                 # Minimax AI engine (alpha-beta pruning)
│   ├── server.py               # Flask API server (all endpoints)
│   ├── requirements.txt        # Python dependencies
│   ├── .gitignore              # Ignores .keras models, __pycache__, models/
│   ├── chessEval1/             # Model v1 — CNN + Vision Transformer hybrid
│   │   ├── NN_training.py      # Hybrid CNN+ViT model definition & training
│   │   ├── CNN_only_training.py# Pure CNN model definition & training
│   │   ├── useModel.py         # Inference: load model & find best move
│   │   └── models/             # Saved .keras model files (gitignored)
│   ├── chessEval2/             # Model v2 — Combined evaluation model
│   │   ├── training.py         # Board-to-tensor encoding + model loading
│   │   ├── eval_tactic_model.py# CombinedEngine: inference + minimax search
│   │   └── models/             # Saved .keras model files (gitignored)
│   └── chessEval3/             # Model v3 — Sequence-to-move (WIP / research)
│       ├── notes.txt           # Design notes for CNN move-prediction model
│       ├── trainer.py          # Data exploration script for games.csv
│       └── games.csv           # Lichess game dataset (~7.6 MB)
│
└── frontend/
    ├── index.html              # HTML entry point (FontAwesome loaded)
    ├── package.json            # Node dependencies
    ├── vite.config.js          # Vite configuration
    ├── public/
    │   └── FontAwesome/        # Self-hosted FontAwesome 7 assets
    └── src/
        ├── main.jsx            # React entry point (Redux Provider)
        ├── App.jsx             # Main layout: sidebar + board + bottom nav
        ├── App.css             # Legacy grid styles
        ├── scss/
        │   └── style.scss      # CoreUI theme customization (colors, fonts)
        ├── store/
        │   ├── index.js        # Redux store configuration
        │   ├── chessSlice.js   # Game state, async thunks for AI moves
        │   └── themeSlice.js   # Theme state (light/dark/auto)
        ├── components/
        │   ├── ChessBoard.jsx  # Interactive board (drag, drop, highlights)
        │   ├── Selector.jsx    # Side selector (commented out / unused)
        │   ├── players/
        │   │   ├── localPlayer.jsx   # Local player UI (controls, timer, captures)
        │   │   ├── remotePlayer.jsx  # AI player UI (avatar, timer, captures)
        │   │   └── PieceIcon.jsx     # Chess piece icon component
        │   └── theme/
        │       ├── ThemeSwitch.jsx   # Dark/light toggle switch
        │       └── theme.css         # Theme switch styling
        └── utils/
            └── chessBoard_utils.js   # Captured pieces calc, time formatting
```

---

## Prerequisites

| Tool                       | Version | Notes                                               |
| -------------------------- | ------- | --------------------------------------------------- |
| **Python**                 | 3.10+   | Required for backend                                |
| **Node.js**                | 18+     | Required for frontend (npm included)                |
| **pip**                    | Latest  | Python package manager                              |
| **TensorFlow**             | 2.x     | Required to run neural network models               |
| _(Optional)_ **Stockfish** | Any     | External chess engine binary for Stockfish endpoint |

---

## Setup & Installation

### Backend Setup

1. **Clone the repository** and navigate to the backend:

    ```bash
    git clone https://github.com/Eric-Kumenda/Chess.git
    cd Chess/backend
    ```

2. **Create and activate a virtual environment** (recommended):

    ```bash
    python -m venv venv
    source venv/bin/activate    # Linux/macOS
    # venv\Scripts\activate     # Windows
    ```

3. **Install Python dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

4. **Install TensorFlow** (not listed in requirements.txt):

    ```bash
    pip install tensorflow
    ```

5. **Place trained model files** in the appropriate directories:
    - `backend/chessEval1/models/model.keras` — CNN+ViT hybrid model
    - `backend/chessEval2/models/model_combined.keras` — Combined evaluation model

    > [!IMPORTANT]
    > Model files (`.keras`) are gitignored. You must train them yourself using the training scripts or obtain them separately. Without these files, the CNN-based AI endpoints will fail on startup.

6. _(Optional)_ **Configure Stockfish**: Update the `STOCKFISH_PATH` variable in `server.py` to point to your local Stockfish binary:

    ```python
    STOCKFISH_PATH = r"/path/to/your/stockfish"
    ```

### Frontend Setup

1. **Navigate to the frontend directory**:

    ```bash
    cd Chess/frontend
    ```

2. **Install Node dependencies**:

    ```bash
    npm install
    ```

---

## Running the Application

### 1. Start the Backend Server

```bash
cd Chess/backend
python server.py
```

The Flask server starts on **`http://0.0.0.0:4090`** in debug mode.

### 2. Start the Frontend Dev Server

```bash
cd Chess/frontend
npm run dev
```

Vite serves the app on **`http://localhost:5173`** (default) with hot-module reload.

### 3. Play

Open the frontend URL in your browser, select an AI model from the dropdown, choose your color, and click **Start**.

---

## AI Models

| Model              | Endpoint Route                | Description                                                            |
| ------------------ | ----------------------------- | ---------------------------------------------------------------------- |
| **Random**         | `/chess/play`                 | Picks a random legal move (baseline)                                   |
| **Minimax**        | `/chess/minimax/play`         | Minimax search (depth 3) with alpha-beta pruning & transposition table |
| **CNN1 + ViT**     | `/chess/model/CNN1+VTT/play`  | Hybrid CNN + Vision Transformer board evaluation                       |
| **CNN2**           | `/chess/model/CNN2/play`      | Combined CNN model with confidence-based checkmate scoring             |
| **CNN2 + Minimax** | `/chess/model/2m/play`        | CNN2 evaluation with minimax lookahead (⚠ stub)                        |
| **Stockfish**      | `/chess/model/stockfish/play` | Stockfish engine integration (⚠ commented out / stub)                  |

---

## API Reference

All endpoints accept **POST** with JSON body `{ "fen": "<FEN string>" }` and return:

```json
{
	"move": "e2e4",
	"status": "Active"
}
```

| Method | Endpoint                      | Description         |
| ------ | ----------------------------- | ------------------- |
| POST   | `/chess/play`                 | Random move         |
| POST   | `/chess/minimax/play`         | Minimax AI move     |
| POST   | `/chess/model/CNN1+VTT/play`  | CNN1+ViT model move |
| POST   | `/chess/model/CNN2/play`      | CNN2 model move     |
| POST   | `/chess/model/2m/play`        | CNN2+minimax (stub) |
| POST   | `/chess/model/stockfish/play` | Stockfish (stub)    |

---

## Configuration

| Variable / File        | Location                           | Purpose                                       |
| ---------------------- | ---------------------------------- | --------------------------------------------- |
| `STOCKFISH_PATH`       | `backend/server.py`                | Path to Stockfish binary                      |
| Backend port           | `backend/server.py`                | Default: `4090`                               |
| API base URL           | `frontend/src/store/chessSlice.js` | Hardcoded to `http://127.0.0.1:4090`          |
| Timer duration         | `frontend/src/store/chessSlice.js` | Default: 300s (5 min) per side                |
| Search depth (Minimax) | `backend/server.py`                | `Chess_AI.find_best_move(board, 3)` — depth 3 |
| Theme colors           | `frontend/src/scss/style.scss`     | CoreUI SCSS variables                         |
| Font                   | `frontend/src/scss/style.scss`     | Nunito (self-hosted)                          |

---

## License

This project is currently unlicensed. Please add a `LICENSE` file to specify usage terms.
