# game_logic.py
import copy

MIN_ROWS = 4
MIN_COLUMNS = 3
SPACE = ' '
FIELD_COLORS = ['S', 'T', 'V', 'W', 'X', 'Y', 'Z', ' ']
FALLER_COLORS = ['S', 'T', 'V', 'W', 'X', 'Y', 'Z']


class Faller:
    falling_status = 'falling'
    freeze_status = 'freeze'
    landed_status = 'landed'

    def __init__(self, column, top, middle, bottom):
        self._column = column
        self._status = Faller.falling_status
        self._top_piece = top
        self._middle_piece = middle
        self._bottom_piece = bottom
        self._bottom_piece_row = 2
        self._faller = [self._bottom_piece, self._middle_piece, self._top_piece]
        self._require_valid_faller(self._faller)

    def get_status(self) -> str:
        return self._status

    def set_status(self, status) -> None:
        self._status = status

    def set_column(self, column) -> None:
        self._column = column

    def get_column(self) -> int:
        return self._column

    def get_faller(self) -> list:
        return self._faller

    def get_top_piece(self):
        return self._top_piece

    def get_middle_piece(self):
        return self._middle_piece

    def get_bottom_piece(self):
        return self._bottom_piece

    def get_bottom_piece_row(self) -> int:
        return self._bottom_piece_row

    def move_down_bottom_piece(self) -> None:
        self._bottom_piece_row += 1

    def rotate(self) -> None:
        temp_top = self._top_piece
        self._top_piece = self._bottom_piece
        self._bottom_piece = self._middle_piece
        self._middle_piece = temp_top
        self._faller = [self._bottom_piece, self._middle_piece, self._top_piece]

    def _require_valid_faller(self, contents: list[list]) -> None:
        for color in contents:
            if color not in FALLER_COLORS:
                raise ValueError('The colors can only be S, T, V, W, X, Y, Z')


class Cell:
    empty_cell = 'empty cell'
    jewel_cell = 'jewel cell'
    landed_cell = 'landed cell'
    freeze_cell = 'freeze cell'
    falling_cell = 'falling cell'
    match = 'match'

    def __init__(self, row: int, col: int, value: str, status: str):
        self._row = row
        self._column = col
        self._value = value
        self._status = status

    def set_value(self, new_value: str) -> None:
        self._value = new_value

    def set_status(self, status: str) -> None:
        self._status = status

    def get_value(self) -> str:
        return self._value

    def get_status(self) -> str:
        return self._status

    def get_row(self) -> int:
        return self._row

    def get_column(self) -> int:
        return self._column


