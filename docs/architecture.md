**HUMAN REVIEW REQUIRED**

**Status**: [APPROVED]

To approve, change status to: [APPROVED]
To reject, change status to: [REJECTED]

---

# Architecture Document: Simple Chess Game POC

**Version**: v1.0.0
**Last Updated**: 2026-01-15

## 1. System Architecture Overview

### 1.1 Architecture Style
**Client-Side Single-Page Application**
- No backend server required
- All logic runs in browser
- No external dependencies or frameworks

### 1.2 High-Level Architecture
```
┌─────────────────────────────────────────┐
│         Browser Environment             │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │       index.html (View)           │ │
│  │  - Board rendering                │ │
│  │  - UI controls                    │ │
│  └───────────┬───────────────────────┘ │
│              │                          │
│  ┌───────────▼───────────────────────┐ │
│  │      styles.css (Styling)         │ │
│  │  - Board/piece appearance         │ │
│  │  - Responsive layout              │ │
│  └───────────────────────────────────┘ │
│              │                          │
│  ┌───────────▼───────────────────────┐ │
│  │     game.js (Controller)          │ │
│  │  - Event handlers                 │ │
│  │  - DOM manipulation               │ │
│  └───────────┬───────────────────────┘ │
│              │                          │
│  ┌───────────▼───────────────────────┐ │
│  │    chess-engine.js (Model)        │ │
│  │  - Game state                     │ │
│  │  - Move validation                │ │
│  │  - Chess rules logic              │ │
│  └───────────────────────────────────┘ │
│                                         │
└─────────────────────────────────────────┘
```

## 2. Component Architecture

### 2.1 Module Breakdown

#### Module 1: HTML View (`index.html`)
**Responsibility**: Structure and presentation layer
```html
<div id="game-container">
  <header>
    <h1>Simple Chess Game</h1>
    <div id="game-status"></div>
  </header>
  <div id="chess-board"></div>
  <button id="new-game-btn">New Game</button>
</div>
```

**Key Elements**:
- `#chess-board`: 8x8 grid container
- `.square`: Individual board squares (64 elements)
- `.piece`: Chess piece elements with data attributes
- `#game-status`: Display turn/check/checkmate status

#### Module 2: Styling (`styles.css`)
**Responsibility**: Visual appearance
- Grid layout for board
- Square colors (light/dark alternating)
- Piece styling (Unicode symbols)
- Highlight states (selected, valid moves)

#### Module 3: Game Controller (`game.js`)
**Responsibility**: User interaction and view updates
```javascript
class GameController {
  constructor(chessEngine);
  initBoard();
  handleSquareClick(file, rank);
  updateDisplay();
  highlightValidMoves(piece);
  resetGame();
}
```

**Key Functions**:
- `initBoard()`: Create board DOM elements
- `handleSquareClick()`: Process player clicks
- `updateDisplay()`: Sync DOM with game state
- `highlightValidMoves()`: Show valid move indicators

#### Module 4: Chess Engine (`chess-engine.js`)
**Responsibility**: Game logic and state management
```javascript
class ChessEngine {
  constructor();
  initializeBoard();
  isValidMove(from, to);
  makeMove(from, to);
  getValidMoves(piece);
  isInCheck(color);
  isCheckmate(color);
  isStalemate(color);
}
```

**Key Functions**:
- `initializeBoard()`: Set up starting position
- `isValidMove()`: Validate move legality
- `makeMove()`: Execute move and update state
- `getValidMoves()`: Calculate legal moves for piece
- `isInCheck()`: Detect check condition
- `isCheckmate()`: Detect checkmate
- `isStalemate()`: Detect stalemate

## 3. Data Models

### 3.1 Board Representation
```javascript
// 8x8 array: board[rank][file]
// rank 0 = 1st rank (white), rank 7 = 8th rank (black)
// file 0 = a-file, file 7 = h-file
board = [
  [Piece, Piece, ...], // Rank 1
  [...],               // Rank 2
  ...
  [...]                // Rank 8
]
```

### 3.2 Piece Model
```javascript
class Piece {
  constructor(type, color, position) {
    this.type = type;     // 'pawn', 'rook', 'knight', 'bishop', 'queen', 'king'
    this.color = color;   // 'white', 'black'
    this.position = {     // Current position
      file: 0-7,          // a-h (0-7)
      rank: 0-7           // 1-8 (0-7)
    };
    this.hasMoved = false; // For castling/pawn rules
  }

  getUnicodeSymbol() {
    // Returns appropriate Unicode chess symbol
  }
}
```

### 3.3 Game State Model
```javascript
class GameState {
  constructor() {
    this.board = [];           // 8x8 array
    this.currentTurn = 'white'; // 'white' or 'black'
    this.status = 'normal';    // 'normal', 'check', 'checkmate', 'stalemate'
    this.moveHistory = [];     // Array of moves
    this.selectedPiece = null; // Currently selected piece
    this.enPassantTarget = null; // Valid en passant square
  }
}
```

### 3.4 Move Model
```javascript
class Move {
  constructor(from, to, piece, capturedPiece, specialMove) {
    this.from = {file, rank};
    this.to = {file, rank};
    this.piece = piece;
    this.capturedPiece = capturedPiece || null;
    this.specialMove = specialMove || null; // 'castling', 'enPassant', 'promotion'
  }
}
```

## 4. Key Algorithms

