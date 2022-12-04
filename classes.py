from random import randint
# from outter_logic import *
class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    def __repr__(self):
        return f"Dot({self.x}, {self.y})"


class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь  выстрелить за пределы доски!"

class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"

class BoardWrongShipException(BoardException):
    pass

class Ship:
    def __init__(self, bow, length, direction):
        self.bow = bow
        self.length = length
        self.direction = direction
        self.lives = length


    @property
    def dots(self):
        ship_dots = []
        for i in range(self.length):
            current_x = self.bow.x
            current_y = self.bow.y

            if self.direction == 1:
                current_x += i

            else:
                current_y += i

            ship_dots.append(Dot(current_x, current_y))
        return ship_dots
    def shooten(self, shot):
        return shot in self.dots

class Board:
    def __init__(self, hid = False, size = 6):
        self.size = size
        self.hid = hid
        self.count = 0
        self.field = [["O"] * size for _ in range(size)]
        self.busy = []
        self.ships = []

    def __str__(self):
        res = " "
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n {i+1} | " + " | ".join(row) + " |"
        if self.hid:
            res = res.replace("*", "O")
        return res

    def out(self, dot):
        return not ((0 <= dot.x < self.size) and (0 <= dot.y < self.size))

    def add_ship(self, ship):
        for dot in ship.dots:
            if self.out(dot) or dot in self.busy:
                raise BoardWrongShipException()

        for dot in ship.dots:
            self.field[dot.x][dot.y] = "*"
            self.busy.append(dot)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)
        ]

        for dot in ship.dots:
            for dx, dy in near:
                current = Dot(dot.x + dx, dot.y + dy)
                if not(self.out(current)) and current not in self.busy:
                    if verb:
                        self.field[current.x][current.y] = "."
                    self.busy.append(current)


    def shot(self, dot):
        if self.out(dot):
            raise BoardOutException()
        if dot in self.busy:
            raise BoardUsedException()

        self.busy.append(dot)

        for ship in self.ships:
            if ship.shooten(dot):
                ship.lives -= 1
                self.field[dot.x][dot.y] = "!"
                if ship.lives == 0:
                    self.contour(ship, verb=True)
                    self.count += 1
                    for dot in ship.dots:
                        self.field[dot.x][dot.y] = "X"
                    print("Ship destroyed")
                    return False
                else:
                    print("Ship is hitted!")
                    return True
        self.field[dot.x][dot.y] = "."
        print("Missed")
        return False

    def begin(self):
        self.busy = []
    def defeat(self):
        return self.count == len(self.ships)

class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)

class User(Player):
    def ask(self):
        while True:
            coords = input("Your turn: ").split()

            if len(coords) != 2:
                print("Enter only 2 coordinates!")
                continue
            x, y = coords

            if not (x.isdigit()) or not (y.isdigit()):
                print("Enter the numbers!")

            x, y = int(x), int(y)

            return Dot(x-1, y-1)

    # def set_ask(self, x, y):
    #
    #     self.x
    #     self.y


class AI(Player):
    def ask(self):
        dot = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {dot.x + 1} {dot.y + 1}")
        return dot

class Game:
    def __init__(self, size = 6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)
    def try_board(self):
        lengths = [3, 2, 2, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lengths:
            while True:
                attempts += 1
                if attempts > 1000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board
    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def greet(self):
        print("--------------\nHello there!\n--------------\nInput format: x y\nx - string number\ny - column number")
    def loop(self):
        num = 0
        while True:
            print('-'*20, '\n Your board:\n')
            print(self.us.board)
            print('-'*20, "\n AI's board:\n")
            print(self.ai.board)

            if num % 2 == 0:
                print("\n\nUser's turn\n\n")
                repeat = self.us.move()
            else:
                print("\n\nAI's turn\n\n")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.defeat():
                print('-' *20, "\n User wins!\n")
                print(self.ai.board)
                break
            if self.us.board.defeat():
                print("-"*20, "\n AI wins!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()