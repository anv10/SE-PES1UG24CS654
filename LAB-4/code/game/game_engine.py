import pygame
from .snake import Snake
from .food import Food

# Game Engine

WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (220, 60, 60)

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.cell_size = 20
        self.grid_width = width // self.cell_size
        self.grid_height = height // self.cell_size

        self.snake = Snake(self.grid_width // 2, self.grid_height // 2, self.cell_size)
        self.food = Food(self.grid_width, self.grid_height, self.cell_size, self.snake.body)

        self.score = 0
        self.font = pygame.font.SysFont("Arial", 30)
        self.big_font = pygame.font.SysFont("Arial", 60, bold=True)

        self.moves_per_second = 8
        self._frame_counter = 0

        self.game_over = False
        self.quit_requested = False

    def handle_keydown(self, key):
        if self.game_over:
            # Game Over screen waits for the player's choice.
            if key in (pygame.K_q, pygame.K_ESCAPE):
                self.quit_requested = True
            return

        # Direction changes are buffered by the snake and applied on its next move.
        if key in (pygame.K_UP, pygame.K_w):
            self.snake.set_direction(0, -1)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.snake.set_direction(0, 1)
        elif key in (pygame.K_LEFT, pygame.K_a):
            self.snake.set_direction(-1, 0)
        elif key in (pygame.K_RIGHT, pygame.K_d):
            self.snake.set_direction(1, 0)

    def handle_input(self):
        # Reserved for continuously-held-key input (not used for a
        # grid-based snake, but kept here to mirror the engine's shape).
        pass

    def update(self):
        if self.game_over:
            return

        self._frame_counter += 1
        frames_per_move = max(1, 60 // self.moves_per_second)
        if self._frame_counter < frames_per_move:
            return
        self._frame_counter = 0

        prev_body = list(self.snake.body)
        self.snake.move()

        if (self.snake.collides_with_wall(self.grid_width, self.grid_height)
                or self.snake.collides_with_self()):
            # Undo the fatal move so the head is drawn against the wall/body
            # it hit, not past the edge of the screen or on top of itself.
            self.snake.body = prev_body
            self.game_over = True
            return

        if self.snake.head_rect().colliderect(self.food.rect()):
            self.snake.grow()
            self.score += 1
            self.food.respawn(self.snake.body)

    def render(self, screen):
        # Draw food
        pygame.draw.rect(screen, RED, self.food.rect())

        # Draw snake
        for rect in self.snake.segment_rects():
            pygame.draw.rect(screen, GREEN, rect)

        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        if self.game_over:
            self.render_game_over(screen)

    def render_game_over(self, screen):
        # Dim the board, then draw the Game Over text centred on top.
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        lines = [
            (self.big_font, "GAME OVER", RED),
            (self.font, f"Final Score: {self.score}", WHITE),
            (self.font, "Press Q or Esc to quit", WHITE),
        ]
        y = self.height // 2 - 80
        for font, text, color in lines:
            surface = font.render(text, True, color)
            screen.blit(surface, surface.get_rect(center=(self.width // 2, y)))
            y += surface.get_height() + 20
