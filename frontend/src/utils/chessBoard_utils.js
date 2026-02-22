import { Chess } from "chess.js";

export const getCapturedPieces = (game) => {
  const fullSet = {
    w: [
      "P",
      "P",
      "P",
      "P",
      "P",
      "P",
      "P",
      "P",
      "R",
      "R",
      "N",
      "N",
      "B",
      "B",
      "Q",
      "K",
    ],
    b: [
      "p",
      "p",
      "p",
      "p",
      "p",
      "p",
      "p",
      "p",
      "r",
      "r",
      "n",
      "n",
      "b",
      "b",
      "q",
      "k",
    ],
  };

  const currentPieces = game.board();

  // Count current pieces on board
  const current = { w: [], b: [] };
  for (const row of currentPieces) {
    for (const square of row) {
      if (square) {
        current[square.color].push(square.type);
      }
    }
  }

  // Function to count frequency of each piece type
  const countPieces = (arr) =>
    arr.reduce((acc, piece) => {
      acc[piece] = (acc[piece] || 0) + 1;
      return acc;
    }, {});

  const startingCounts = {
    w: countPieces(fullSet.w.map((p) => p.toLowerCase())),
    b: countPieces(fullSet.b.map((p) => p.toLowerCase())),
  };

  const currentCounts = {
    w: countPieces(current.w),
    b: countPieces(current.b),
  };

  const captured = { w: {}, b: {} };
  // Define piece values for advantage calculation
  const pieceValue = {
    p: 1,
    n: 3,
    b: 3,
    r: 5,
    q: 9,
    k: 0,
  };

  // Initialize advantage points
  const advantage = { w: 0, b: 0 };

  // Compare starting vs current to get captures
  ["w", "b"].forEach((color) => {
    const opponent = color === "w" ? "b" : "w";
    for (const piece in startingCounts[opponent]) {
      const startCount = startingCounts[opponent][piece] || 0;
      const currentCount = currentCounts[opponent][piece] || 0;
      const capturedCount = startCount - currentCount;
      if (capturedCount > 0) {
        captured[color][piece] = capturedCount;
        advantage[color] += (pieceValue[piece] || 0) * capturedCount;
      }
    }
  });
  // console.log(advantage);
  return { captured, advantage };
};

export const formatTime = (seconds) => {
    const m = Math.floor(seconds / 60)
      .toString()
      .padStart(2, "0");
    const s = (seconds % 60).toString().padStart(2, "0");
    return `${m}:${s}`;
  };
