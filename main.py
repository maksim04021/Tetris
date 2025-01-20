import pygame
import random

pygame.init()

WINDOW_WIDTH, WINDOW_HEIGHT = 1980, 1080
CELL_SIZE = 30
COLUMNS = 10
ROWS = 20
GRID_WIDTH = COLUMNS * CELL_SIZE
GRID_HEIGHT = ROWS * CELL_SIZE
GRID_X_OFFSET = (WINDOW_WIDTH - GRID_WIDTH) // 2
GRID_Y_OFFSET = (WINDOW_HEIGHT - GRID_HEIGHT) // 2
SCOREBOARD_WIDTH = 300
NEXT_PIECES_MENU_WIDTH = 300

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)

COLORS = [CYAN, YELLOW, MAGENTA, GREEN, RED, BLUE, ORANGE]

SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[0, 1, 0], [1, 1, 1]],
    [[1, 0, 0], [1, 1, 1]],
    [[0, 0, 1], [1, 1, 1]],
    [[0, 1, 1], [1, 1, 0]],
    [[1, 1, 0], [0, 1, 1]]
]


class Tetrimino:
    def __init__(self, shape, color):
        self.shape = shape
        self.color = color
        self.x = COLUMNS // 2 - len(shape[0]) // 2
        self.y = 0

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]


