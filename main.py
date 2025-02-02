import pygame
import random
import os

pygame.init()

pygame.mixer.init()
rotate_sound = pygame.mixer.Sound("placing_sound.wav")
line_clear_sound = pygame.mixer.Sound("sound_1.wav")
complete_sound = pygame.mixer.Sound("sound_2.wav")

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
LEADERBOARD_FILE = "leaderboard.txt"

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
    SHAPE_COLORS = {
        "I": (0, 255, 255),
        "O": (255, 255, 0),
        "T": (128, 0, 128),
        "S": (0, 255, 0),
        "Z": (255, 0, 0),
        "J": (0, 0, 255),
        "L": (255, 165, 0)
    }

    SHAPES = {
        "I": [[1, 1, 1, 1]],
        "O": [[1, 1], [1, 1]],
        "T": [[0, 1, 0], [1, 1, 1]],
        "S": [[0, 1, 1], [1, 1, 0]],
        "Z": [[1, 1, 0], [0, 1, 1]],
        "J": [[1, 0, 0], [1, 1, 1]],
        "L": [[0, 0, 1], [1, 1, 1]]
    }

    def __init__(self, shape_type):
        self.shape = self.SHAPES[shape_type]
        self.color = self.SHAPE_COLORS[shape_type]
        self.x = COLUMNS // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]
        rotate_sound.play() 

