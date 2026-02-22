import { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import { v4 as uuidv4 } from "uuid";

const PieceIcon = ({ piece, size = "1x", pieceColor }) => {
  const storedTheme = useSelector((state) => state.theme.theme);

  const isWhitePiece = pieceColor === "w";

  const [styleVariant, setStyleVariant] = useState(() => {
    return storedTheme === "dark"
      ? isWhitePiece
        ? "solid"
        : "regular"
      : isWhitePiece
      ? "regular"
      : "solid";
  });

  useEffect(() => {
    const newStyleVariant =
      storedTheme === "dark"
        ? isWhitePiece
          ? "solid"
          : "regular"
        : isWhitePiece
        ? "regular"
        : "solid";
    setStyleVariant(newStyleVariant); // Trigger state update when theme changes
    console.log("styleVariant updated:", newStyleVariant);
  }, [pieceColor]); // Trigger effect on storedTheme and pieceColor change

  const pieceMap = {
    p: "fa-chess-pawn",
    n: "fa-chess-knight",
    b: "fa-chess-bishop",
    r: "fa-chess-rook",
    q: "fa-chess-queen",
    k: "fa-chess-king",
  };

  const iconClass = pieceMap[piece.toLowerCase()];

  if (!iconClass) return null;

  const stableKey = `${piece}-${styleVariant}-${uuidv4()}`;

  return (
    <span key={stableKey}>
      <i className={`fa-${styleVariant} ${iconClass}`} />
    </span>
  );
};

export default PieceIcon;
