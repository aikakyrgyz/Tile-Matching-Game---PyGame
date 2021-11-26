import unittest
import random
from game_logic import *
import project4

class GameBoardTest(unittest.TestCase):

    def test_board_list_has_size_zero_when_initilized(self):
        gameboard = self._create_test_gameboard()
        self.assertEqual(len(gameboard.get_board()), 0)

    def test_empty_board_has_all_cells_with_value_empty(self):
        gameboard = self._create_test_gameboard()
        gameboard.set_board(True, [])
        for row in gameboard.get_board():
            for col in row:
                self.assertEqual(col.get_status(), Cell.empty_cell)
    #
    # def test_contents_of_board_set_properly_without_filling_blanks(self):
    #     gameboard = self._create_test_gameboard()
    #     contents = self._create_list_of_contents(gameboard.get_rows(), gameboard.get_columns())
    #     gameboard.set_board(False, contents)
    #     for row in range(gameboard.get_rows()):
    #         for col in range(gameboard.get_columns()):
    #             self.assertEqual(gameboard.get_board()[row][col].get_value(), contents[row][col])

    # def test_contents_of_board_set_properly_with_filling_blanks_right_away(self):
    #     gameboard = self._create_test_gameboard()
    #     contents = self._create_list_of_contents(gameboard.get_rows(), gameboard.get_columns())
    #     gameboard.set_board(False, contents)
    #     contents = self._fill_blanks(contents)
    #     for row in range(gameboard.get_rows()):
    #         for col in range(gameboard.get_columns()):
    #             self.assertEqual(gameboard.get_board()[row][col].get_value(), contents[row][col])
    def test_match_is_found_right_away_with_given_contents(self):
        gameboard = GameBoard(4, 4)
        gameboard.set_board(False, [[' ', 'Y', ' ', 'X'], ['S', ' ', 'V', ' '], ['T', 'X', 'Y', 'S'], ['X', ' ', 'X', 'Y']])
        # project4.draw_board(gameboard)
    def test_match_is_found_right_away_with_given_contents2(self):
        gameboard = GameBoard(4, 4)
        gameboard.set_board(False,
                            [['X', 'X', 'X', 'X'], [' ', 'S', 'V', 'V'], ['T', 'X', 'S', 'S'], ['X', ' ', 'X', 'V']])
        # project4.draw_board(gameboard)

    def test_match_is_found_right_away_with_given_contents3(self):
        gameboard = GameBoard(4, 4)
        gameboard.set_board(False,
                            [['X', 'X', 'X', 'V'], ['Y', 'Y', 'Y', 'T'], ['Z', 'S', 'S', 'S'], [' ', ' ', ' ', ' ']])
        # project4.draw_board(gameboard)
    def test_match_horizontally(self):
        gameboard = GameBoard(4, 4)
        gameboard.set_board(False,
                            [['X', 'Y', 'X', 'V'], ['T', 'Y', 'Y', 'W'], ['Z', 'Y', 'W', 'W'], [' ', ' ', ' ', ' ']])
        # project4.draw_board(gameboard)
    def test_faller_is_created(self):
        gameboard = GameBoard(4, 4)
        gameboard.set_board(True, [])
        gameboard.add_faller_to_board('F 3 X Y Z')
        self.assertEqual(gameboard.get_faller().get_faller(), ['Z', 'Y', 'X'])
        self.assertEqual(gameboard.get_faller().get_status(), Faller.falling_status)
        self.assertEqual(gameboard.get_faller().get_column(), 2)
        self.assertEqual(gameboard.get_faller().get_bottom_piece_row(), 2)

    def test_fallers_bottom_jewel_is_on_row_one_and_column_given(self):
        gameboard = GameBoard(4, 4)
        gameboard.set_board(True, [])
        gameboard.add_faller_to_board('F 3 X Y Z')
        self.assertEqual(gameboard.get_faller().get_faller(), ['Z', 'Y', 'X'])
        self.assertEqual(gameboard.get_board()[0][gameboard.get_faller().get_column()].get_value(), 'X')
        self.assertEqual(gameboard.get_board()[0][gameboard.get_faller().get_column()].get_status(), Cell.falling_cell)
        self.assertEqual(gameboard.get_board()[1][gameboard.get_faller().get_column()].get_value(), 'Y')
        self.assertEqual(gameboard.get_board()[1][gameboard.get_faller().get_column()].get_status(), Cell.falling_cell)
        self.assertEqual(gameboard.get_board()[2][gameboard.get_faller().get_column()].get_value(), 'Z')
        self.assertEqual(gameboard.get_board()[2][gameboard.get_faller().get_column()].get_status(), Cell.falling_cell)

    def test_faller_keeps_moving_down(self):
        gameboard = GameBoard(4, 4)
        gameboard.set_board(True, [])
        gameboard.add_faller_to_board('F 1 X Y Z')
        for i in range(7):
            gameboard.action()
        self.assertEqual(gameboard.get_board_cell(4, 0).get_value(), 'Y')
        self.assertEqual(gameboard.get_board_cell(3, 0).get_value(), 'X')
        self.assertEqual(gameboard.get_board_cell(5, 0).get_value(), 'Z')
        self.assertEqual(gameboard.get_faller(), None)

    def _create_test_gameboard(self):
        return GameBoard(random.randint(4, 10), random.randint(3, 10))

    def _create_a_cell(self, row, column, cell, state):
        return Cell(row, column, cell, state)

    def _create_list_of_contents(self, rows, cols):
        contents = []
        possible_inputs = ['S', 'T', 'V', 'W', 'X', 'Y', 'Z', ' ']
        for row in range(rows):
            one_row = []
            for col in range(cols):
                one_row.append(random.choice(possible_inputs))
            contents.append(one_row)
        return contents

if __name__ == '__main__':
    unittest.main()
