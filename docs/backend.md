**HUMAN REVIEW REQUIRED**

**Status**: [APPROVED]

To approve, change status to: [APPROVED]
To reject, change status to: [REJECTED]

---

# Backend Implementation Plan: Simple Chess Game POC

**Version**: v1.0.0
**Last Updated**: 2026-01-15

## 1. Overview

**Note**: This is a **frontend-only** application with no traditional backend server. This document describes the "backend logic" that runs client-side in JavaScript.

### 1.1 Architecture Decision
- **No Server**: All logic runs in browser
- **No API**: No HTTP requests
- **No Database**: Game state in memory only
- **No Authentication**: Local two-player only

### 1.2 Backend Components (Client-Side)
All "backend" logic is implemented in client-side JavaScript:
- `chess-engine.js`: Game state and rules engine
- `pieces.js`: Data models for chess pieces

## 2. Game State Management

### 2.1 State Structure
```javascript
class GameState {
  constructor() {
    this.board = [];              // 8x8 2D array of Piece objects
    this.currentTurn = 'white';   // 'white' | 'black'
    this.status = 'normal';       // 'normal' | 'check' | 'checkmate' | 'stalemate'
    this.moveHistory = [];        // Array of Move objects
    this.enPassantTarget = null;  // {file, rank} | null
    this.castlingRights = {       // Track castling availability
      white: { kingSide: true, queenSide: true },
      black: { kingSide: true, queenSide: true }
    };
  }
}
```

### 2.2 Board Initialization
```javascript
initializeBoard() {
  // Create empty 8x8 board
  this.board = Array(8).fill(null).map(() => Array(8).fill(null));

  // Place pawns
  for (let file = 0; file < 8; file++) {
    this.board[1][file] = new Piece('pawn', 'white', {file, rank: 1});
    this.board[6][file] = new Piece('pawn', 'black', {file, rank: 6});
  }

  // Place back rank pieces
  const backRankSetup = ['rook', 'knight', 'bishop', 'queen', 'king', 'bishop', 'knight', 'rook'];
  backRankSetup.forEach((type, file) => {
    this.board[0][file] = new Piece(type, 'white', {file, rank: 0});
    this.board[7][file] = new Piece(type, 'black', {file, rank: 7});
  });

  this.currentTurn = 'white';
  this.status = 'normal';
  this.moveHistory = [];
  this.enPassantTarget = null;
}
```

## 3. Move Validation Logic

### 3.1 Main Validation Function
```javascript
isValidMove(from, to) {
  // 1. Get piece at source
  const piece = this.getPieceAt(from.file, from.rank);
  if (!piece) return false;

  // 2. Check it's the correct player's turn
  if (piece.color !== this.currentTurn) return false;

  // 3. Check destination is different from source
  if (from.file === to.file && from.rank === to.rank) return false;

  // 4. Check destination doesn't have own piece
  const targetPiece = this.getPieceAt(to.file, to.rank);
  if (targetPiece && targetPiece.color === piece.color) return false;

  // 5. Check move is valid for piece type
  if (!this.isValidMovePattern(piece, from, to)) return false;

  // 6. Check path is clear (except knights)
  if (piece.type !== 'knight' && !this.isPathClear(from, to)) return false;

  // 7. Simulate move and check if king is in check
  if (this.wouldBeInCheck(from, to, piece.color)) return false;

  return true;
}
```

### 3.2 Move Pattern Validation by Piece Type

