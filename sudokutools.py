#!/usr/bin/env python3

from random import randint, shuffle

def generate_board():
    board = [[0 for _ in range(9)] for _ in range(9)]

    for i in range(0, 9, 3):
        num = list(range(1, 10))
        shuffle(num)
        for row in range(3):
            for col in range(3):
                board[i + row][i + col] = num.pop()

    def fill_cells(board, row, col):
        if row == 9:
            return True
        if col == 9:
            return fill_cells(board, row + 1, 0)
        if board[row][col] != 0:
            return fill_cells(board, row, col + 1)

        for num in range(1, 10):
            if valid(board, (row, col), num):
                board[row][col] = num

                if fill_cells(board, row, col + 1):
                    return True
        board[row][col] = 0
        return False

    fill_cells(board, 0, 0)

    for _ in range(randint(55, 65)):
        row, col = randint(0, 8), randint(0, 8)
        board[row][col] = 0

    return board

def print_board(board):
    board_string = ""
    for i in range(9):
        for j in range(9):
            board_string += str(board[i][j]) + " "
            if (j + 1) % 3 == 0 and j != 0 and j + 1 != 9:
                board_string += "| "
            if j == 8:
                board_string += "\n"
            if j == 8 and (i + 1) % 3 == 0 and i + 1 != 9:
                board_string += "- - - - - - - - - - - \n"
    print(board_string)

def find_empty(board):
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                return (i, j)
    return None

def valid(board, pos, num):
    for i in range(9):
        if board[i][pos[1]] == num:
            return False

    for j in range(9):
        if board[pos[0]][j] == num:
            return False

    start_i = pos[0] - pos[0] % 3
    start_j = pos[1] - pos[1] % 3

    for i in range(3):
        for j in range(3):
            if board[start_i + i][start_j + j] == num:
                return False

    return True

def solve(board):
    # Pre-compute empty cells
    empty_cells = [(i, j) for i in range(9) for j in range(9) if board[i][j] == 0]
    
    def solve_helper(index):
        # If we've filled all empty cells, we're done
        if index >= len(empty_cells):
            return True
            
        row, col = empty_cells[index]
        for num in range(1, 10):
            if valid(board, (row, col), num):
                board[row][col] = num
                if solve_helper(index + 1):
                    return True
                board[row][col] = 0
                
        return False
    
    return solve_helper(0)

if __name__ == "__main__":
    board = generate_board()
    print_board(board)
    solve(board)
    print_board(board)
