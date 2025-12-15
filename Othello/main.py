from .constants import BLACK, WHITE, opponent
from .board import Board
from .ai import AI
from .player import Player


def ask_player_type(name: str) -> str:
    while True:
        print(f"Select type for {name}:")
        print("1) Human")
        print("2) AI")
        choice = input("Enter 1 or 2: ").strip()
        if choice == "1":
            return "human"
        if choice == "2":
            return "ai"
        print("Invalid choice. Please try again.\n")


def main():
    board = Board()
    ai_engine = AI(depth=4)

    print("Welcome to Othello / Reversi")
    print(f"Black = {BLACK}, White = {WHITE}\n")

    black_type = ask_player_type("Black (@)")
    white_type = ask_player_type("White (O)")
    print()

    black_player = Player(
        color=BLACK,
        kind=black_type,
        ai=ai_engine if black_type == "ai" else None,
        name="Black (@)",
    )
    white_player = Player(
        color=WHITE,
        kind=white_type,
        ai=ai_engine if white_type == "ai" else None,
        name="White (O)",
    )

    players = {
        BLACK: black_player,
        WHITE: white_player,
    }

    current_color = BLACK
    board.display()

    while not board.is_game_over():
        current_player = players[current_color]
        print(f"Turn: {current_player.name}")

        current_player.play_turn(board)
        board.display()

        current_color = opponent(current_color)

    print("Game over!")
    black_score = board.count_score(BLACK)
    white_score = board.count_score(WHITE)
    print(f"Final score - Black (@): {black_score}")
    print(f"Final score - White (O): {white_score}")

    winner = board.get_winner()
    if winner == BLACK:
        print("Winner: Black (@)")
    elif winner == WHITE:
        print("Winner: White (O)")
    else:
        print("Result: Draw")


if __name__ == "__main__":
    main()
