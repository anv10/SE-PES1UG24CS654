import pygame

class Snake:
    def __init__(self, x, y, cell_size):
        self.cell_size = cell_size
        # body is a list of (x, y) grid-cell positions, head is body[0]
        self.body = [(x, y), (x - 1, y), (x - 2, y)]
        self.direction = (1, 0)  # moving right
        self.grow_pending = False
        # Buffered turns, applied one per move so two quick key presses
        # within a single tick can't add up to a reversal.
        self.direction_queue = []

    def set_direction(self, dx, dy):
        # Validate against the last queued direction (or the current one),
        # ignoring reversals and repeats of the same direction.
        last = self.direction_queue[-1] if self.direction_queue else self.direction
        if (dx, dy) == last or (dx, dy) == (-last[0], -last[1]):
            return
        if len(self.direction_queue) < 2:
            self.direction_queue.append((dx, dy))

    def move(self):
        if self.direction_queue:
            self.direction = self.direction_queue.pop(0)
        head_x, head_y = self.body[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)

        self.body.insert(0, new_head)
        if self.grow_pending:
            self.grow_pending = False
        else:
            self.body.pop()

    def grow(self):
        self.grow_pending = True

    def head_rect(self):
        x, y = self.body[0]
        return pygame.Rect(x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)

    def segment_rects(self):
        return [
            pygame.Rect(x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)
            for (x, y) in self.body
        ]

    def collides_with_self(self):
        head = self.body[0]
        return head in self.body[1:]

    def collides_with_wall(self, grid_width, grid_height):
        x, y = self.body[0]
        return x < 0 or y < 0 or x >= grid_width or y >= grid_height
