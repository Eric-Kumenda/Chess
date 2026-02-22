import React, { useEffect } from "react";
import PieceIcon from "./PieceIcon";
import { CButton } from "@coreui/react";
import { useDispatch, useSelector } from "react-redux";
import { resetGame, setGameStatus } from "../../store/chessSlice";
import { formatTime } from "../../utils/chessBoard_utils";
const LocalPlayer = ({
  isLocalTurn,
  localColor,
  captures,
  advantage,
  handleUndoMove,
  handleRedoMove,
}) => {
  const whiteTime = useSelector((state) => state.chess.timer.w);
  const blackTime = useSelector((state) => state.chess.timer.b);
  const dispatch = useDispatch();
  const gameStatus = useSelector((state) => state.chess.gameStatus);
  const undoStack = useSelector((state) => state.chess.undoStack);
  const localAdvantage = advantage?.[localColor] || 0;
  const opponentColor = localColor === "w" ? "b" : "w";
  const opponentAdvantage = advantage?.[opponentColor] || 0;

  const showAdvantage = localAdvantage > opponentAdvantage;
  const advantageDiff = showAdvantage ? localAdvantage - opponentAdvantage : 0;
  const localTime = formatTime(localColor === "w" ? whiteTime : blackTime);

  const handleGameStatusChange = () => {
    if (gameStatus === "Inactive") {
      dispatch(setGameStatus("Active"));
    } else {
      dispatch(setGameStatus("Inactive"));
    }
  };

  const handleGameReset = () => {
    dispatch(resetGame());
  };
  return (
    <div className="row mt-2">
      <div className="col col-auto">
        <CButton size="sm" onClick={handleGameStatusChange} key={gameStatus}>
          <i
            className={`fa-regular fa-${
              gameStatus === "Inactive" ? "play" : "pause"
            }`}
          ></i>
        </CButton>
        <CButton size="sm" onClick={handleUndoMove}>
          <i className="fa-regular fa-angle-left"></i>
        </CButton>
        <CButton
          size="sm"
          onClick={undoStack.length > 1 ? handleRedoMove : null}
          disabled={undoStack.length < 1}
        >
          <i className="fa-regular fa-angle-right"></i>
        </CButton>
        <CButton size="sm">
          <i className="fa-regular fa-lightbulb-on"></i>
        </CButton>
        <CButton size="sm" onClick={handleGameReset}>
          <i className="fa-regular fa-arrow-rotate-right"></i>
        </CButton>
        <CButton size="sm">
          <i className="fa-regular fa-xmark"></i>
        </CButton>
      </div>
      <div className="col d-flex justify-content-end">
        {showAdvantage ? "+" + advantageDiff : ""}
        <div className="d-flex ms-2" style={{ gap: "2px" }}>
          {captures &&
            Object.entries(captures).map(([piece, count]) => (
              <span key={piece} className="mx-0 p-0">
                {Array.from({ length: count }).map((_, i) => (
                  <PieceIcon
                    key={i}
                    piece={piece}
                    pieceColor={localColor === "w" ? "b" : "w"}
                  />
                ))}
              </span>
            ))}
        </div>
        <button
          className={`btn btn-sm rounded bg-${
            isLocalTurn
              ? "success"
              : localColor === "w"
              ? "white text-bg-light"
              : "black text-bg-dark"
          } border ms-2 fs-5`}
          type="button"
        >
          {localTime}
        </button>
      </div>
    </div>
  );
};

export default LocalPlayer;
