from user_interface import _user_input, ask_for_line, draw_board, user_choice
import game_logic


def run():
    num_rows, num_columns, empty, contents_list = _user_input()
    gameboard = game_logic.GameBoard(num_rows, num_columns)
    gameboard.set_board(empty, contents_list)
    game_over = False
    while not game_over:
        draw_board(gameboard)
        break_line = ask_for_line()
        if break_line == '':
            gameboard.action()
            if gameboard.get_game_over():
                game_over = True
        else:
            column_filled = user_choice(break_line, gameboard)
            if column_filled == 'game over':
                game_over = True
    draw_board(gameboard)
    print('GAME OVER')



if __name__ == '__main__':
    run()