### 4.1 Move Validation Algorithm
```
function isValidMove(piece, from, to):
  1. Check basic movement pattern for piece type
  2. Check path is clear (no pieces blocking)
  3. Check destination is empty or contains enemy piece
  4. Simulate move
  5. Check if own king would be in check
  6. If check, return false
  7. Return true
```

### 4.2 Check Detection Algorithm
```
function isInCheck(color):
  1. Find king of given color
  2. For each opponent piece:
     a. Get all valid moves (without check validation)
     b. If any move targets king position:
        Return true
  3. Return false
```

### 4.3 Checkmate Detection Algorithm
```
function isCheckmate(color):
  1. If not in check, return false
  2. For each piece of given color:
     a. Get all valid moves
     b. For each valid move:
        - Simulate move
        - If no longer in check, return false
  3. Return true (no moves escape check)
```

### 4.4 Valid Move Generation
```
function getValidMoves(piece):
  1. Generate all possible moves based on piece type:
     - Pawn: forward 1-2, diagonal captures
     - Rook: horizontal/vertical lines
     - Knight: L-shaped jumps
     - Bishop: diagonal lines
     - Queen: horizontal/vertical/diagonal lines
     - King: 1 square any direction + castling
  2. Filter out moves blocked by pieces
  3. Filter out moves that leave king in check
  4. Return valid moves array
```

## 5. API Specifications (Internal)

### 5.1 ChessEngine Public API
```javascript
// Initialize new game
chessEngine.initializeBoard(): void

// Get piece at position
chessEngine.getPieceAt(file, rank): Piece | null

// Validate move
chessEngine.isValidMove(from, to): boolean

// Execute move
chessEngine.makeMove(from, to): Move | null

// Get valid moves for piece
chessEngine.getValidMoves(file, rank): Array<{file, rank}>

// Get current game state
chessEngine.getCurrentTurn(): 'white' | 'black'
chessEngine.getStatus(): 'normal' | 'check' | 'checkmate' | 'stalemate'

// Check game conditions
chessEngine.isInCheck(color): boolean
chessEngine.isCheckmate(color): boolean
chessEngine.isStalemate(color): boolean
```

### 5.2 GameController Public API
```javascript
// Initialize game
gameController.init(): void

// Reset to new game
gameController.resetGame(): void

// Handle user input
gameController.handleSquareClick(file, rank): void

// Update display
gameController.render(): void
```

## 6. Data Flow

### 6.1 Move Execution Flow
```
1. User clicks square
   ↓
2. GameController.handleSquareClick()
   ↓
3. If no piece selected:
   - Select piece
   - Get valid moves from ChessEngine
   - Highlight valid moves in DOM
   ↓
4. If piece selected and valid move:
   - Call ChessEngine.makeMove()
   - Update game state
   - Check for check/checkmate/stalemate
   - Switch turn
   - Update DOM
   - Clear selection
```

### 6.2 Game State Update Flow
```
makeMove(from, to)
   ↓
Update board array
   ↓
Update piece position
   ↓
Check special moves (castling, en passant)
   ↓
Add to move history
   ↓
Switch current turn
   ↓
Check game status (check, checkmate, stalemate)
   ↓
Emit state change event
   ↓
GameController updates DOM
```

## 7. File Structure

```
chess-game/
├── index.html          # Main HTML file
├── styles.css          # Styling
├── js/
│   ├── game.js         # Game controller
│   ├── chess-engine.js # Chess logic
│   └── pieces.js       # Piece definitions
└── README.md           # Project documentation
```

## 8. Deployment Architecture

### 8.1 Hosting
- Static file hosting (GitHub Pages, Netlify, Vercel, or local file://)
- No server-side processing required
- No build process needed

### 8.2 Browser Requirements
- ES6+ JavaScript support
- CSS Grid support
- Modern DOM APIs

## 9. Performance Considerations

### 9.1 Optimization Strategies
- Use event delegation for square clicks (single listener on board)
- Cache valid moves instead of recalculating
- Use CSS classes for highlights instead of inline styles
- Minimize DOM manipulations (batch updates)

### 9.2 Performance Targets
- Initial render: < 100ms
- Move validation: < 10ms
- Move execution: < 50ms
- UI update after move: < 50ms

## 10. Security Considerations

### 10.1 Client-Side Security
- No user data stored
- No external API calls
- No authentication required
- No XSS risk (no user-generated content)

## 11. Error Handling

### 11.1 Error Types
- Invalid move attempts: Silently ignore or show feedback
- Invalid board state: Log to console, allow game reset
- DOM element not found: Fail gracefully with console error

### 11.2 Error Recovery
- All errors should allow "New Game" button to reset
- No errors should crash the application
- Console logging for debugging

## 12. Testing Strategy

### 12.1 Unit Testing (Optional for POC)
- Test move validation logic
- Test check detection
- Test checkmate detection

### 12.2 Manual Testing Scenarios
- Complete a full game
- Test all piece movements
- Test castling (both sides)
- Test en passant
- Test check/checkmate detection
- Test stalemate detection

## 13. Extensibility Points

### 13.1 Future Extensions
- Add AI opponent (new module: `ai-engine.js`)
- Add move history UI (new component in HTML)
- Add save/load (use localStorage)
- Add timer/clock (new module: `timer.js`)
- Add animations (enhance CSS/JS)

### 13.2 Extension Guidelines
- Keep chess-engine.js pure logic (no DOM)
- Extend GameController for new UI features
- Add new modules instead of modifying existing ones
