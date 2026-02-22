import { useState, useEffect, useRef } from "react";
import { Chess } from "chess.js";
import {
  Chessboard,
  defaultDarkSquareStyle,
  defaultLightSquareStyle,
} from "react-chessboard";
import { useDispatch, useSelector } from "react-redux";
import {
  minimaxMove,
  makeMove,
  stockFishMove,
  CNN1Move,
  CNN2Move,
  setTime,
} from "../store/chessSlice";
import RemotePlayer from "./players/remotePlayer";
import LocalPlayer from "./players/localPlayer";
import { getCapturedPieces } from "../utils/chessBoard_utils";

const ChessBoard = () => {
  const dispatch = useDispatch();
  const gameFen = useSelector((state) => state.chess.gameFen);
  const gamePgn = useSelector((state) => state.chess.gamePgn);
  const undoStack = useSelector((state) => state.chess.undoStack);
  const localColor = useSelector((state) => state.chess.userColor);
  const gameStatus = useSelector((state) => state.chess.gameStatus);
  const selectedModel = useSelector((state) => state.chess.selectedModel);
  const storedTheme = useSelector((state) => state.theme.theme);
  const [game, setGame] = useState(new Chess(gameFen));
  const [squareStyles, setSquareStyles] = useState({});
  const [checkSquareStyle, setCheckSquareStyle] = useState({});
  const [whiteCaptures, setWhiteCaptures] = useState({});
  const [blackCaptures, setBlackCaptures] = useState({});
  const [advantageVal, setAdvantageVal] = useState({});
  const whiteTime = useSelector((state) => state.chess.timer.w);
  const blackTime = useSelector((state) => state.chess.timer.b);

  useEffect(() => {
    if (gameFen) {
      const newGame = new Chess(gameFen);
      // newGame.loadPgn(gamePgn);
      // console.log(newGame.history())
      setGame(newGame);
    }
  }, [gameFen]);

  const timerRef = useRef(null);

  const currentTurn = game.turn(); // "w" or "b"
  useEffect(() => {
    clearInterval(timerRef.current);

    timerRef.current = setInterval(() => {
      if (gameStatus === "Active") {
        if (currentTurn === "w") {
          if (whiteTime === 1) return;
          dispatch(setTime({ w: whiteTime }));
        } else {
          if (blackTime === 1) return;
          dispatch(setTime({ b: blackTime }));
        }
      }
    }, 1000);

    if (game.isCheck()) {
      const newSquareStyles = {};
      const attackedKing = game.findPiece({ type: "k", color: currentTurn });

      newSquareStyles[attackedKing] = {
        backgroundColor: "rgba(200, 0, 0, 0.5)",
      };
      setSquareStyles(newSquareStyles);
      setCheckSquareStyle(newSquareStyles);
    } else {
      setCheckSquareStyle({});
    }

    if ((currentTurn !== localColor) & (gameStatus === "Active")) {
      if (selectedModel === "Minimax") {
        dispatch(minimaxMove());
      } else if (selectedModel === "Stockfish") {
        dispatch(stockFishMove());
      } else if (selectedModel === "CNN1 + VTT Evaluation") {
        dispatch(CNN1Move());
      } else if (selectedModel === "CNN2 Evaluation") {
        dispatch(CNN2Move());
      }
    }
    return () => clearInterval(timerRef.current);
  }, [currentTurn, gameStatus]);

  const onLiftUp = ({ square }) => {
    if (square) {
      const getLegalMoves = (square) => {
        return game.moves({ square, verbose: true }).map((move) => move.to);
      };
      const legalMoves = getLegalMoves(square);
      if (legalMoves.length === 0) {
        setSquareStyles(game.isCheck() ? checkSquareStyle : {});
        return;
      }
      const newSquareStyles = game.isCheck() ? checkSquareStyle : {};
      // src square
      if (game.findPiece({ type: "k", color: currentTurn }) !== square) {
        newSquareStyles[square] = {
          backgroundColor: "rgba(0, 0, 200, 0.3)",
        };
      }

      // target square
      legalMoves.forEach((destSquare) => {
        newSquareStyles[destSquare] = {
          backgroundColor: "rgba(0, 200, 0, 0.4)",
        };
      });

      setSquareStyles(newSquareStyles);
    }
  };

  const onDrop = async (sourceSquare, targetSquare) => {
    const from = sourceSquare?.sourceSquare;
    const to = sourceSquare?.targetSquare;
    if (from === to) {
      setSquareStyles({});
      const newSquareStyles = game.isCheck() ? checkSquareStyle : {};
      if (game.findPiece({ type: "k", color: currentTurn }) !== from) {
        newSquareStyles[from] = {
          backgroundColor: "rgba(0, 0, 200, 0.3)",
        };
      }
      setSquareStyles(newSquareStyles);
      return false;
    }

    const newGame = game; //new Chess(game.fen());
    const move = newGame.move({
      from: from,
      to: to,
      promotion: "q", // promote to queen
    });
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

    if (move) {
      // console.log(newGame.pgn({ maxWidth: 5,  }));
      dispatch(
        makeMove({
          fen: newGame.fen(),
          pgn: newGame.pgn(),
          move: serializedMove,
        })
      );
      setGame(newGame);
      setSquareStyles(game.isCheck() ? checkSquareStyle : {});
      return true;
    }
    return false;
  };
  const canDragPiece = ({ piece }) => {
    return piece.pieceType[0] === game.turn() && game.turn() === localColor;
  };

  const handleUndoMove = () => {
    if (game) {
      const newGame = game; //new Chess(game.fen());
      const move = newGame.undo();
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

      if (move) {
        // console.log(newGame.pgn({ maxWidth: 5,  }));
        dispatch(
          makeMove({
            fen: newGame.fen(),
            pgn: newGame.pgn(),
            move: serializedMove,
            undoMove: serializedMove,
          })
        );
        setGame(newGame);
        setSquareStyles(game.isCheck() ? checkSquareStyle : {});
        return true;
      }
      return false;
    }
  };

  const handleRedoMove = () => {
    if (undoStack.length === 0) {
      return false;
    }
    if (game) {
      const newGame = game; //new Chess(game.fen());
      let undoStackCopy = [...undoStack];
      // console.log(undoStackCopy.pop());
      const redoMove = undoStackCopy.length > 0 ? undoStackCopy.pop() : null;
      const move = newGame.move({
        from: redoMove?.from,
        to: redoMove?.to,
        promotion: "q", // promote to queen
      });
      const serializedMove = {
        color: move?.color,
        from: move?.from,
        to: move?.to,
        piece: move?.piece,
        san: move?.san,
        flags: move?.flags,
        captured: move?.captured || null,
        promotion: move?.promotion || null,
      };

      if (move) {
        console.log(move);
        dispatch(
          makeMove({
            fen: newGame.fen(),
            pgn: newGame.pgn(),
            move: serializedMove,
            redoMove: serializedMove,
          })
        );
        setGame(newGame);
        setSquareStyles(game.isCheck() ? checkSquareStyle : {});
        return true;
      }
      return false;
    }
  };

  const chessboardOptions = {
    onPieceDrop: onDrop,
    canDragPiece,
    onPieceDrag: onLiftUp,
    squareStyles,
    position: game.fen(),
    darkSquareStyle: {
      backgroundImage: `repeating-linear-gradient(135deg, #999da3  0, #999da3  0.8px, transparent 0, transparent 50%)`,
      backgroundSize: `8px 8px`,
      backgroundColor: `#ffffff`,
    },
    lightSquareStyle: { background: "#ffffff" },
    boardOrientation: localColor === "w" ? "white" : "black",
  };

  useEffect(() => {
    let { captured, advantage } = getCapturedPieces(game);
    setWhiteCaptures(captured.w);
    setBlackCaptures(captured.b);
    setAdvantageVal(advantage);
  }, [game]);

  return (
    <div>
      <RemotePlayer
        isRemoteTurn={currentTurn !== localColor}
        localColor={localColor}
        captures={localColor === "b" ? whiteCaptures : blackCaptures}
        advantage={advantageVal}
        theme={storedTheme}
      />
      <Chessboard options={chessboardOptions} />
      <LocalPlayer
        isLocalTurn={currentTurn === localColor}
        localColor={localColor}
        captures={localColor === "w" ? whiteCaptures : blackCaptures}
        advantage={advantageVal}
        handleUndoMove={handleUndoMove}
        handleRedoMove={handleRedoMove}
      />
    </div>
  );
};

export default ChessBoard;
