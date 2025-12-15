# 🧠⚔️ Adversarial Arena

**🚀 A Game AI Experimentation Hub**  
_A growing collection of adversarial board games powered by classical AI search algorithms_

---

## 🗂 Project Structure

```

Adversarial-Arena/
├── images/                      
├── Othello/                     # [Complete]
├── Chess/                       # [Complete]
├── main_launcher.py             # [Complete]
│
├── (More games coming soon...)
│   ├── GoBang/                  # [Planned]
│
└── README.md                    # Project-level documentation

````

---

## 🌱 About This Project

**Adversarial Arena** is a long-term, academic-oriented project focused on designing and implementing  
**adversarial board games** using **Artificial Intelligence decision-making techniques**.

Each game in the arena is treated as an **independent module**, while sharing common architectural and conceptual foundations such as:

- Turn-based environments  
- Competing intelligent agents  
- Search-based decision making  
- Clear separation between game logic, AI logic, and user interface  

The project is designed to grow incrementally as new games and AI strategies are introduced.

---

## 🎮 Implemented Games

### 🟢 Othello / Reversi
- Human vs Human  
- Human vs AI  
- AI vs AI  
- Minimax with Alpha-Beta Pruning  
- Terminal-based and PyQt5 GUI implementations  

> Additional games will be integrated following the same architectural approach.

---

## 🤖 AI Focus

This repository emphasizes **classical Game AI techniques**, including:

- Minimax Search  
- Alpha-Beta Pruning  
- Heuristic Evaluation Functions  
- Positional Weighting (Board Heatmaps)  
- Terminal State Evaluation  
- Turn Skipping and Game-End Detection  

Different games may adopt different heuristics depending on their strategic complexity.

---

## 🎯 Project Objectives

- Apply **adversarial search algorithms** in practical scenarios  
- Build reusable and extensible **game engines**  
- Compare AI strategies across multiple games  
- Serve as a **learning-focused and portfolio-ready project**  
- Maintain clean, readable, and well-structured code  

---

## 🛠️ Tech Stack

Technologies currently used in this project:

- Python 3  
- PyQt5 (for GUI-based games)  
- Object-Oriented Programming  
- Classical AI search algorithms  

---

## 🖥 Running the Project & Graphical Interface

The project supports both **direct game execution** and a **unified modern launcher**.
Each game is implemented with its own GUI while sharing a common architectural style.

---

### 🔹 Option 1: Run a Specific Game Directly

```bash
git clone https://github.com/1abdelrahman-ahmed/Adversarial-Arena.git
cd Adversarial-Arena

# Example: run Othello directly
cd Othello
python othello_gui.py
````

> Each game directory contains its own **README** with detailed usage instructions
> and game-specific configuration options.

---

### 🔹 Option 2: Run Using the Unified Launcher (Recommended)

#### 1️⃣ Install dependencies

```bash
pip install pyqt5
```

#### 2️⃣ Run the launcher from the project root

```bash
python main_launcher.py
```

#### 3️⃣ Select a game

Choose between **Chess** or **Othello** from the launcher interface.

---

### 🎨 Graphical Interface Overview

* Built using **PyQt5**
* Unified modern launcher (`main_launcher.py`)
* Each game has its own dedicated GUI
* Designed for scalability and future game integration without refactoring

```

---

## 📜 License

This project is open-source and free to use for **learning, experimentation, and personal projects**.