class Tetris:
    def __init__(self):
        self.grid = [[BLACK for elem in range(COLUMNS)] for elem in range(ROWS)]
        self.score = 0
        self.game_over = False
        self.current_piece = self.new_piece()
        self.hold_piece = None
        self.hold_used = False

    def new_piece(self):
        shape = random.choice(SHAPES)
        color = random.choice(COLORS)
        return Tetrimino(shape, color)

    def reset_game(self):
        self.grid = [[BLACK for elem in range(COLUMNS)] for elem in range(ROWS)]
        self.score = 0
        self.game_over = False
        self.current_piece = self.new_piece()
        self.hold_piece = None
        self.hold_used = False

    def draw_grid(self, screen):
        for y in range(ROWS):
            for x in range(COLUMNS):
                pygame.draw.rect(screen, self.grid[y][x],
                                 (GRID_X_OFFSET + x * CELL_SIZE, GRID_Y_OFFSET + y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(screen, WHITE,
                                 (GRID_X_OFFSET + x * CELL_SIZE, GRID_Y_OFFSET + y * CELL_SIZE, CELL_SIZE, CELL_SIZE),
                                 1)

    def draw_piece(self, screen, piece):
        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(
                        screen, piece.color,
                        (
                            GRID_X_OFFSET + (piece.x + x) * CELL_SIZE, GRID_Y_OFFSET + (piece.y + y) * CELL_SIZE,
                            CELL_SIZE,
                            CELL_SIZE)
                    )

    def draw_hold(self, screen):
        font = pygame.font.Font(None, 32)
        text = font.render("HOLD", True, WHITE)
        screen.blit(text, (10, 10))
        if self.hold_piece:
            for y, row in enumerate(self.hold_piece.shape):
                for x, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(
                            screen, self.hold_piece.color,
                            (10 + x * CELL_SIZE, 40 + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                        )

    def hold_current_piece(self):
        if not self.hold_used:
            if self.hold_piece is None:
                self.hold_piece = self.current_piece
                self.current_piece = self.new_piece()
            else:
                self.hold_piece, self.current_piece = self.current_piece, self.hold_piece
                self.hold_piece.x, self.hold_piece.y = 0, 0
            self.hold_used = True

    def move_piece(self, dx, dy):
        self.current_piece.x += dx
        self.current_piece.y += dy
        if not self.valid_position():
            self.current_piece.x -= dx
            self.current_piece.y -= dy
            return False
        return True

    def drop_piece(self):
        while self.move_piece(0, 1):
            pass
        self.lock_piece()

    def valid_position(self):
        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = self.current_piece.x + x
                    new_y = self.current_piece.y + y
                    if new_x < 0 or new_x >= COLUMNS or new_y >= ROWS:
                        return False
                    if new_y >= 0 and self.grid[new_y][new_x] != BLACK:
                        return False
        return True

    def lock_piece(self):
        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[self.current_piece.y + y][self.current_piece.x + x] = self.current_piece.color
        self.clear_lines()
        self.current_piece = self.new_piece()
        self.hold_used = False
        if not self.valid_position():
            self.game_over = True

    def clear_lines(self):
        new_grid = [row for row in self.grid if BLACK in row]
        lines_cleared = ROWS - len(new_grid)
        score_table = {1: 100, 2: 300, 3: 700, 4: 1500}
        self.score += score_table.get(lines_cleared, 0)
        while len(new_grid) < ROWS:
            new_grid.insert(0, [BLACK for elem in range(COLUMNS)])
        self.grid = new_grid

    def draw_scoreboard(self, screen):
        pygame.draw.rect(screen, WHITE, (GRID_X_OFFSET + GRID_WIDTH + 19, GRID_Y_OFFSET, SCOREBOARD_WIDTH, GRID_HEIGHT))
        pygame.draw.rect(screen, BLACK,
                         (GRID_X_OFFSET + GRID_WIDTH + 20, GRID_Y_OFFSET + 1, SCOREBOARD_WIDTH - 2, GRID_HEIGHT - 2))
        font = pygame.font.Font(None, 48)
        text = font.render("Счет", True, WHITE)
        screen.blit(text, (GRID_X_OFFSET + GRID_WIDTH + 50, GRID_Y_OFFSET + 20))

        score_text = font.render(str(self.score), True, WHITE)
        screen.blit(score_text, (GRID_X_OFFSET + GRID_WIDTH + 50, GRID_Y_OFFSET + 80))

    def draw_next_pieces_bg(self, screen):
        pygame.draw.rect(screen, WHITE,
                         (GRID_X_OFFSET - GRID_WIDTH - 21, GRID_Y_OFFSET, NEXT_PIECES_MENU_WIDTH, GRID_HEIGHT))
        pygame.draw.rect(screen, BLACK, (
            GRID_X_OFFSET - GRID_WIDTH - 20, GRID_Y_OFFSET + 1, NEXT_PIECES_MENU_WIDTH - 2, GRID_HEIGHT - 2))
        font = pygame.font.Font(None, 36)
        text = font.render("Ближайшие фигуры: ", True, WHITE)
        screen.blit(text, (GRID_X_OFFSET - GRID_WIDTH, GRID_Y_OFFSET + 20))


# доделать фигуры

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SCALED)
pygame.display.set_caption("Тетрис")
clock = pygame.time.Clock()

background = pygame.image.load("more.jpg")
background = pygame.transform.scale(background, (WINDOW_WIDTH, WINDOW_HEIGHT))


def main_menu():
    menu_running = True
    while menu_running:
        screen.blit(background, (0, 0))
        font1 = pygame.font.Font('Hakim_0.ttf', 64)
        font2 = pygame.font.Font('Hakim_0.ttf', 48)
        title = font1.render("Tetris", True, WHITE)
        start = font2.render("1. Старт", True, WHITE)
        settings = font2.render("2. Таблица лидеров", True, WHITE)
        quit = font2.render("3. Выход", True, WHITE)
        screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, WINDOW_HEIGHT // 2 - 100))
        screen.blit(start, (WINDOW_WIDTH // 2 - start.ge3 t_width() // 2, WINDOW_HEIGHT // 2))
        screen.blit(settings, (WINDOW_WIDTH // 2 - settings.get_width() // 2, WINDOW_HEIGHT // 2 + 50))
        screen.blit(quit, (WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 + 100))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    menu_running = False
                if event.key == pygame.K_2:
                    pass
                if event.key == pygame.K_3:
                    game_over = True
                    pygame.quit()


main_menu()

tetris = Tetris()
fall_time = 0
fall_speed = 500

running = True
while running:
    screen.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                tetris.move_piece(-1, 0)
            if event.key == pygame.K_RIGHT:
                tetris.move_piece(1, 0)
            if event.key == pygame.K_DOWN:
                tetris.move_piece(0, 1)
            if event.key == pygame.K_UP:
                tetris.current_piece.rotate()
                if not tetris.valid_position():
                    tetris.current_piece.rotate()
                    tetris.current_piece.rotate()
                    tetris.current_piece.rotate()
            if event.key == pygame.K_ESCAPE:
                main_menu()
            if event.key == pygame.K_SPACE:
                tetris.drop_piece()
            if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                tetris.hold_current_piece()

    fall_time += clock.get_rawtime()
    clock.tick()

    if fall_time > fall_speed:
        if not tetris.move_piece(0, 1):
            tetris.lock_piece()
        fall_time = 0

    tetris.draw_grid(screen)
    tetris.draw_piece(screen, tetris.current_piece)
    tetris.draw_hold(screen)
    tetris.draw_scoreboard(screen)
    tetris.draw_next_pieces_bg(screen)

    if tetris.game_over:
        font = pygame.font.Font(None, 48)
        text = font.render("GAME OVER", True, WHITE)
        screen.blit(text, (WINDOW_WIDTH // 2 - text.get_width() // 2, WINDOW_HEIGHT // 2 - text.get_height() // 2))
        pygame.display.flip()
        pygame.time.wait(2000)
        tetris.reset_game()

    pygame.display.flip()

pygame.quit()
