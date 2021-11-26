#user_interface.py
import game_logic

def _user_input():
    num_rows = int(input())
    num_columns = int(input())
    empty_or_not = input()
    list_of_rows = []
    if empty_or_not == 'CONTENTS':
        empty = False
        for r in range(num_rows):
            one_row = input()
            list_of_rows.append(one_row)
    elif empty_or_not == 'EMPTY':
        empty = True
    else:
        exit()
    new_list = []
    for row in list_of_rows:
        list_ = []
        for char in row:
            list_.append(char)
        new_list.append(list_)
    return num_rows, num_columns, empty,  new_list


def ask_for_line():
    return input()

def user_choice(choice, gameboard: game_logic.GameBoard) -> None:
    if choice.startswith('Q'):
        exit()
    if choice.startswith('F'):
        if gameboard.get_faller() == None:
            faller_column = int(choice[2]) - 1
            top = choice[4]
            middle = choice[6]
            bottom = choice[8]
            column_filled = gameboard.add_faller_to_board(faller_column, top, middle, bottom)
            return column_filled
    elif choice.startswith('R') and gameboard.get_faller():
        gameboard.rotate_faller()
    elif choice.startswith('<') and gameboard.get_faller():
        gameboard.move_left()
    elif choice.startswith('>') and gameboard.get_faller():
        gameboard.move_right()
    else:
        exit()


def draw_board(gameboard: game_logic.GameBoard) -> None:
    board = gameboard.get_board()
    for row in range(2, gameboard.get_rows()):
        to_print = ''
        print('|', end = '')
        for col in range(gameboard.get_columns()):
            cell = board[row][col]
            status = cell.get_status()
            value = cell.get_value()
            if status == game_logic.Cell.empty_cell:
                to_print += game_logic.SPACE * 3
            elif status == game_logic.Cell.jewel_cell:
                to_print += game_logic.SPACE + value + game_logic.SPACE
            elif status == game_logic.Cell.falling_cell:
                to_print += f'[{value}]'
            elif status == game_logic.Cell.landed_cell:
                to_print += f'|{value}|'
            elif status == game_logic.Cell.match:
                to_print += f'*{value}*'
        print(to_print + '|')
    print(f" {3*gameboard.get_columns() * '-' + ' '}")


