import time
from typing import Literal

from fasthtml.common import *
from pydantic import BaseModel

app, rt = fast_app(
    pico=True,
    exts='ws'
)

class Cell(BaseModel):
    value: Literal["X", "O"] | None = None
    pos_x: int | None = None
    pos_y: int | None = None

    @property
    def id(self):
        return f'cell-{self.pos_x}-{self.pos_y}'

    def __ft__(self):
        return Div(Div(Span(self.value, style={'color': 'blue' if self.value == 'X' else 'red'}), id=f'{self.id}-value',
                     style={'display': 'flex', 'justify-content': 'center', 'width': '100%', 'height': '100%', 'align-items': 'center'},
                    hx_trigger='click', hx_target=f'#game-state', hx_swap="innerHTML", hx_get='/check-state'),
                   id=self.id, style={'width': '50px', 'height': '50px', 'border': '1px solid'},
                   hx_trigger='click', hx_target=f'#{self.id}-value', hx_swap="innerHTML", hx_put='/change',
                   hx_vals={'x': self.pos_x, 'y': self.pos_y})


class Board:
    def __init__(self):
        self.cells = [[Cell(pos_x=x, pos_y=y) for y in range(3)] for x in range(3)]

    def __getitem__(self, x):
        return self.cells[x]

    def change(self, x: int, y: int, value: str):
        if self[x][y].value:
            return self[x][y].value, False

        self[x][y].value = value
        return value, True

    def restart_board(self):
        for row in self.cells:
            for cell in row:
                cell.value = None

    def check_completed_rows(self):
        for row in self.cells:
            if all(cell.value == row[0].value for cell in row) and row[0].value is not None:
                return row[0].value
        return None

    def check_completed_columns(self):
        for col in range(3):
            if all(self[row][col].value == self[0][col].value for row in range(3)) and self[0][col].value is not None:
                return self[0][col].value
        return None

    def check_completed_diagonals(self):
        if all(self[i][i].value == self[0][0].value for i in range(3)) and self[0][0].value is not None:
            return self[0][0].value
        if all(self[i][2-i].value == self[0][2].value for i in range(3)) and self[0][2].value is not None:
            return self[0][2].value
        return None

    def check_state(self):
        winner = self.check_completed_rows() or self.check_completed_columns() or self.check_completed_diagonals()
        if winner:
            return f"{winner} wins!"
        elif all(cell.value is not None for row in self.cells for cell in row):
            return "It's a draw!"
        else:
            return ""

    def __ft__(self):
        return Div(*[
            Div(*[cell for cell in row], style={"width": 'fit-content', 'display': 'grid', 'grid-template-columns': 'repeat(3, 50px)'}) for row in self.cells
        ],
        Div(id="game-state", style={"display": "flex", "justify-content": "center"}),
        id='board', style={'width': 'fit-content', 'margin': 'auto', 'padding': '10px'})

class Game:
    def __init__(self):
        self.board = Board()
        self.current_value = "X"
        self.ended = False

    def change(self, x: int, y: int):
        if self.ended:
            return self.board[x][y].value

        prev_value, changed = self.board.change(x, y, self.current_value)
        if changed:
            self.current_value = "X" if prev_value == "O" else "O"
        return prev_value

    def restart_game(self):
        self.board.restart_board()
        self.current_value = "X"
        self.ended = False

    def check_state(self):
        winner = self.board.check_state()
        if winner:
            self.ended = True
        return winner

    def __ft__(self):
        return Div(self.board,
                   Button("Restart", id='restart', hx_post='/new', hx_target='#board', hx_swap='outerHTML', style={'margin': 'auto', 'display': 'block'}))

game = Game()

@rt('/')
async def get():
   return game

@rt('/change')
async def put(x:int, y:int):
    value = game.change(x, y)
    return Span(value, style={'color': 'blue' if value == 'X' else 'red'})
    # return game.change(x, y)

@rt('/check-state')
async def get():
    time.sleep(0.02)
    return game.check_state()

@rt('/new')
async def post():
    game.restart_game()
    return game.board

serve()