#### Pawn Movement
```javascript
isValidPawnMove(piece, from, to) {
  const direction = piece.color === 'white' ? 1 : -1;
  const startRank = piece.color === 'white' ? 1 : 6;
  const fileDiff = to.file - from.file;
  const rankDiff = to.rank - from.rank;

  // Forward move (1 square)
  if (fileDiff === 0 && rankDiff === direction) {
    return this.getPieceAt(to.file, to.rank) === null;
  }

  // Forward move (2 squares from start)
  if (fileDiff === 0 && rankDiff === 2 * direction && from.rank === startRank) {
    const intermediateRank = from.rank + direction;
    return this.getPieceAt(to.file, to.rank) === null &&
           this.getPieceAt(from.file, intermediateRank) === null;
  }

  // Diagonal capture
  if (Math.abs(fileDiff) === 1 && rankDiff === direction) {
    const targetPiece = this.getPieceAt(to.file, to.rank);

    // Normal capture
    if (targetPiece && targetPiece.color !== piece.color) {
      return true;
    }

    // En passant
    if (this.enPassantTarget &&
        to.file === this.enPassantTarget.file &&
        to.rank === this.enPassantTarget.rank) {
      return true;
    }
  }

  return false;
}
```

#### Rook Movement
```javascript
isValidRookMove(piece, from, to) {
  // Must move along rank or file (not both)
  return (from.file === to.file) !== (from.rank === to.rank);
}
```

#### Knight Movement
```javascript
isValidKnightMove(piece, from, to) {
  const fileDiff = Math.abs(to.file - from.file);
  const rankDiff = Math.abs(to.rank - from.rank);

  // L-shape: 2+1 or 1+2
  return (fileDiff === 2 && rankDiff === 1) ||
         (fileDiff === 1 && rankDiff === 2);
}
```

#### Bishop Movement
```javascript
isValidBishopMove(piece, from, to) {
  const fileDiff = Math.abs(to.file - from.file);
  const rankDiff = Math.abs(to.rank - from.rank);

  // Must move diagonally (equal file and rank distance)
  return fileDiff === rankDiff && fileDiff > 0;
}
```

#### Queen Movement
```javascript
isValidQueenMove(piece, from, to) {
  // Queen moves like rook or bishop
  return this.isValidRookMove(piece, from, to) ||
         this.isValidBishopMove(piece, from, to);
}
```

#### King Movement
```javascript
isValidKingMove(piece, from, to) {
  const fileDiff = Math.abs(to.file - from.file);
  const rankDiff = Math.abs(to.rank - from.rank);

  // Normal move: 1 square in any direction
  if (fileDiff <= 1 && rankDiff <= 1) {
    return true;
  }

  // Castling: 2 squares horizontally
  if (rankDiff === 0 && fileDiff === 2 && !piece.hasMoved) {
    return this.canCastle(piece, from, to);
  }

  return false;
}
```

### 3.3 Path Clearance Check
```javascript
isPathClear(from, to) {
  const fileStep = Math.sign(to.file - from.file);
  const rankStep = Math.sign(to.rank - from.rank);

  let currentFile = from.file + fileStep;
  let currentRank = from.rank + rankStep;

  while (currentFile !== to.file || currentRank !== to.rank) {
    if (this.getPieceAt(currentFile, currentRank) !== null) {
      return false;
    }
    currentFile += fileStep;
    currentRank += rankStep;
  }

  return true;
}
```

## 4. Special Moves

### 4.1 Castling
```javascript
canCastle(king, from, to) {
  const color = king.color;
  const rank = from.rank;
  const isKingSide = to.file > from.file;
  const rookFile = isKingSide ? 7 : 0;

  // 1. Check castling rights
  if (isKingSide && !this.castlingRights[color].kingSide) return false;
  if (!isKingSide && !this.castlingRights[color].queenSide) return false;

  // 2. Check king hasn't moved
  if (king.hasMoved) return false;

  // 3. Check rook exists and hasn't moved
  const rook = this.getPieceAt(rookFile, rank);
  if (!rook || rook.type !== 'rook' || rook.hasMoved) return false;

  // 4. Check path is clear
  const direction = isKingSide ? 1 : -1;
  for (let file = from.file + direction; file !== rookFile; file += direction) {
    if (this.getPieceAt(file, rank) !== null) return false;
  }

  // 5. Check king is not in check
  if (this.isInCheck(color)) return false;

  // 6. Check king doesn't pass through check
  const passFile = from.file + direction;
  if (this.wouldBeInCheck(from, {file: passFile, rank}, color)) return false;

  // 7. Check king doesn't end in check
  if (this.wouldBeInCheck(from, to, color)) return false;

  return true;
}

executeCastling(kingFrom, kingTo) {
  const rank = kingFrom.rank;
  const isKingSide = kingTo.file > kingFrom.file;
  const rookFile = isKingSide ? 7 : 0;
  const rookToFile = isKingSide ? 5 : 3;

  // Move rook
  const rook = this.getPieceAt(rookFile, rank);
  this.board[rank][rookToFile] = rook;
  this.board[rank][rookFile] = null;
  rook.position = {file: rookToFile, rank};
  rook.hasMoved = true;
}
```

