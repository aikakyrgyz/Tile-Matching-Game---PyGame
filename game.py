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
_GRID = pygame.Color(102, 179, 255)
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
        self._background_image = pygame.image.load('background.jpeg')
        self._running = True
        self._state = game_logic.GameBoard(_ROWS_NUM, _COLUMN_NUM)
        self._state.set_board(True, [])

    def run(self) -> None:
        pygame.init()
        self._create_surface((_INITIAL_WIDTH, _INITIAL_HEIGHT))
        self._initialize_sounds()
        clock = pygame.time.Clock()
        action = 0
        while self._running:
            clock.tick(400)
            self._handle_events()
            if action % 30 == 0:
                self._state.action()
                self._set_score()
                if self._state.get_faller():
                    if self._state.get_faller().get_status() == game_logic.Faller.landed_status:
                        self._play_sound('fall')
                if self._state.get_game_over():
                    self._end_game()
                    self._play_sound('game over')
                    self._draw_end_game()
                self._add_faller()
                action = 0
            self._redraw()
            pygame.display.flip()

            action += 1

        pygame.quit()

    def _initialize_sounds(self):
        """
        Initialized all the sounds needed for the game
        """
        self._sound_left_right = pygame.mixer.Sound('move.mp3')
        self._sound_fall = pygame.mixer.Sound('fall.mp3')
        self._sound_game_over = pygame.mixer.Sound('game_over.wav')

    def _set_score(self):
        """
        Sets the score to the current score
        """
        self._score = (self._state.get_score() - 3) / 2

    def _end_game(self) -> None:
        self._running = False

    def _draw_end_game(self) -> None:
        """
        Displays Game Over text
        Stays still until the close button is clicked
        """
        waiting = True
        clock = pygame.time.Clock()
        while waiting:
            clock.tick(30)
            pygame.font.init()
            self._redraw()
            text = pygame.font.SysFont('Century', int(65 * self._surface.get_height() / 700), False, False)
            text_surface = text.render('GAME OVER', True, (255, 51, 51))
            # self._surface.blit(text_surface, (210, 210))
            pixel_x = self._surface.get_width() * 0.3
            pixel_y = self._surface.get_height() * 0.3
            self._surface.blit(text_surface, (pixel_x, pixel_y))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.VIDEORESIZE:
                    self._create_surface(event.size)

    def _create_surface(self, dimensions: tuple[int, int]) -> None:
        """
        Creates a surface
        :param dimensions: dimensions of the display
        :return: None
        """
        self._surface = pygame.display.set_mode(dimensions, pygame.RESIZABLE)

    def _redraw(self) -> None:
        """
        Redraws all of the contents of the display
        """
        self._draw_background()
        self._draw_board_box()
        self._draw_jewels()

    def _draw_background(self) -> None:
        """
        Draws the background image
        """
        background_rect = pygame.Rect(0, 0, self._surface.get_width(), self._surface.get_height())
        scaled_image = pygame.transform.scale(self._background_image, (self._surface.get_width(), self._surface.get_height()))
        self._surface.blit(scaled_image, background_rect)
        self._draw_score_box()

    def _draw_score_box(self) -> None:
        """
        Draws the score box
        """
        top_left_frac_x = 0.05
        top_left_frac_y = 0.4
        top_left_pixel_x = int(top_left_frac_x * self._surface.get_width())
        top_left_pixel_y = int(top_left_frac_y * self._surface.get_height())
        width_pixel = 0.20 * self._surface.get_width()
        height_pixel = 0.10 * self._surface.get_height()
        self._score_box = pygame.Rect(top_left_pixel_x, top_left_pixel_y, width_pixel, height_pixel)
        pygame.draw.rect(self._surface, pygame.Color(193, 238, 247), self._score_box, 0, 5)
        pygame.font.init()
        text = pygame.font.SysFont('Century', int(40 * self._surface.get_height()/_INITIAL_HEIGHT), False, False)
        text_surface = text.render('Score:', True, (0, 0, 0))
        current_w, current_h = self._surface.get_size()
        text_w, text_h = text_surface.get_size()
        text_surface = pygame.transform.smoothscale(
            text_surface, (text_w * current_w // 700, text_h * current_h // _INITIAL_HEIGHT))
        self._surface.blit(text_surface, (top_left_pixel_x + 10, top_left_pixel_y + 10))
        text = pygame.font.SysFont('Century', int(40 * self._surface.get_height()/700), False, False)
        text_surface = text.render(f'{self._score}', True, (0, 204, 0))
        text_w, text_h = text_surface.get_size()
        text_surface = pygame.transform.smoothscale(
            text_surface, (text_w * current_w // _INITIAL_HEIGHT, text_h * current_h // _INITIAL_HEIGHT))
        self._surface.blit(text_surface, (top_left_pixel_x + self._surface.get_width() * 0.020, top_left_pixel_y + self._surface.get_height() * 0.06))

    def _draw_board_box(self):
        """
        Draws the game board (inner box)
        """
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
        """
        Loops through each jewel, determines the linked color, dimensions, and coordinates
        and class draw_jewel function
        """
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
        """
        Draws each jewel, color is the image that should be blit on the jewel
        Draws the grid, by drawing an outline of width 1 on every empty cell
        """
        width = _JEWEL_WIDTH * self._surface.get_width()
        height = _JEWEL_HEIGHT * self._surface.get_height()
        jewel_rect = pygame.Rect(top_left_pixel_x, top_left_pixel_y, width, height)
        if status != game_logic.Cell.empty_cell and status != game_logic.Cell.landed_cell:
            self._assign_image(jewel_rect, width, height, color) #color is the image
        else:
            pygame.draw.rect(self._surface, color, jewel_rect)
        if status == game_logic.Cell.empty_cell:
            pygame.draw.rect(self._surface, _GRID, jewel_rect, 1)
        else:
            pygame.draw.rect(self._surface, _BACKGROUND_COLOR, jewel_rect, 1)

    def _add_faller(self) -> None:
        """
        Add a faller to the board if there is no faller present
        Faller is strictly created on a column that is not all filled with frozen jewels unless there is no
        """
        if self._state.get_faller() == None:
                faller_colors = self._random_colors()
                faller_column = self._random_column()
                while self._state.get_board_cell(2, faller_column).get_status() != game_logic.Cell.empty_cell:
                    faller_column = self._random_column()
                    rows = []
                    for row in self._state.get_board()[0:3]:
                        row.append(row)
                    if ' ' not in rows:
                        faller_column = self._random_column()
                        break
                self._state.add_faller_to_board(faller_column, faller_colors[0],
                                                faller_colors[1], faller_colors[2])

    def _handle_events(self) -> None:
        """
        Handles each pygame event
        Pressing space, right arrow and left arrow triggers a sound
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False
            if event.type == pygame.VIDEORESIZE:
                self._create_surface(event.size)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self._state.rotate_faller()
                self._play_sound('move')
            if event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                self._state.move_left()
                self._play_sound('move')
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                self._state.move_right()
                self._play_sound('move')

    def _play_sound(self, str):
        """
        Plays the sound depending on the action
        """
        if str == 'move':
            self._sound_left_right.play()
        elif str == 'fall':
            self._sound_fall.play()
        elif str == 'game over':
            self._sound_game_over.play()

    def _assign_image(self, jewel_rect, width, height, color) -> None:
        """
        Assigns an image to each jewel depending on the letter-color
        """
        scaled_image = pygame.transform.scale(color, (int(width), int(height)))
        self._surface.blit(scaled_image, jewel_rect)

    def _random_colors(self) -> list:
        """
        Generates three random colors for each jewel of a faller
        """
        faller_colors = []
        for jewel in range(_FALLER):
            faller_colors.append(random.choice(LETTER_COLORS))
        return faller_colors

    def _random_column(self) -> int:
        """
        Generates a random integer between 0 and 5 for a faller column
        """
        return random.randint(0, _COLUMN_NUM-1)


if __name__ == '__main__':
    ColumnsGame().run()