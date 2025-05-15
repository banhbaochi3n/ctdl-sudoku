#!/usr/bin/env python3

from sudokutools import *
from copy import deepcopy
from sys import exit
import pygame
import time
import random

pygame.init()

class Board:
    def __init__(self, window):
        self.board = generate_board()
        self.solved_board = deepcopy(self.board)
        solve(self.solved_board)
        self.tiles = [
            [Tile(self.board[i][j], window, i * 60, j * 60) for j in range(9)]
            for i in range(9)
        ]
        self.window = window

    def draw_board(self):
        for i in range(9):
            for j in range(9):
                # Draw vertical lines every three columns.
                if j % 3 == 0 and j != 0:
                    pygame.draw.line(
                        self.window,
                        (0, 0, 0),
                        (j // 3 * 180, 0),
                        (j // 3 * 180, 540),
                        4,
                    )
                # Draw horizontal lines every three rows.
                if i % 3 == 0 and i != 0:
                    pygame.draw.line(
                        self.window,
                        (0, 0, 0),
                        (0, i // 3 * 180),
                        (540, i // 3 * 180),
                        4,
                    )
                # Ve cac tile len board
                self.tiles[i][j].draw((0, 0, 0), 1)

                # Hien thi gia tri cua tile neu khac 0 (empty)
                if self.tiles[i][j].value != 0:
                    self.tiles[i][j].display(self.tiles[i][j].value, (21 + j * 60, 16 + i * 60), (0, 0, 0))

        # Draw a horizontal line at the bottom of the board.
        pygame.draw.line(
            self.window,
            (0, 0, 0),
            (0, (i + 1) // 3 * 180),
            (540, (i + 1) // 3 * 180),
            4,
        )

    def deselect(self, tile):
        for i in range(9):
            for j in range(9):
                if self.tiles[i][j] != tile:
                    self.tiles[i][j].selected = False

    def redraw(self, keys, wrong, time):
        self.window.fill((255, 255, 255))
        self.draw_board()
        for i in range(9):
            for j in range(9):
                if self.tiles[j][i].selected:
                    # highlight mau xanh la tile duoc chon
                    self.tiles[j][i].draw((50, 205, 50), 4)
                elif self.tiles[i][j].correct:
                    # highlight mau xanh la dam tile duoc chon
                    self.tiles[j][i].draw((34, 139, 34), 4)
                elif self.tiles[i][j].incorrect:
                    # highlight mau do tile sai
                    self.tiles[j][i].draw((255, 0, 0), 4)

                if len(keys) != 0:
                    for value in keys:
                        self.tiles[value[0]][value[1]].display(
                            keys[value],
                            (21 + value[0] * 60, 16 + value[1] * 60),
                            (128, 128, 128),
                        )

                if wrong > 0:
                    font = pygame.font.SysFont("Bauhaus 93", 30)
                    text = font.render("X", True, (255, 0, 0))
                    self.window.blit(text, (10, 554))

                    font = pygame.font.SysFont("Bahnschrift", 40)
                    text = font.render(str(wrong), True, (0, 0, 0))
                    self.window.blit(text, (32, 542))

                # Hien thi thoi gian
                font = pygame.font.SysFont("Bahnschrift", 40)
                text = font.render(str(time), True, (0, 0, 0))
                self.window.blit(text, (388, 542))
                pygame.display.flip()

    def visual_solve(self, wrong, time):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()  # exit the game if the user clicks the close button

        empty = find_empty(self.board)
        if not empty:
            return True  # the board is solved if there are no empty tiles left

        for nums in range(9):
            if valid(self.board, (empty[0], empty[1]), nums + 1):
                # fill in the current empty tile with a valid number
                self.board[empty[0]][empty[1]] = nums + 1
                self.tiles[empty[0]][empty[1]].value = nums + 1
                self.tiles[empty[0]][empty[1]].correct = True
                pygame.time.delay(63)  # delay to slow down the solving animation
                self.redraw({}, wrong, time)  # redraw the game window with the updated board

                if self.visual_solve(wrong, time):
                    return True  # recursively solve the rest of the board if the current move is valid

                # if the current move is not valid, reset the tile and highlight it as incorrect
                self.board[empty[0]][empty[1]] = 0
                self.tiles[empty[0]][empty[1]].value = 0
                self.tiles[empty[0]][empty[1]].incorrect = True
                self.tiles[empty[0]][empty[1]].correct = False
                pygame.time.delay(63)  # delay to slow down the solving animation
                self.redraw({}, wrong, time)  # redraw the game window with the updated board

    def hint(self, keys):
        while True:
            i = random.randint(0, 8)
            j = random.randint(0, 8)
            if self.board[i][j] == 0:
                if (j, i) in keys:
                    del keys[(j, i)]
                # fill in the selected empty tile with the correct number
                self.board[i][j] = self.solved_board[i][j]
                self.tiles[i][j].value = self.solved_board[i][j]
                return True
            elif self.board == self.solved_board:
                return False  # the board is already solved, so no hint can be provided.

class Tile:
    def __init__(self, value, window, x1, y1):
        self.value = value
        self.window = window
        self.rect = pygame.Rect(x1, y1, 60, 60)
        self.selected = False
        self.correct = False
        self.incorrect = False

    def draw(self, color, thickness):
        pygame.draw.rect(self.window, color, self.rect, thickness)

    def display(self, value, pos, color):
        font = pygame.font.SysFont("lato", 45)
        text = font.render(str(value), True, color)
        self.window.blit(text, pos)

    def clicked(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.selected = True
        return self.selected

def main():
    # Set up pygame window
    screen = pygame.display.set_mode((540, 590))
    screen.fill((255, 255, 255))
    pygame.display.set_caption("Sudoku Solver")
    icon = pygame.image.load("assets/thumbnail.png")
    pygame.display.set_icon(icon)

    # Display "Generating Random Grid" text while generating a random grid
    font = pygame.font.SysFont("Bahnschrift", 40)
    text = font.render("Generating", True, (0, 0, 0))
    screen.blit(text, (175, 245))

    font = pygame.font.SysFont("Bahnschrift", 40)
    text = font.render("Random Grid", True, (0, 0, 0))
    screen.blit(text, (156, 290))
    pygame.display.flip()

    wrong = 0
    board = Board(screen)
    selected = (-1, -1)
    key_dict = {}
    solved = False
    start_time = time.time()

    while not solved:
        # Tinh thoi gian giai sudoku
        elapsed = time.time() - start_time
        passedTime = time.strftime("%H:%M:%S", time.gmtime(elapsed))

        # Kiem tra xem bang sudoku da solve chua
        if board.board == board.solved_board:
            solved = True

        # Xu li cac event
        for event in pygame.event.get():
            elapsed = time.time() - start_time
            passedTime = time.strftime("%H:%M:%S", time.gmtime(elapsed))
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.MOUSEBUTTONUP:
                # Kiem tra xem tile co duoc click hay khong
                mousePos = pygame.mouse.get_pos()
                for i in range(9):
                    for j in range(9):
                        if board.tiles[i][j].clicked(mousePos):
                            selected = (i, j)
                            board.deselect(board.tiles[i][j])
            elif event.type == pygame.KEYDOWN:
                # Handle key presses
                if board.board[selected[1]][selected[0]] == 0 and selected != (-1, -1):
                    if event.key == pygame.K_1:
                        key_dict[selected] = 1

                    if event.key == pygame.K_2:
                        key_dict[selected] = 2

                    if event.key == pygame.K_3:
                        key_dict[selected] = 3

                    if event.key == pygame.K_4:
                        key_dict[selected] = 4

                    if event.key == pygame.K_5:
                        key_dict[selected] = 5

                    if event.key == pygame.K_6:
                        key_dict[selected] = 6

                    if event.key == pygame.K_7:
                        key_dict[selected] = 7

                    if event.key == pygame.K_8:
                        key_dict[selected] = 8

                    if event.key == pygame.K_9:
                        key_dict[selected] = 9
                    elif event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                        if selected in key_dict:
                            board.tiles[selected[1]][selected[0]].value = 0
                            del key_dict[selected]
                    elif event.key == pygame.K_RETURN:
                        if selected in key_dict:
                            if key_dict[selected] != board.solved_board[selected[1]][selected[0]]:
                                wrong += 1
                                board.tiles[selected[1]][selected[0]].value = 0
                                del key_dict[selected]
                                # break

                            board.tiles[selected[1]][selected[0]].value = key_dict[selected]
                            board.board[selected[1]][selected[0]] = key_dict[selected]
                            del key_dict[selected]

                # Kiem tra phim goi y (phim H)
                if event.key == pygame.K_h:
                    board.hint(key_dict)

                # Kiem tra backtrack event (phim space)
                if event.key == pygame.K_SPACE:
                    # Deselect cac tile and clear key_dict
                    for i in range(9):
                        for j in range(9):
                            board.tiles[i][j].selected = False
                    key_dict = {}

                    # Solve the sudoku visually and reset all tile correctness
                    elapsed = time.time() - start_time
                    passedTime = time.strftime("%H:%M:%S", time.gmtime(elapsed))
                    board.visual_solve(wrong, passedTime)
                    for i in range(9):
                        for j in range(9):
                            board.tiles[i][j].correct = False
                            board.tiles[i][j].incorrect = False

                    # Set solved thanh True sau khi solve xong board
                    solved = True

        board.redraw(key_dict, wrong, passedTime)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return


main()
pygame.quit()
