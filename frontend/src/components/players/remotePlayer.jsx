import React, { useEffect } from "react";
import { CAvatar } from "@coreui/react";
import PieceIcon from "./PieceIcon";
import { useSelector } from "react-redux";
import { formatTime } from "../../utils/chessBoard_utils";

const remoteAvatar = "../../assets/react.svg";

const RemotePlayer = ({
  isRemoteTurn,
  localColor,
  captures,
  advantage,
}) => {
  const whiteTime = useSelector((state) => state.chess.timer.w);
  const blackTime = useSelector((state) => state.chess.timer.b);
  const remoteColor = localColor === "w" ? "b" : "w";
  const remoteAdvantage = advantage?.[remoteColor] || 0;
  const opponentColor = localColor;
  const opponentAdvantage = advantage?.[opponentColor] || 0;

  const showAdvantage = remoteAdvantage > opponentAdvantage;
  const advantageDiff = showAdvantage ? remoteAdvantage - opponentAdvantage : 0;
  const remoteTime = formatTime(localColor === "w" ? blackTime : whiteTime);
  return (
    <div className="row mb-2">
      <div className="col col-auto">
        <CAvatar src={remoteAvatar} size="sm" className="me-2" />
        <span>Mt Model</span>
      </div>
      <div className="col d-flex justify-content-end">
        {showAdvantage ? "+" + advantageDiff : ""}
        <div className="d-flex ms-2" style={{ gap: "2px" }}>
          {captures &&
            Object.entries(captures).map(([piece, count]) => (
              <span key={piece} className="mx-0 p-0">
                {Array.from({ length: count }).map((_, i) => (
                  <PieceIcon key={i} piece={piece} pieceColor={localColor} />
                ))}
              </span>
            ))}
        </div>
        <button
          className={`btn btn-sm rounded bg-${
            isRemoteTurn
              ? "success"
              : localColor === "b"
              ? "white text-bg-light"
              : "black text-bg-dark"
          } border ms-2`}
          type="button"
        >
          {remoteTime}
        </button>
      </div>
    </div>
  );
};

export default RemotePlayer;
