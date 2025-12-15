# ♟️ Chess AI Engine

**🧠 An adversarial board game powered by classical AI search algorithms**  
_A complete implementation of the game of Chess with intelligent AI agents, supporting both CLI and GUI gameplay_

---

## 📋 Game Overview

Chess is a two-player, turn-based strategy board game played on an **8×8 grid**.  
Players alternate turns moving pieces with the objective of **checkmating the opponent’s king**.

This project is part of the **Adversarial Arena** initiative and focuses on building a
**clean chess engine**, **strong AI decision-making**, and **multiple interaction modes**
using a well-structured Object-Oriented design.

---

## 🧩 How the Game Works

### 🔹 Board & Pieces
- Board size: **8×8**
- White (`w`) always moves first
- Black (`b`) plays second
- Standard chess pieces:
  - Pawn, Knight, Bishop, Rook, Queen, King

---

### 🔹 Valid Moves
- All standard chess rules are supported:
  - Legal move validation
  - Captures
  - Castling (King-side & Queen-side)
  - En-passant
  - Pawn promotion

---

### 🔹 Turn Rules
- Players alternate turns
- Illegal moves are rejected
- The game detects:
  - Check
  - Checkmate
  - Stalemate

---

### 🔹 Draw Conditions
The game automatically detects draws by:
- Threefold repetition
- Fifty-move rule
- Insufficient material

---

## 🎮 Game Modes

- Human vs Human  
- Human vs AI  
- AI vs AI  

The game can be played in:
- **Terminal (CLI)**
- **Graphical User Interface (PyQt5)**

---

## 🤖 AI Implementation

The AI player is built using **classical adversarial search techniques**:

- **Minimax Algorithm**
- **Alpha-Beta Pruning** for performance optimization
- **Quiescence Search** to reduce horizon effects
- **Transposition Table (Zobrist Hashing)**

### 🔍 Evaluation Function
The AI evaluates board positions using:
- Material values
- Piece-Square Tables (positional heatmaps)
- Bishop pair bonus
- Repetition penalties
- King safety (implicitly via search)

Search depth is configurable (default: `depth = 3`).

---

## 🗂 Project Structure

```

Chess/
├── assets/          # Assets folder for images and sounds
├── ai.py            # AI engine (Minimax, Alpha-Beta, evaluation)
├── board.py         # Board representation and chess rules
├── chess_gui.py     # PyQt5 graphical user interface
├── constants.py     # Shared constants and evaluation tables
├── main.py          # Terminal-based (CLI) entry point
├── moves.py         # Move parsing and formatting utilities
├── pieces.py        # Piece utilities and asset mapping
├── player.py        # Player abstraction (human / AI)
├── zobrist.py       # Zobrist hashing for position repetition
└── README.md        # Project documentation

````

---

## ▶️ How to Run

### 🖥️ GUI Version (Recommended)

Install dependencies:

```bash
pip install PyQt5
````

Run the game:

```bash
python chess_gui.py
```

Features:

* Click-based gameplay
* Legal move highlighting
* Promotion dialog
* Sound effects (optional)
* Multiple game modes

---

### ⌨️ Terminal (CLI) Version

Run:

```bash
python main.py
```

Instructions:

* Enter moves using **UCI format** (example: `e2e4`)
* Promotion example: `e7e8q`
* Enter `q` to quit the game

---

## 🧪 Example (Terminal)

```
White to move
Enter move: e2e4

Black AI is thinking...
Black plays: c7c5

White to move
Enter move: g1f3
```

---

## 🎯 Learning Objectives

This project is designed to practice and demonstrate:

* Adversarial search algorithms
* Game state representation
* Heuristic evaluation design
* Object-Oriented Programming (OOP)
* Clean separation between game logic, AI, and UI
* CLI and GUI coexistence over the same core engine

---

## 📦 Part of a Larger Project

This game is a **core module** of the **Adversarial Arena** project,
which aims to collect and compare multiple adversarial board games
under a unified AI experimentation framework.

---

## 📜 License

Open-source and free to use for **learning, experimentation, and academic purposes**.