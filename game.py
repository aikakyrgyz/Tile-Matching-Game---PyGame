#game.py
#view
import pygame
import game_logic
import user_interface
import random

_INITIAL_WIDTH = 700
_INITIAL_HEIGHT = 700
_BACKGROUND_COLOR = pygame.Color(255, 255, 255)
_LANDED_COLOR = pygame.Color(173, 235, 235)
_GRID = pygame.Color(184,184,184)
_BOARD_COLOR = pygame.Color(0, 0, 0)
_JEWEL_WIDTH = 0.07
_JEWEL_HEIGHT = 0.07
_ROWS_NUM = 13
_COLUMN_NUM = 6
_FALLER = 3
LETTER_COLORS = ['S', 'T', 'V', 'W', 'X', 'Y', 'Z']
_COLORS = {'S': [pygame.Color(204, 255, 255), pygame.image.load('1.jpg')],
           'T': [pygame.Color(255, 204, 255), pygame.image.load('2.jpg')],
           'V': [pygame.Color(153, 153, 255), pygame.image.load('3.jpg')],
           'W': [pygame.Color(0, 204, 153),   pygame.image.load('4.jpg')],
           'X': [pygame.Color(255, 218, 179), pygame.image.load('5.jpg')],
           'Y': [pygame.Color(179, 204, 255), pygame.image.load('6.jpg')],
           'Z': [pygame.Color(191, 255, 128), pygame.image.load('7.png')],
           'MATCH': [pygame.Color(255, 255, 0), pygame.image.load('match.jpeg')],
           ' ': _BACKGROUND_COLOR}



class ColumnsGame:
    def __init__(self):
        self._running = True
        self._state = game_logic.GameBoard(_ROWS_NUM, _COLUMN_NUM)
        self._state.set_board(True, [])
        self._background_image = pygame.image.load('background.jpeg')

    def run(self) -> None:
        pygame.init()
        self._create_surface((_INITIAL_WIDTH, _INITIAL_HEIGHT))
        clock = pygame.time.Clock()
        action = 0
        while self._running:
            clock.tick(40)
            self._handle_events()
            if action%10==0:
                user_interface.draw_board(self._state)
                self._state.action()
                if self._state.get_game_over():
                    self._draw_end_game()
                    self._end_game()
                self._add_faller()
                action = 0
            self._redraw()
            action+=1

        pygame.quit()

    def _end_game(self) -> None:
        self._running = False

    def _draw_end_game(self) -> None:
        pygame.font.init()
        text = pygame.font.SysFont('Century', 63, False, True)
        text_surface = text.render('GAME OVER', True, (255, 102, 102))
        self._surface.blit(text_surface, (215, 210))
        pygame.display.flip()
        waiting = True
        clock = pygame.time.Clock()
        while waiting:
            clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                if event.type == pygame.VIDEORESIZE:
                    self._create_surface(event.size)

    def _create_surface(self, dimensions: tuple[int, int]) -> None:
        self._surface = pygame.display.set_mode(dimensions, pygame.RESIZABLE)
        self._jewel_image_scaled = None

    def _redraw(self) -> None:
        self._draw_background()
        self._draw_board_box()
        self._draw_jewels()
        pygame.display.flip()

    def _draw_background(self) -> None:
        background_rect = pygame.Rect(0, 0, self._surface.get_width(), self._surface.get_height())
        scaled_image = pygame.transform.scale(self._background_image, (self._surface.get_width(), self._surface.get_height()))
        self._surface.blit(scaled_image, background_rect)

    def _draw_board_box(self):
        self._distance_from_top = (1.0 - (_JEWEL_HEIGHT * 13))/2 - 0.002
        self._distance_from_side = (1.0 - (_JEWEL_WIDTH * 6))/2 - 0.002

        top_left_frac_x = self._distance_from_side
        top_left_frac_y = self._distance_from_top

        top_left_pixel_x = int(top_left_frac_x * self._surface.get_width())
        top_left_pixel_y = int(top_left_frac_y * self._surface.get_height())

        width_pixel = ((_JEWEL_WIDTH) * _COLUMN_NUM) * self._surface.get_width()
        height_pixel = ((_JEWEL_HEIGHT) * _ROWS_NUM) * self._surface.get_height()

        self._board_box = pygame.Rect(top_left_pixel_x, top_left_pixel_y, width_pixel + 3, height_pixel + 3)
        pygame.draw.rect(self._surface, _GRID, self._board_box, 2)

    def _draw_jewels(self) -> None:
        for row in range(2, self._state.get_rows()):
            for col in range(self._state.get_columns()):
                cell = self._state.get_board_cell(row, col)
                status = cell.get_status()
                letter = cell.get_value()
                top_left_frac_x = (col * _JEWEL_WIDTH) + self._distance_from_side + 0.002
                top_left_frac_y = ((row-2) * _JEWEL_HEIGHT) + self._distance_from_top + 0.003
                top_left_pixel_x = int(top_left_frac_x * self._surface.get_width())
                top_left_pixel_y = int(top_left_frac_y * self._surface.get_height())
                if status == game_logic.Cell.match:
                    color = _COLORS['MATCH'][1]
                elif status == game_logic.Cell.empty_cell:
                    color = _BACKGROUND_COLOR
                elif status == game_logic.Cell.landed_cell:
                    color = _LANDED_COLOR
                else:
                    color = _COLORS[letter][1] #change index to 0, if want to use colors instead of images

                self._draw_jewel(status, top_left_pixel_x, top_left_pixel_y, color)

    def _draw_jewel(self, status, top_left_pixel_x, top_left_pixel_y, color) -> None:
        width = _JEWEL_WIDTH * self._surface.get_width()
        height = _JEWEL_HEIGHT * self._surface.get_height()
        jewel_rect = pygame.Rect(top_left_pixel_x, top_left_pixel_y, width, height)
        if status != game_logic.Cell.empty_cell and status != game_logic.Cell.landed_cell:
            self._assign_image(jewel_rect, width, height, color) #color is the image
        else:
            pygame.draw.rect(self._surface, color, jewel_rect)
        if status == game_logic.Cell.empty_cell:
            pygame.draw.rect(self._surface, _GRID, jewel_rect, 1 )
        else:
            pygame.draw.rect(self._surface, _BACKGROUND_COLOR, jewel_rect, 1)

    def _add_faller(self) -> None:
        if self._state.get_faller() == None:
                faller_colors = self._random_colors()
                faller_column = self._random_column()
                while self._state.get_board_cell(2, faller_column).get_status() != game_logic.Cell.empty_cell:
                    faller_column = self._random_column()
                self._state.add_faller_to_board(faller_column, faller_colors[0],
                                                faller_colors[1], faller_colors[2])

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False
            if event.type == pygame.VIDEORESIZE:
                print('RESIZE')
                self._create_surface(event.size)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self._state.rotate_faller()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                self._state.move_left()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                self._state.move_right()

    def _assign_image(self, jewel_rect, width, height, color) -> None:
        scaled_image = pygame.transform.scale(color, (width, height))
        self._surface.blit(scaled_image, jewel_rect)

    def _random_colors(self) -> list:
        faller_colors = []
        for jewel in range(_FALLER):
            faller_colors.append(random.choice(LETTER_COLORS))
        return faller_colors

    def _random_column(self) -> int:
        return random.randint(0, _COLUMN_NUM-1)



if __name__ == '__main__':
    ColumnsGame().run()