class GameBoard:
    def __init__(self, rows: int, columns: int):
        self._rows = rows
        self._columns = columns
        self._board = []
        self._require_valid_column_start(columns)
        self._require_valid_row_start(rows)
        self._faller = None
        self._game_over = False
        self._matching_cells_present = False
        self._match_score = 3

    def get_rows(self) -> int:
        return self._rows

    def get_columns(self) -> int:
        return self._columns

    def get_board(self) -> list[list]:
        return self._board

    def get_board_cell(self, row: int, col: int) -> Cell or None:
        if row < self._rows and col < self._columns:
            return self._board[row][col]

    def get_faller(self) -> Faller:
        return self._faller

    def get_score(self) -> int:
        return self._match_score

    def get_game_over(self) -> bool:
        return self._game_over


    def set_board(self, empty: bool, contents_list: list) -> None:
        '''
        Sets the initial board, if empty is True then it will set at the cells empty
        If the contents are given then sets the board wth the given contents and filles the blanks afterward
        Then looks for a match and adjusts the board
        '''
        if empty:
            self._board = []
            for row in range(self._rows):
                each_row = []
                for col in range(self._columns):
                    cell = Cell(row + 2, col, SPACE, Cell.empty_cell)
                    each_row.append(cell)
                self._board.append(each_row)
        else:
            self._require_valid_contents(contents_list)
            for row in range(self._rows):
                each_row = []
                for col in range(self._columns):
                    content = contents_list[row][col]
                    if content is SPACE:
                        cell = Cell(row + 2, col, SPACE, Cell.empty_cell)
                    else:
                        cell = Cell(row + 2, col, content, Cell.jewel_cell)
                    each_row.append(cell)
                self._board.append(each_row)

        row_middle_piece = []
        row_top_piece = []
        for i in range(0, self.get_columns()):
            empty_cell = Cell(1, i, SPACE, Cell.empty_cell)
            row_middle_piece.append(empty_cell)
        for i in range(0, self.get_columns()):
            empty_cell = Cell(0, i, SPACE, Cell.empty_cell)
            row_top_piece.append(empty_cell)
        self._board.reverse()
        self._board.append(row_middle_piece)
        self._board.append(row_top_piece)
        self._board.reverse()
        self._rows += 2

        self.fill_blanks()
        self._find_match()

    def fill_blanks(self) -> None:
        '''
        If the cell is empty and there is non-empty cell above it,
        The jewel above fills the blank cell
        '''
        # if self._faller is None:
        for row in range(self._rows):
            for row in range(self._rows - 1, 0, -1):
                for col in range(self._columns):
                    if self.get_board_cell(row, col).get_status() == Cell.empty_cell:
                        non_empty_cell_above = self._board[row - 1][col]
                        if non_empty_cell_above.get_status() == Cell.falling_cell or non_empty_cell_above.get_status() == Cell.landed_cell:
                            continue
                        self._board[row][col].set_value(non_empty_cell_above.get_value())
                        self._board[row][col].set_status(non_empty_cell_above.get_status())
                        self._board[row - 1][col].set_value(SPACE)
                        self._board[row - 1][col].set_status(Cell.empty_cell)

    def _check_above_rows_unmatched(self) -> bool:
        '''
        Checks if the frozen faller fit in the board
        After matching and blanked were filled
        If there are still jewel cells on the board then return False otherwise True
        '''
        first_row = False
        second_row = False
        empty = False
        jewel = self.get_board_cell(0, 0).get_status()
        if jewel == Cell.empty_cell:
            equal = True
            for each in self._board[0]:
                if jewel != each.get_status():
                    equal = False
                    break
            if equal:
                first_row = True
        jewel = self.get_board_cell(1, 0).get_status()
        if jewel == Cell.empty_cell:
            equal = True
            for each in self._board[1]:
                if jewel != each.get_status():
                    equal = False
                    break
            if equal:
                second_row = True
        if second_row and first_row:
            empty = True
        return empty

    def action(self) -> None:
        '''
        Takes the appropriate action while the faller is in progress,
        depending on the state of the faller. Checks for matching cells and deletes them if found
        Fills in the blanks if necessary
        Determines if the game was over
        '''
        self._check_if_matching_cells()
        if self._faller is None:
            self._find_match()
            if self._check_above_rows_unmatched():
                self._game_over = False
            else:
                self._game_over = True
        if self._faller:
            if self._faller.get_status() == Faller.landed_status:
                self._faller_landed()
                self._find_match()
            elif self._faller.get_status() == Faller.falling_status:
                self._keep_falling()
        self._matching_cells_present = False


    def add_faller_to_board(self, column, top, middle, bottom) -> None:
        '''
        Adds the faller to the board with the specified color in contents
        '''

        self._faller = Faller(column, top, middle, bottom)
        column_faller = self._faller.get_column()
        middle_piece = self._faller.get_middle_piece()
        top_piece = self._faller.get_top_piece()
        if self.get_board_cell(2, column_faller).get_status() == Cell.empty_cell:
            top_faller_cell = self.get_board_cell(0, column_faller)
            top_faller_cell.set_value(top_piece)
            top_faller_cell.set_status(Cell.falling_cell)
            middle_faller_cell = self.get_board_cell(1, column_faller)
            middle_faller_cell.set_value(middle_piece)
            middle_faller_cell.set_status(Cell.falling_cell)
            bottom_cell = self.get_board_cell(2, self._faller.get_column())
            bottom_cell.set_value(self._faller.get_bottom_piece())
            bottom_cell.set_status(Cell.falling_cell)
            self._check_the_floor()
        else:
            return 'game over'

    def _check_the_floor(self) -> None:
        '''
        If there is a landing ground below the bottom jewel of the faller
        Then the status of the jewel is changed to 'landed status'
        And the cell values are changed to the faller jewels
        If there is not a landing ground then the 'falling status' REMAINS
        But the cell values are changed to the faller jewels
        '''

        landing_row = self._faller.get_bottom_piece_row() + 1
        jewels = self._get_jewels_on_board()
        j = 0
        if landing_row >= self.get_rows() \
                or self.get_board_cell(landing_row, self._faller.get_column()).get_status() == Cell.jewel_cell:
            self._faller._status = Faller.landed_status
            for jewel_cell in jewels:
                jewel_cell.set_status(Cell.landed_cell)
                jewel_cell.set_value(self._faller.get_faller()[j])
                j += 1
        else:
            self._faller._status = Faller.falling_status
            for jewel_cell in jewels:
                jewel_cell.set_status(Cell.falling_cell)
                jewel_cell.set_value(self._faller.get_faller()[j])
                j += 1

    def _keep_falling(self) -> None:
        '''
        Moves the faller down a row
        Swaps the value accordingly:
        Cell of the next row of the faller's column becomes the bottom piece of the faller
        Cell of the previous bottom piece becomes the middle piece
        Cell of the previous middle piece becomes the top piece
        If the faller lands then adjusts the status of each cell
        '''
        if self._faller.get_status() != Faller.landed_status:
            if self._faller.get_bottom_piece_row() >= self.get_rows():
                return
            else:
                landing_row = self._faller.get_bottom_piece_row() + 1
                landing_cell = self.get_board_cell(landing_row, self._faller.get_column())
            if landing_cell.get_status() != Cell.jewel_cell:
                landing_row = self._faller.get_bottom_piece_row() + 1
                bottom_jewel = self.get_board_cell(self._faller.get_bottom_piece_row(), self._faller.get_column())
                middle_jewel = self.get_board_cell(self._faller.get_bottom_piece_row() - 1, self._faller.get_column())
                top_jewel = self.get_board_cell(self._faller.get_bottom_piece_row() - 2, self._faller.get_column())
                self.get_board_cell(landing_row, self._faller.get_column()).set_value(bottom_jewel.get_value())
                self.get_board_cell(landing_row, self._faller.get_column()).set_status(bottom_jewel.get_status())
                self.get_board_cell(landing_row - 1, self._faller.get_column()).set_value(middle_jewel.get_value())
                self.get_board_cell(landing_row - 1, self._faller.get_column()).set_status(middle_jewel.get_status())
                self.get_board_cell(landing_row - 2, self._faller.get_column()).set_value(top_jewel.get_value())
                self.get_board_cell(landing_row - 2, self._faller.get_column()).set_status(top_jewel.get_status())
                self.get_board_cell(landing_row - 3, self._faller.get_column()).set_value(SPACE)
                self.get_board_cell(landing_row - 3, self._faller.get_column()).set_status(Cell.empty_cell)
                self._faller.move_down_bottom_piece()
                self._check_the_floor()

    def _faller_landed(self):
        '''
        If the faller has landed, but did not fit in the board then _game_over is set to True and we exit the game
        If the faller has landed, then changes the state of the faller's cells to frozen jewel cells
        Sets the faller attribute to None after it has landed so that a new faller is available to create
        Rearranges the board if there are matching cells
        '''
        self._check_the_floor()
        if self._faller.get_status() == Faller.landed_status:
            if self._faller.get_bottom_piece_row() < 5:
                self._game_over = True
            bottom_jewel = self.get_board_cell(self._faller.get_bottom_piece_row(), self._faller.get_column())
            middle_jewel = self.get_board_cell(self._faller.get_bottom_piece_row() - 1, self._faller.get_column())
            top_jewel = self.get_board_cell(self._faller.get_bottom_piece_row() - 2, self._faller.get_column())
            for jewel in (bottom_jewel, middle_jewel, top_jewel):
                self._board[jewel.get_row()][jewel.get_column()].set_value(jewel.get_value())
                self._board[jewel.get_row()][jewel.get_column()].set_status(Cell.jewel_cell)
            self._faller = None
            self._find_match()
            empty = self._invisible_match()
            if empty:
                self._game_over = False

    def _invisible_match(self):
        '''
        Determines if there was a match that led for the game to be 'saved'
        If the game can be saved return True, otherwise returns False
        '''
        copy_board = copy.deepcopy(self._board)
        for row in range(self._rows):
            for col in range(self._columns):
                if copy_board[row][col].get_status() == Cell.match:
                    copy_board[row][col].set_value(SPACE)
                    copy_board[row][col].set_status(Cell.empty_cell)
        if self._faller is None:
            for row in range(self._rows):
                for row in range(self._rows - 1, 0, -1):
                    for col in range(self._columns):
                        if copy_board[row][col].get_status() == Cell.empty_cell:
                            non_empty_cell_above = copy_board[row - 1][col]
                            copy_board[row][col].set_value(non_empty_cell_above.get_value())
                            copy_board[row][col].set_status(non_empty_cell_above.get_status())
                            copy_board[row - 1][col].set_value(SPACE)
                            copy_board[row - 1][col].set_status(Cell.empty_cell)
        first_row = False
        second_row = False
        empty = False
        jewel = copy_board[0][0].get_status()
        if jewel == Cell.empty_cell:
            equal = True
            for each in copy_board[0][:-1]:
                if jewel != each.get_status():
                    equal = False
                    break
            if equal:
                first_row = True
        jewel = copy_board[1][0].get_status()
        if jewel == Cell.empty_cell:
            equal = True
            for each in copy_board[1][:-1]:
                if jewel != each.get_status():
                    equal = False
                    break
            if equal:
                second_row = True
        if second_row and first_row:
            empty = True

        return empty

    def _get_jewels_on_board(self) -> list:
        '''
        Return the jewels that are visible on the board
        '''
        jewels = []
        bottom_jewel = self.get_board_cell(self._faller.get_bottom_piece_row(), self._faller.get_column())
        jewels.append(bottom_jewel)
        middle_jewel = self.get_board_cell(self._faller.get_bottom_piece_row() - 1, self._faller.get_column())
        jewels.append(middle_jewel)
        top_jewel = self.get_board_cell(self._faller.get_bottom_piece_row() - 2, self._faller.get_column())
        jewels.append(top_jewel)
        return jewels

    def rotate_faller(self) -> None:
        'Rotates the faller'
        if self._faller:
            self._faller.rotate()
            self.get_board_cell(self._faller.get_bottom_piece_row(), self._faller.get_column()).set_value(
                self._faller.get_bottom_piece())
            self.get_board_cell(self._faller.get_bottom_piece_row() - 1, self._faller.get_column()).set_value(
                self._faller.get_middle_piece())
            self.get_board_cell(self._faller.get_bottom_piece_row() - 2, self._faller.get_column()).set_value(
                self._faller.get_top_piece)
            self._check_the_floor()

    def move_left(self) -> None:
        'Moves the faller to the left'
        if self._faller:
            left_side_column = self._faller.get_column() - 1
            if self._check_if_empty_column(left_side_column):
                self._move_to_the_side(left_side_column)

    def move_right(self) -> None:
        if self._faller:
            'Moves the faller to the right'
            right_side_column = self._faller.get_column() + 1
            if self._check_if_empty_column(right_side_column):
                self._move_to_the_side(right_side_column)

    def _check_if_empty_column(self, side_column: int) -> bool:
        '''
        If the faller cannot be moved because either it is already on the edge
        Or if the column requested to move to is already occupied by other jewels
        Then return False Else return True
        '''
        if side_column >= 0 and side_column < self.get_columns():
            bottom_cell = self.get_board_cell(self._faller.get_bottom_piece_row(), side_column)
            bottom_status = bottom_cell.get_status()
            if bottom_cell.get_row() == 0:
                middle_status = Cell.empty_cell
                top_status = Cell.empty_cell
            else:
                middle_cell = self.get_board_cell(self._faller.get_bottom_piece_row() - 1, side_column)
                middle_status = middle_cell.get_status()
                if middle_cell.get_row() == 0:
                    top_status = Cell.empty_cell
                else:
                    top_cell = self.get_board_cell(self._faller.get_bottom_piece_row() - 2, side_column)
                    top_status = top_cell.get_status()
            if bottom_status == Cell.empty_cell and middle_status == Cell.empty_cell and top_status == Cell.empty_cell:
                return True
        else:
            return False

    def _move_to_the_side(self, side_column: int) -> None:
        'Moves the faller to the given column'
        for row in range(len(self._faller.get_faller())):
            cell = self.get_board_cell(self._faller.get_bottom_piece_row() - row, self._faller.get_column())
            self.get_board_cell(cell.get_row(), side_column).set_value(cell.get_value())
            self.get_board_cell(cell.get_row(), side_column).set_status(cell.get_status())
            self.get_board_cell(cell.get_row(), cell.get_column()).set_value(SPACE)
            self.get_board_cell(cell.get_row(), cell.get_column()).set_status(Cell.empty_cell)
        self._faller.set_column(side_column)
        self._check_the_floor()

    def _find_match(self) -> None:
        '''
        Finds matching cells in three directions:
        1. Horizontally
        2. Vertically
        3. Diagonally (Not finished)
        '''

        self._horizontal_match()
        self._vertical_match()
        # self._diagonal_match()

    def _horizontal_match(self):
        empty = Cell(-1000, -1000, 0, Cell.empty_cell)
        match_jewels = [empty]
        for row in range(self._rows - 1, -1, -1):
            for col in range(self._columns):
                next_jewel = self.get_board_cell(row, col)
                if next_jewel.get_value() == match_jewels[-1].get_value() and (
                        next_jewel.get_status() != Cell.empty_cell or next_jewel.get_status() == Cell.match):
                    match_jewels.append(next_jewel)
                    if len(match_jewels) >= 3:
                        for jewel in match_jewels:
                            self._match_score += 1
                            jewel_row = jewel.get_row()
                            jewel_col = jewel.get_column()
                            self._board[jewel_row][jewel_col].set_status(Cell.match)
                        # self._matching_cells_present = True
                        match_jewels = [empty]
                else:
                    # print([i.get_value() for i in match_jewels])
                    if col == self._columns - 1:
                        if len(match_jewels) >= 3:
                            for jewel in match_jewels:
                                self._match_score += 1
                                jewel_row = jewel.get_row()
                                jewel_col = jewel.get_column()
                                self._board[jewel_row][jewel_col].set_status(Cell.match)
                            self._matching_cells_present = True
                        # else:
                        #     self._matching_cells_present = False
                    match_jewels = []
                    match_jewels.append(next_jewel)


    def _vertical_match(self):
        empty = Cell(-4, -4, 0, Cell.empty_cell)
        match_jewels = []
        match_jewels.append(empty)
        for col in range(self._columns):
            for row in range(self._rows - 1, -1, -1):
                next_jewel = self.get_board_cell(row, col)
                if next_jewel.get_value() == match_jewels[-1].get_value() and (
                        next_jewel.get_status() != Cell.empty_cell or next_jewel.get_status() == Cell.match):
                    match_jewels.append(next_jewel)
                    if row == 0:
                        if len(match_jewels) >= 3:
                            for jewel in match_jewels:
                                jewel_row = jewel.get_row()
                                jewel_col = jewel.get_column()
                                self._board[jewel_row][jewel_col].set_status(Cell.match)
                            # self._matching_cells_present = True
                            match_jewels = [empty]
                else:
                    if len(match_jewels) >= 3:
                        for jewel in match_jewels:
                            self._match_score += 1
                            jewel_row = jewel.get_row()
                            jewel_col = jewel.get_column()
                            self._board[jewel_row][jewel_col].set_status(Cell.match)
                        # self._matching_cells_present = True


                    match_jewels = []
                    match_jewels.append(next_jewel)
    def get_matching_cells_present(self):
        return self._matching_cells_present

    def _diagonal_match(self):
        'Finds matched cells diagonally'
        # DIAGONALLY
        # have not finished implementing
        '''
        print('diagonally')
        empty = Cell(-4, -4, 0, Cell.empty_cell)
        match_jewels = []
        match_jewels.append(empty)
        for row in range(self._rows):
            move_row = 0
            move_column = 0
            for col in range(self._columns):
                    if move_column == self._columns - 2 - 1 or to_check_row == row:
                        break
                    next_jewel = self.get_board_cell(to_check_row, to_check_col)
                    print(next_jewel)
                    if next_jewel.get_value() == match_jewels[-1].get_value() and (
                        next_jewel.get_status() != Cell.empty_cell or next_jewel.get_status() == Cell.match):
                        match_jewels.append(next_jewel)
                    else:
                        if len(match_jewels) >= 3:
                            for jewel in match_jewels:
                                jewel_row = jewel.get_row()
                                jewel_col = jewel.get_column()
                                self._board[jewel_row][jewel_col].set_status(Cell.match)
                            match_jewels = [empty]
                        match_jewels = []
                        match_jewels.append(next_jewel)
                    move_column+=1
                    move_row+=1
        '''

    def _check_if_matching_cells(self) -> None:
        'Cells that are matched will be deleted (filled with a space)'
        for row in range(self._rows):
            for col in range(self._columns):
                if self._board[row][col].get_status() == Cell.match:
                    self._matching_cells_present = True
                    self._board[row][col].set_value(SPACE)
                    self._board[row][col].set_status(Cell.empty_cell)
        self.fill_blanks()

    def _require_valid_column_start(self, columns: int) -> None:
        '''Raises a ValueError if the given number of columns is invalid.'''
        if columns < MIN_COLUMNS:
            raise ValueError(f'columns must be an int greater than {MIN_COLUMNS}')

    def _require_valid_row_start(self, rows: int) -> None:
        '''Raises a ValueError if the given number of rows is invalid.'''
        if rows < MIN_ROWS:
            raise ValueError(f'rows must be an int greater {MIN_ROWS}')

    def _require_valid_contents(self, contents: list[list]) -> None:
        if contents != []:
            for row in contents:
                for color in row:
                    if color not in FIELD_COLORS:
                        raise ValueError(f'The colors can only be S, T, V, W, X, Y, Z')
