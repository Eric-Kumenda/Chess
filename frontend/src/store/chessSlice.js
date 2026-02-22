import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { Chess } from "chess.js";

export const minimaxMove = createAsyncThunk(
  "chess/minimaxMove",
  async (_, { getState, rejectWithValue }) => {
    const { gameFen, gamePgn } = getState().chess;
    try {
      const res = await fetch("http://127.0.0.1:4090/chess/minimax/play", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ fen: gameFen }),
      });

      const data = await res.json();
      if (!data.move) throw new Error("No move returned from AI");

      const aiGame = new Chess();
      aiGame.loadPgn(gamePgn);
      const aiMove = data.move;
      const move = aiGame.move(aiMove);
      const status = data.status;
      const serializedMove = {
        color: move.color,
        from: move.from,
        to: move.to,
        piece: move.piece,
        san: move.san,
        flags: move.flags,
        captured: move.captured || null,
        promotion: move.promotion || null,
      };

      return {
        fen: aiGame.fen(),
        pgn: aiGame.pgn(),
        status: status,
        move: serializedMove,
      };
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const CNN1Move = createAsyncThunk(
  "chess/CNN1Move",
  async (_, { getState, rejectWithValue }) => {
    const { gameFen, gamePgn } = getState().chess;
    try {
      const res = await fetch(
        "http://127.0.0.1:4090/chess/model/CNN1+VTT/play",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ fen: gameFen }),
        }
      );

      const data = await res.json();
      if (!data.move) throw new Error("No move returned from AI");

      const aiGame = new Chess();
      aiGame.loadPgn(gamePgn);
      const aiMove = data.move;
      const move = aiGame.move(aiMove);
      const status = data.status;
      const serializedMove = {
        color: move.color,
        from: move.from,
        to: move.to,
        piece: move.piece,
        san: move.san,
        flags: move.flags,
        captured: move.captured || null,
        promotion: move.promotion || null,
      };

      return {
        fen: aiGame.fen(),
        pgn: aiGame.pgn(),
        status: status,
        move: serializedMove,
      };
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);
export const CNN2Move = createAsyncThunk(
  "chess/CNN2Move",
  async (_, { getState, rejectWithValue }) => {
    const { gameFen, gamePgn } = getState().chess;
    try {
      const res = await fetch("http://127.0.0.1:4090/chess/model/CNN2/play", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ fen: gameFen }),
      });

      const data = await res.json();
      if (!data.move) throw new Error("No move returned from AI");

      const aiGame = new Chess();
      aiGame.loadPgn(gamePgn);
      const aiMove = data.move;
      const move = aiGame.move(aiMove);
      const status = data.status;
      const serializedMove = {
        color: move.color,
        from: move.from,
        to: move.to,
        piece: move.piece,
        san: move.san,
        flags: move.flags,
        captured: move.captured || null,
        promotion: move.promotion || null,
      };

      return {
        fen: aiGame.fen(),
        pgn: aiGame.pgn(),
        status: status,
        move: serializedMove,
      };
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const stockFishMove = createAsyncThunk(
  "chess/stockFishMove",
  async (_, { getState, rejectWithValue }) => {
    const { gameFen, gamePgn } = getState().chess;
    try {
      const res = await fetch(
        "http://127.0.0.1:4090/chess/model/stockfish/play",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ fen: gameFen }),
        }
      );

      const data = await res.json();
      if (!data.move) throw new Error("No move returned from AI");

      const aiGame = new Chess();
      aiGame.loadPgn(gamePgn);
      const aiMove = data.move;
      const move = aiGame.move(aiMove);
      const status = data.status;
      const serializedMove = {
        color: move.color,
        from: move.from,
        to: move.to,
        piece: move.piece,
        san: move.san,
        flags: move.flags,
        captured: move.captured || null,
        promotion: move.promotion || null,
      };

      return {
        fen: aiGame.fen(),
        pgn: aiGame.pgn(),
        status: status,
        move: serializedMove,
      };
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

const initialState = {
  gameFen: new Chess().fen(),
  gamePgn: new Chess().pgn(),
  undoStack: [],
  timer: { w: 300, b: 300 },
  lastMove: null,
  gameOver: false,
  gameStatus: "Inactive",
  gameHistory: [],
  selectedModel: "Minimax",
  userColor: "w",
};

const chessSlice = createSlice({
  name: "chess",
  initialState,
  reducers: {
    makeMove: (state, action) => {
      state.gameFen = action.payload.fen;
      state.gamePgn = action.payload.pgn;
      state.gameHistory.push(action.payload.move);
      action.payload?.undoMove
        ? state.undoStack.push(action.payload.undoMove)
        : null;
      action.payload?.redoMove ? state.undoStack.pop() : null;
    },
    setSelectedModel: (state, action) => {
      state.selectedModel = action.payload;
    },
    setUserColor: (state, action) => {
      state.userColor = action.payload;
    },
    setGameStatus: (state, action) => {
      state.gameStatus = action.payload;
    },
    resetGame: (state, action) => {
      state.gameFen = new Chess().fen();
      state.gamePgn = new Chess().pgn();
      state.undoStack = [];
      state.gameStatus = "Inactive";
      state.gameHistory = [];
    },
    setTime: (state, action) => {
      state.timer.w = action.payload.w? action.payload.w - 1 : state.timer.w;
      state.timer.b = action.payload.b? action.payload.b - 1 : state.timer.b;
    },
  },

  extraReducers: (builder) => {
    builder
      .addCase(minimaxMove.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(minimaxMove.fulfilled, (state, action) => {
        state.loading = false;
        state.gameFen = action.payload.fen;
        state.gamePgn = action.payload.pgn;
        state.gameHistory.push(action.payload.move);
        state.gameStatus = action.payload.status;
      })
      .addCase(minimaxMove.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(CNN1Move.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(CNN1Move.fulfilled, (state, action) => {
        state.loading = false;
        state.gameFen = action.payload.fen;
        state.gamePgn = action.payload.pgn;
        state.gameHistory.push(action.payload.move);
        state.gameStatus = action.payload.status;
      })
      .addCase(CNN1Move.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(CNN2Move.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(CNN2Move.fulfilled, (state, action) => {
        state.loading = false;
        state.gameFen = action.payload.fen;
        state.gamePgn = action.payload.pgn;
        state.gameHistory.push(action.payload.move);
        state.gameStatus = action.payload.status;
      })
      .addCase(CNN2Move.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      .addCase(stockFishMove.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(stockFishMove.fulfilled, (state, action) => {
        state.loading = false;
        state.gameFen = action.payload.fen;
        state.gamePgn = action.payload.pgn;
        state.gameHistory.push(action.payload.move);
        state.gameStatus = action.payload.status;
      })
      .addCase(stockFishMove.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const {
  makeMove,
  setSelectedModel,
  setUserColor,
  setGameStatus,
  resetGame,
  setTime,
} = chessSlice.actions;
export default chessSlice.reducer;