### 4.2 En Passant
```javascript
checkEnPassant(piece, from, to) {
  // Check if last move was 2-square pawn move
  if (this.moveHistory.length === 0) return;

  const lastMove = this.moveHistory[this.moveHistory.length - 1];
  const lastPiece = lastMove.piece;

  // Must be pawn moving 2 squares
  if (lastPiece.type !== 'pawn') {
    this.enPassantTarget = null;
    return;
  }

  const rankDiff = Math.abs(lastMove.to.rank - lastMove.from.rank);
  if (rankDiff === 2) {
    // Set en passant target square (the square the pawn passed over)
    const targetRank = (lastMove.from.rank + lastMove.to.rank) / 2;
    this.enPassantTarget = {file: lastMove.to.file, rank: targetRank};
  } else {
    this.enPassantTarget = null;
  }
}

executeEnPassant(from, to) {
  // Remove captured pawn (one rank behind target square)
  const capturedPawnRank = this.currentTurn === 'white' ? to.rank - 1 : to.rank + 1;
  this.board[capturedPawnRank][to.file] = null;
}
```

### 4.3 Pawn Promotion
```javascript
checkPromotion(piece, to) {
  if (piece.type !== 'pawn') return;

  const promotionRank = piece.color === 'white' ? 7 : 0;
  if (to.rank === promotionRank) {
    // Auto-promote to queen for POC
    piece.type = 'queen';
  }
}
```

## 5. Check and Checkmate Detection

### 5.1 Check Detection
```javascript
isInCheck(color) {
  const king = this.findKing(color);
  if (!king) return false;

  const opponentColor = color === 'white' ? 'black' : 'white';

  // Check if any opponent piece can attack the king
  for (let rank = 0; rank < 8; rank++) {
    for (let file = 0; file < 8; file++) {
      const piece = this.board[rank][file];
      if (piece && piece.color === opponentColor) {
        // Check if piece can move to king's position (without check validation)
        if (this.canAttack(piece, {file, rank}, king.position)) {
          return true;
        }
      }
    }
  }

  return false;
}

canAttack(piece, from, to) {
  // Check move pattern without checking for check (to avoid recursion)
  if (!this.isValidMovePattern(piece, from, to)) return false;

  if (piece.type !== 'knight' && !this.isPathClear(from, to)) return false;

  return true;
}
```

### 5.2 Checkmate Detection
```javascript
isCheckmate(color) {
  // Must be in check to be checkmate
  if (!this.isInCheck(color)) return false;

  // Check if any legal move exists
  return !this.hasLegalMoves(color);
}

hasLegalMoves(color) {
  for (let fromRank = 0; fromRank < 8; fromRank++) {
    for (let fromFile = 0; fromFile < 8; fromFile++) {
      const piece = this.board[fromRank][fromFile];
      if (piece && piece.color === color) {
        // Try all possible destinations
        for (let toRank = 0; toRank < 8; toRank++) {
          for (let toFile = 0; toFile < 8; toFile++) {
            if (this.isValidMove(
              {file: fromFile, rank: fromRank},
              {file: toFile, rank: toRank}
            )) {
              return true; // Found a legal move
            }
          }
        }
      }
    }
  }
  return false; // No legal moves
}
```

