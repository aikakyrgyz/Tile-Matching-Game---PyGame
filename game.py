#game.py
#view
import pygame
import game_logic
import user_interface
import random

_INITIAL_WIDTH = 700
_INITIAL_HEIGHT = 700
_BACKGROUND_COLOR = pygame.Color(255, 255, 255)
_BOARD_COLOR = pygame.Color(0, 0, 0)
_JEWEL_WIDTH = 0.05
_JEWEL_HEIGHT = 0.05
_ROWS_NUM = 13
_COLUMN_NUM = 6
_FALLER = 3
LETTER_COLORS = ['S', 'T', 'V', 'W', 'X', 'Y', 'Z']
_COLORS = {'S': pygame.Color(204, 255, 255), 'T': pygame.Color(255, 204, 255),
           'V': pygame.Color(153, 153, 255), 'W': pygame.Color(0, 204, 153),
           'X': pygame.Color(255, 218, 179), 'Y': pygame.Color(179, 204, 255),
           'Z': pygame.Color(191, 255, 128), 'MATCH': pygame.Color(255, 255, 0),
           ' ': _BACKGROUND_COLOR}


class ColumnsGame:
    def __init__(self):
        self._running = True
        self._state = game_logic.GameBoard(_ROWS_NUM, _COLUMN_NUM)
        self._state.set_board(True, [])


    def run(self) -> None:
        pygame.init()
        self._create_surface((_INITIAL_WIDTH, _INITIAL_HEIGHT))
        clock = pygame.time.Clock()
        action = 0
        while self._running:
            clock.tick(30)
            self._handle_events()
            if action%10==0:
                user_interface.draw_board(self._state)
                self._state.action()
                if self._state.get_game_over():
                    self._end_game()
                self._add_faller()
                action = 0
            self._redraw()

            action+=1

        pygame.quit()

    def _end_game(self) -> None:
        self._running = False


    def _create_surface(self, dimensions: tuple[int, int]) -> None:
        self._surface = pygame.display.set_mode(dimensions, pygame.RESIZABLE)
        self._jewel_image_scaled = None

    def _redraw(self) -> None:
        self._surface.fill(_BACKGROUND_COLOR)
        self._draw_board_box()
        self._draw_jewels()
        pygame.display.flip()

    def _draw_board_box(self):
        self._distance_from_top = (1.0 - (_JEWEL_HEIGHT * 13))/2
        self._distance_from_side = (1.0 - (_JEWEL_WIDTH * 6))/2

        top_left_frac_x = self._distance_from_side
        top_left_frac_y = self._distance_from_top

        top_left_pixel_x = int(top_left_frac_x * self._surface.get_width())
        top_left_pixel_y = int(top_left_frac_y * self._surface.get_height())

        width_pixel = _JEWEL_WIDTH * _COLUMN_NUM * self._surface.get_width()
        height_pixel = _JEWEL_HEIGHT * _ROWS_NUM * self._surface.get_height()

        board_box = pygame.Rect(top_left_pixel_x, top_left_pixel_y, width_pixel, height_pixel)

        pygame.draw.rect(self._surface, _BOARD_COLOR, board_box, 0)

    def _draw_jewels(self) -> None:
        for row in range(2, self._state.get_rows()):
            for col in range(self._state.get_columns()):
                cell = self._state.get_board_cell(row, col)
                status = cell.get_status()
                letter = cell.get_value()
                if status == game_logic.Cell.empty_cell:
                    continue
                top_left_frac_x = (col * _JEWEL_WIDTH) + self._distance_from_side
                top_left_frac_y = ((row-2) * _JEWEL_HEIGHT) + self._distance_from_top
                top_left_pixel_x = int(top_left_frac_x * self._surface.get_width())
                top_left_pixel_y = int(top_left_frac_y * self._surface.get_height())
                if status == game_logic.Cell.match:
                    color = _COLORS['MATCH']
                else:
                    color = _COLORS[letter]
                self._draw_jewel(top_left_pixel_x, top_left_pixel_y, color)

    def _draw_jewel(self, top_left_pixel_x, top_left_pixel_y, color) -> None:
        width = _JEWEL_WIDTH * self._surface.get_width()
        height = _JEWEL_HEIGHT * self._surface.get_height()
        jewel_rect = pygame.Rect(top_left_pixel_x, top_left_pixel_y, width, height)
        pygame.draw.rect(self._surface, color, jewel_rect)


    def _add_faller(self) -> None:
        if self._state.get_faller() == None:
                faller_colors = self._random_colors()
                faller_column = self._random_column()
                while self._state.get_board_cell(0, faller_column).get_status() != game_logic.Cell.empty_cell:
                    faller_column = self._random_column()
                self._state.add_faller_to_board(faller_column, faller_colors[0],
                                                faller_colors[1], faller_colors[2])

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False
            elif event.type == pygame.VIDEORESIZE:
                self._create_surface(event.size)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self._state.rotate_faller()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                self._state.move_left()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                self._state.move_right()
            else:
                return

    def _random_colors(self) -> list:
        faller_colors = []
        for jewel in range(_FALLER):
            faller_colors.append(random.choice(LETTER_COLORS))
        return faller_colors

    def _random_column(self) -> int:
        return random.randint(0, _COLUMN_NUM-1)


if __name__ == '__main__':
    ColumnsGame().run()