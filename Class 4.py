import random

grid = [1,2,3,4,5,6,7,8,9]

def showboard():

    RED = "\033[91m"
    BLUE = "\033[94m"
    RESET = "\033[0m"

    def color(value):

        if value == "X":
            return RED + "X" + RESET

        if value == "O":
            return BLUE + "O" + RESET

        return str(value)

    print("")

    print(f" {color(grid[0])} | {color(grid[1])} | {color(grid[2])}")
    print("---+---+---")
    print(f" {color(grid[3])} | {color(grid[4])} | {color(grid[5])}")
    print("---+---+---")
    print(f" {color(grid[6])} | {color(grid[7])} | {color(grid[8])}")

    print("")

def checkwinner(board):

    winning_combinations = [
        [0,1,2],
        [3,4,5],
        [6,7,8],
        [0,3,6],
        [1,4,7],
        [2,5,8],
        [0,4,8],
        [2,4,6]
    ]

    for combo in winning_combinations:

        a, b, c = combo

        if board[a] == board[b] == board[c]:
            if board[a] == "X":
                return "X"

            if board[a] == "O":
                return "O"

    if all(space in ["X", "O"] for space in board):
        return "Draw"

    return None


def moveplayer():

    while True:

        try:
            move = int(input("Enter your move (1-9): ")) - 1

            if move < 0 or move > 8:
                print("Please enter a number from 1 to 9.")
                continue

            if grid[move] in ["X", "O"]:
                print("That square is already taken!")
                continue

            grid[move] = "X"
            break

        except ValueError:
            print("Please enter a number.")


def minimax(board, maximizing):

    result = checkwinner(board)

    # AI wins
    if result == "O":
        return 1

    # Player wins
    if result == "X":
        return -1

    # Draw
    if result == "Draw":
        return 0

    empty = []

    for i in range(9):

        if board[i] not in ["X", "O"]:
            empty.append(i)

    if maximizing:

        best_score = -100

        for move in empty:

            old = board[move]

            board[move] = "O"

            score = minimax(board, False)

            board[move] = old

            best_score = max(best_score, score)

        return best_score

    else:

        best_score = 100

        for move in empty:

            old = board[move]

            board[move] = "X"

            score = minimax(board, True)

            board[move] = old

            best_score = min(best_score, score)

        return best_score


def moveai():

    best_score = -100
    best_move = None

    for i in range(9):

        if grid[i] not in ["X", "O"]:

            old = grid[i]

            grid[i] = "O"

            score = minimax(grid, False)

            grid[i] = old

            if score > best_score:

                best_score = score
                best_move = i

    grid[best_move] = "O"


def game():

    print("TIC TAC TOE")
    print("You are X")
    print("AI is O")

    showboard()

    while True:

        # Player's turn
        moveplayer()

        showboard()

        result = checkwinner(grid)

        if result == "X":
            print("You win!")
            break

        if result == "Draw":
            print("It's a draw!")
            break

        # AI's turn
        print("AI is thinking...")

        moveai()

        showboard()

        result = checkwinner(grid)

        if result == "O":
            print("AI wins!")
            break

        if result == "Draw":
            print("It's a draw!")
            break


game()