### 5.3 Stalemate Detection
```javascript
isStalemate(color) {
  // Must not be in check to be stalemate
  if (this.isInCheck(color)) return false;

  // Must have no legal moves
  return !this.hasLegalMoves(color);
}
```

### 5.4 Simulated Move for Check Validation
```javascript
wouldBeInCheck(from, to, color) {
  // Save current state
  const fromPiece = this.getPieceAt(from.file, from.rank);
  const toPiece = this.getPieceAt(to.file, to.rank);

  // Simulate move
  this.board[to.rank][to.file] = fromPiece;
  this.board[from.rank][from.file] = null;

  // Check if in check
  const inCheck = this.isInCheck(color);

  // Restore state
  this.board[from.rank][from.file] = fromPiece;
  this.board[to.rank][to.file] = toPiece;

  return inCheck;
}
```

## 6. Move Execution

### 6.1 Main Move Function
```javascript
makeMove(from, to) {
  if (!this.isValidMove(from, to)) {
    return null; // Invalid move
  }

  const piece = this.getPieceAt(from.file, from.rank);
  const capturedPiece = this.getPieceAt(to.file, to.rank);

  // Create move record
  const move = new Move(from, to, piece, capturedPiece);

  // Handle special moves
  if (piece.type === 'king' && Math.abs(to.file - from.file) === 2) {
    move.specialMove = 'castling';
    this.executeCastling(from, to);
  }

  if (piece.type === 'pawn' && to.file === this.enPassantTarget?.file &&
      to.rank === this.enPassantTarget?.rank) {
    move.specialMove = 'enPassant';
    this.executeEnPassant(from, to);
  }

  // Execute move
  this.board[to.rank][to.file] = piece;
  this.board[from.rank][from.file] = null;
  piece.position = {file: to.file, rank: to.rank};
  piece.hasMoved = true;

  // Check for pawn promotion
  this.checkPromotion(piece, to);

  // Update castling rights
  this.updateCastlingRights(piece, from);

  // Update en passant target
  this.checkEnPassant(piece, from, to);

  // Add to history
  this.moveHistory.push(move);

  // Switch turn
  this.switchTurn();

  // Update game status
  this.updateGameStatus();

  return move;
}
```

### 6.2 Game Status Update
```javascript
updateGameStatus() {
  const color = this.currentTurn;

  if (this.isCheckmate(color)) {
    this.status = 'checkmate';
  } else if (this.isStalemate(color)) {
    this.status = 'stalemate';
  } else if (this.isInCheck(color)) {
    this.status = 'check';
  } else {
    this.status = 'normal';
  }
}
```

## 7. Helper Functions

### 7.1 Board Queries
```javascript
getPieceAt(file, rank) {
  if (file < 0 || file > 7 || rank < 0 || rank > 7) {
    return null;
  }
  return this.board[rank][file];
}

findKing(color) {
  for (let rank = 0; rank < 8; rank++) {
    for (let file = 0; file < 8; file++) {
      const piece = this.board[rank][file];
      if (piece && piece.type === 'king' && piece.color === color) {
        return piece;
      }
    }
  }
  return null;
}

getAllPieces(color) {
  const pieces = [];
  for (let rank = 0; rank < 8; rank++) {
    for (let file = 0; file < 8; file++) {
      const piece = this.board[rank][file];
      if (piece && piece.color === color) {
        pieces.push({piece, position: {file, rank}});
      }
    }
  }
  return pieces;
}
```

### 7.2 Turn Management
```javascript
switchTurn() {
  this.currentTurn = this.currentTurn === 'white' ? 'black' : 'white';
}

getCurrentTurn() {
  return this.currentTurn;
}

getStatus() {
  return this.status;
}
```