class Tetris:
    def __init__(self):
        self.grid = [[BLACK for col in range(COLUMNS)] for row in range(ROWS)]
        self.score = 0
        self.game_over = False
        self.current_piece = self.new_piece()
        self.hold_piece = None
        self.hold_used = False
        self.next_pieces = [self.new_piece() for piece in range(3)]

    def new_piece(self):
        shape_type = random.choice(list(Tetrimino.SHAPES.keys()))
        return Tetrimino(shape_type)

    def reset_game(self):
        self.grid = [[BLACK for col in range(COLUMNS)] for row in range(ROWS)]
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
        self.current_piece = self.next_pieces.pop(0)
        self.next_pieces.append(self.new_piece())
        self.hold_used = False
        complete_sound.play()
        if not self.valid_position():
            self.game_over = True

    def clear_lines(self):
        new_grid = [row for row in self.grid if BLACK in row]
        lines_cleared = ROWS - len(new_grid)
        score_table = {1: 100, 2: 300, 3: 700, 4: 1500}
        self.score += score_table.get(lines_cleared, 0)
        if lines_cleared > 0:
            line_clear_sound.play()
        while len(new_grid) < ROWS:
            new_grid.insert(0, [BLACK for col in range(COLUMNS)])
        self.grid = new_grid

    def draw_scoreboard(self, screen):
        pygame.draw.rect(screen, WHITE, (GRID_X_OFFSET + GRID_WIDTH + 19, GRID_Y_OFFSET, SCOREBOARD_WIDTH,
                                         GRID_HEIGHT))
        pygame.draw.rect(screen, BLACK,
                         (GRID_X_OFFSET + GRID_WIDTH + 20, GRID_Y_OFFSET + 1, SCOREBOARD_WIDTH - 2,
                          GRID_HEIGHT - 2))
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

    def draw_next_pieces(self, screen):
        pygame.draw.rect(screen, WHITE,
                         (GRID_X_OFFSET - NEXT_PIECES_MENU_WIDTH - 20, GRID_Y_OFFSET, NEXT_PIECES_MENU_WIDTH,
                          GRID_HEIGHT))
        pygame.draw.rect(screen, BLACK,
                         (GRID_X_OFFSET - NEXT_PIECES_MENU_WIDTH - 19, GRID_Y_OFFSET + 1, NEXT_PIECES_MENU_WIDTH - 2,
                          GRID_HEIGHT - 2))
        font = pygame.font.Font(None, 36)
        text = font.render("Ближайшие фигуры", True, WHITE)
        screen.blit(text, (GRID_X_OFFSET - NEXT_PIECES_MENU_WIDTH, GRID_Y_OFFSET + 20))

        for i, piece in enumerate(self.next_pieces):
            for y, row in enumerate(piece.shape):
                for x, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(
                            screen, piece.color,
                            (GRID_X_OFFSET - NEXT_PIECES_MENU_WIDTH + 40 + x * CELL_SIZE,
                             GRID_Y_OFFSET + 60 + i * 100 + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                        )

    def save_score(self):
        with open(LEADERBOARD_FILE, "a") as file:
            file.write(str(self.score) + "\n")

def load_leaderboard():
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    with open(LEADERBOARD_FILE, "r") as file:
        scores = [int(line.strip()) for line in file]
    return sorted(scores, reverse=True)


def draw_leaderboard(screen):
    leaderboard_running = True
    scores = load_leaderboard()
    font = pygame.font.Font('Hakim_0.ttf', 48)
    text = font.render("Таблица лидеров", True, WHITE)

    back_button = Button(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT - 100, 200, 50, "Назад", font,
                         (100, 100, 100), (150, 150, 150),
                            lambda: setattr(draw_leaderboard, 'leaderboard_running', False))

    while leaderboard_running:
        screen.blit(background, (0, 0))
        screen.blit(text, (WINDOW_WIDTH // 2 - text.get_width() // 2, 100))
        y_offset = 200
        for i, score in enumerate(scores[:10]):
            score_text = font.render(f"{i + 1}. {score}", True, WHITE)
            screen.blit(score_text, (WINDOW_WIDTH // 2 - score_text.get_width() // 2, y_offset))
            y_offset += 50
        back_button.draw(screen)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            back_button.handle_event(event)
        if not hasattr(draw_leaderboard, 'leaderboard_running'):
            leaderboard_running = True
        else:
            leaderboard_running = getattr(draw_leaderboard, 'leaderboard_running')
    delattr(draw_leaderboard, 'leaderboard_running')


def draw_next_pieces(self, screen):
    pygame.draw.rect(screen, WHITE, (GRID_X_OFFSET - NEXT_PIECES_MENU_WIDTH - 20, GRID_Y_OFFSET, NEXT_PIECES_MENU_WIDTH, GRID_HEIGHT))
    pygame.draw.rect(screen, BLACK, (GRID_X_OFFSET - NEXT_PIECES_MENU_WIDTH - 19, GRID_Y_OFFSET + 1, NEXT_PIECES_MENU_WIDTH - 2, GRID_HEIGHT - 2))

    font = pygame.font.Font(None, 36)
    text = font.render("Ближайшие фигуры:", True, WHITE)
    screen.blit(text, (GRID_X_OFFSET - NEXT_PIECES_MENU_WIDTH + 10, GRID_Y_OFFSET + 20))

    piece_x_offset = GRID_X_OFFSET - NEXT_PIECES_MENU_WIDTH + 40
    for i, piece in enumerate(self.next_pieces):
        piece_y_offset = GRID_Y_OFFSET + 60 + i * 100

        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect(
                        piece_x_offset + x * CELL_SIZE,
                        piece_y_offset + y * CELL_SIZE,
                        CELL_SIZE, CELL_SIZE
                    )
                    pygame.draw.rect(screen, piece.color, rect)
                    pygame.draw.rect(screen, WHITE, rect, 1)

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SCALED)
pygame.display.set_caption("Тетрис")
clock = pygame.time.Clock()

background = pygame.image.load("more.jpg")
background = pygame.transform.scale(background, (WINDOW_WIDTH, WINDOW_HEIGHT))


class Button:
    def __init__(self, x, y, width, height, text, font, color, hover_color, action):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.action = action
        self.text_surf = font.render(text, True, WHITE)
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, self.hover_color, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)
        screen.blit(self.text_surf, self.text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos):
            line_clear_sound.play()
            self.action()


def main_menu():
    menu_running = True
    font1 = pygame.font.Font('Hakim_0.ttf', 64)
    font2 = pygame.font.Font('Hakim_0.ttf', 48)

    start_button = Button(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2, 200, 50, "Старт", font2, (100, 100, 100), (150, 150, 150),
                            lambda: setattr(main_menu, 'menu_running', False))
    settings_button = Button(WINDOW_WIDTH // 2 - 225, WINDOW_HEIGHT // 2 + 60, 450, 50, "Таблица лидеров", font2, (100, 100, 100),
                            (150, 150, 150), lambda: draw_leaderboard(screen))
    quit_button = Button(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 + 120, 200, 50, "Выход", font2, (100, 100, 100),
                            (150, 150, 150), lambda: setattr(main_menu, 'menu_running', False) or pygame.quit() or exit())
    title = font1.render("Tetris", True, WHITE)

    while menu_running:
        screen.blit(background, (0, 0))
        screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, WINDOW_HEIGHT // 2 - 100))
        start_button.draw(screen)
        settings_button.draw(screen)
        quit_button.draw(screen)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            start_button.handle_event(event)
            settings_button.handle_event(event)
            quit_button.handle_event(event)
        
        if not hasattr(main_menu, 'menu_running'):
            menu_running = True
        else:
            menu_running = getattr(main_menu, 'menu_running')
    delattr(main_menu, 'menu_running')

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
    tetris.draw_next_pieces(screen)

    if tetris.game_over:
        font = pygame.font.Font(None, 48)
        text = font.render("GAME OVER", True, WHITE)
        screen.blit(text, (WINDOW_WIDTH // 2 - text.get_width() // 2, WINDOW_HEIGHT // 2 - text.get_height() // 2))
        pygame.display.flip()
        pygame.time.wait(2000)
        tetris.save_score()
        tetris.reset_game()

    pygame.display.flip()

pygame.quit()
