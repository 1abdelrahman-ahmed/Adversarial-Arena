# ⚫⚪ Othello / Reversi

**🧠 An adversarial board game with AI-powered agents**  
_A strategic implementation of the classic Othello (Reversi) game using adversarial search algorithms_

---

## 📋 Game Overview

Othello (also known as Reversi) is a two-player, turn-based board game played on an **8×8 grid**.  
Players alternate turns placing pieces on the board with the goal of **capturing opponent pieces** by flanking them in straight lines.

This implementation is part of the **Adversarial Arena** project and focuses on combining  
**clean game logic**, **AI decision-making**, and **multiple interaction modes**.

---

## 🧩 How the Game Works

### 🔹 Board & Pieces
- Board size: **8×8**
- Black (`@`) always starts first
- White (`O`) plays second

---

### 🔹 Valid Moves
- A move is valid only if it flips at least one opponent piece
- Flips can occur:
  - Horizontally
  - Vertically
  - Diagonally

---

### 🔹 Turn Rules
- Players alternate turns
- If a player has **no valid moves**, their turn is automatically skipped
- The game ends when **both players have no valid moves**

---

### 🔹 Win Condition
- The game ends by counting the total number of pieces
- The player with the higher count wins
- Equal counts result in a draw

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

The AI player is implemented using **classical adversarial search techniques**:

- **Minimax Algorithm**
- **Alpha-Beta Pruning** for optimization
- **Heuristic Evaluation Function** based on:
  - Positional weighting (heatmap)
  - Board control
- Configurable search depth (default: `depth = 4`)

The AI evaluates board states strategically rather than greedily, prioritizing stable and high-value positions such as corners.

---

## 🗂 Folder Structure

```

Othello/
├── ai.py            # Minimax + Alpha-Beta AI logic            # [In Progress]
├── board.py         # Board representation and game rules      # [In Progress]
├── cell.py          # Cell abstraction                         # [In Progress]
├── constants.py     # shared constants & config                # [In Progress]
├── gui.py           # PyQt5 graphical interface                # [In Progress]
├── main.py          # Terminal-based game entry point          # [In Progress]
├── player.py        # Human and AI player logic                # [In Progress]
└── README.md        # Game documentation                       # [In Progress]

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
python gui.py
```

Features:

* Click-based gameplay
* Visual hints for legal moves
* Real-time score display
* Select Human or AI for each player

---

### ⌨️ Terminal Version

Run:

```bash
python main.py
```

Instructions:

* Choose player type (Human / AI) for each color
* Enter moves as: `row col` (example: `3 4`)
* Enter `q` to quit the game

---

## 🧪 Example (Terminal)

```
Turn: Black (@)
Available moves marked with *
Enter move (row col): 3 4

AI (White) plays: (4, 5)

Game over!
Final score:
Black (@): 34
White (O): 30
Winner: Black (@)
```

---

## 🎯 Learning Objectives

This module is designed to help practice:

* Adversarial search algorithms
* Game state representation
* Heuristic design
* Object-Oriented Programming
* Separation of logic, AI, and UI layers

---

## 📦 Part of a Larger Project

This game is a **submodule** of the **Adversarial Arena** project,
which aims to collect and compare multiple adversarial board games under a unified AI-driven framework.

---

## 📜 License

Open-source and free to use for **learning, experimentation, and academic purposes**.