### 7.3 Valid Moves Generation
```javascript
getValidMoves(file, rank) {
  const piece = this.getPieceAt(file, rank);
  if (!piece || piece.color !== this.currentTurn) {
    return [];
  }

  const validMoves = [];

  // Try all possible destinations
  for (let toRank = 0; toRank < 8; toRank++) {
    for (let toFile = 0; toFile < 8; toFile++) {
      if (this.isValidMove({file, rank}, {file: toFile, rank: toRank})) {
        validMoves.push({file: toFile, rank: toRank});
      }
    }
  }

  return validMoves;
}
```

## 8. Data Models

### 8.1 Piece Model
```javascript
class Piece {
  constructor(type, color, position) {
    this.type = type;       // 'pawn', 'rook', 'knight', 'bishop', 'queen', 'king'
    this.color = color;     // 'white', 'black'
    this.position = position; // {file: 0-7, rank: 0-7}
    this.hasMoved = false;  // For castling and pawn rules
  }

  getUnicodeSymbol() {
    const symbols = {
      white: { king: '♔', queen: '♕', rook: '♖', bishop: '♗', knight: '♘', pawn: '♙' },
      black: { king: '♚', queen: '♛', rook: '♜', bishop: '♝', knight: '♞', pawn: '♟' }
    };
    return symbols[this.color][this.type];
  }

  clone() {
    const cloned = new Piece(this.type, this.color, {...this.position});
    cloned.hasMoved = this.hasMoved;
    return cloned;
  }
}
```

### 8.2 Move Model
```javascript
class Move {
  constructor(from, to, piece, capturedPiece = null, specialMove = null) {
    this.from = from;                   // {file, rank}
    this.to = to;                       // {file, rank}
    this.piece = piece.clone();         // Clone of moved piece
    this.capturedPiece = capturedPiece ? capturedPiece.clone() : null;
    this.specialMove = specialMove;     // 'castling', 'enPassant', 'promotion', null
    this.timestamp = Date.now();
  }

  toAlgebraic() {
    // Convert to algebraic notation (future enhancement)
    const files = 'abcdefgh';
    return `${files[this.from.file]}${this.from.rank + 1}${files[this.to.file]}${this.to.rank + 1}`;
  }
}
```

## 9. Testing Strategy

### 9.1 Unit Test Cases
```javascript
// Example test cases for move validation
testPawnMove() {
  // Test single square forward
  // Test double square from start
  // Test diagonal capture
  // Test en passant
}

testCheckDetection() {
  // Setup board with king in check
  // Verify isInCheck returns true
}

testCheckmateDetection() {
  // Setup Scholar's Mate position
  // Verify isCheckmate returns true
}

testCastling() {
  // Test kingside castling
  // Test queenside castling
  // Test castling blocked by piece
  // Test castling through check
}
```

### 9.2 Integration Tests
- Complete game playthrough
- Special move scenarios
- Edge cases (promotion, stalemate)

## 10. Performance Considerations

### 10.1 Optimization Strategies
- Cache valid moves during piece selection
- Lazy evaluation of check/checkmate (only when needed)
- Efficient board representation (2D array)
- Minimize object cloning

### 10.2 Performance Targets
- Move validation: < 10ms
- Check detection: < 20ms
- Checkmate detection: < 100ms

## 11. Future Backend Enhancements

### 11.1 Server-Side Features (Future)
If a backend server is added later:
- **REST API** for online multiplayer
- **WebSocket** for real-time moves
- **Database** for game history and user accounts
- **AI Engine** for computer opponent

### 11.2 Possible Tech Stack
- Node.js + Express
- Socket.io for real-time
- MongoDB/PostgreSQL for persistence
- Redis for game sessions

## 12. Conclusion

This "backend" is entirely client-side JavaScript implementing the chess game logic. It's designed to be:
- **Independent**: No DOM dependencies (pure logic)
- **Testable**: Can be unit tested without browser
- **Extensible**: Can be reused if server is added later
- **Efficient**: Fast enough for real-time gameplay
