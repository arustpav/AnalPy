import sys
import random
import time
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QPushButton, QHBoxLayout, QVBoxLayout, QLabel
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import Qt
from PyQt5 import QtGui, QtCore
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal, QObject, QRect
from typing import List, Union
import json


class Board:

    def __init__(self, filename: str) -> None:
        with open(filename, "r") as read_file:
            _json = json.load(read_file)

            # Препятствия
            self.__borders = []

            self.__wall = _json['wall']

            self.__level_structures = _json['levels']

        

    def setLvl(self, level: int) -> None:
        self.__borders = []
        # рассматриваем структуру уровня и добавляем границы в соответствии с ней
        for i in range(len(self.__level_structures[level])):
            for j in range(len(self.__level_structures[level][0])):
                if self.__level_structures[level][i][j] == 1:
                    self.__borders.append((j, i))

    def empty(self, position: Union[int, int]) -> bool:
        if position[0] < self.__wall or position[0] > self.verticalLen() - 1 - self.__wall \
                or position[1] < self.__wall or position[1] > self.verticalLen() - 1 - self.__wall:
            return False
        for i in self.__borders:
            if i == position:
                return False
        return True

    def verticalLen(self) -> int:
        return len(self.__level_structures[0])

    def horizontalLen(self) -> int:
        return len(self.__level_structures[0][0])

    def levelsCount(self) -> int:
        return len(self.__level_structures)

    def getBorders(self) -> List[int]:
        return self.__borders

    def wallSize(self) -> int:
        return self.__wall


class Snake:

    def __init__(self) -> None:
        self.__snake = []  # тело змеи (первый элемент - голова)
        # фантомный хвост (место, где был хвост в прошлый ход)
        self.__snake_tail = (0, 0)

    # Проверка нахождения точки на змейке
    def have(self, position: Union[int, int]) -> bool:
        for i in self.__snake:
            if i == position:
                return True
        return False

    # Двигаем змейку
    def move(self, direction: str) -> None:
        self.__snake_tail = self.__snake[-1]

        for i in range(len(self.__snake) - 1, 0, -1):
            self.__snake[i] = self.__snake[i - 1]

        if direction == "Up":
            self.__snake[0] = self.__snake[0][0], self.__snake[0][1] - 1

        if direction == "Down":
            self.__snake[0] = self.__snake[0][0], self.__snake[0][1] + 1

        if direction == "Left":
            self.__snake[0] = self.__snake[0][0] - 1, self.__snake[0][1]

        if direction == "Right":
            self.__snake[0] = self.__snake[0][0] + 1, self.__snake[0][1]

    def incLen(self) -> None:
        self.__snake.append(self.__snake_tail)

    def spawn(self, position: Union[int, int]) -> None:
        self.__snake = [position]
        self.__snake_tail = position

    def checkApple(self, position: Union[int, int]) -> None:
        return self.__snake[0] == position

    def isCorrect(self, board: Board) -> bool:
        # границы
        if self.__snake[0][0] < board.wallSize() or self.__snake[0][1] < board.wallSize() \
                or self.__snake[0][0] > board.verticalLen() - board.wallSize() or self.__snake[0][1] > board.horizontalLen() - board.wallSize():
            return False
        # пересечение змеи и песечение уровня
        for i in range(1, len(self.__snake)):
            if self.__snake[0] == self.__snake[i]:
                return False
            if not board.empty(self.__snake[i]):
                return False
        if not board.empty(self.__snake[0]):
            return False
        return True

    def getSnakeArray(self) -> List[int]:
        return self.__snake


class Apple:

    def __init__(self) -> None:
        self.__position = (0, 0)

    def spawn(self, board: Board, snake: Snake) -> None:
        self.__position = random.randint(0, board.verticalLen() - 1), \
            random.randint(0, board.horizontalLen() - 1)

        # проверка на нормальный спавн 2 методами
        while (not board.empty(self.__position)) or snake.have(self.__position):
            self.__position = random.randint(0, board.verticalLen() - 1), \
                random.randint(0, board.horizontalLen() - 1)

    def getPosition(self) -> Union[int, int]:
        return self.__position


# Виджет самой игры змейки
class SnakeGame(QWidget):
    # Сигналы смены очков жизней
    score_changed_signal = pyqtSignal()
    lives_changed_signal = pyqtSignal()

    # конструктор
    def __init__(self, parent, board: Board, snake: Snake, apple: Apple):

        # обращение к родительскому классу и вызов его конструктора
        super().__init__(parent)

        # теперь ЭТОТ виджет реагирует на нажатия на клавиатуру
        self.setFocus()

        # размеры виджета
        self.resize(500, 500)
        # отбражение виджета
        self.show()

        self.apple = apple
        self.snake = snake
        self.board = board
        self.CELL_SIZE = 20

        # Размеры и задержка таймера
        self.GAME_DELAY = 150

        # Поля с данными
        self.WIN = 0
        self.POINTS_TO_WIN = 5
        self.game_over = 0
        self.game_in_process = -1
        # направление змейки
        self.direction = ""
        self.score = 0
        self.lives = 10
        self.curr_level = 0

        # Инициализируем игру, запускаем таймер и отрисоввывем
        # вызов метода
        self.InitGame()
        self.timer_id = self.startTimer(self.GAME_DELAY)
        self.repaint()

    # Спавним яблоко, создаём змейку, записываем длинну змейки
    def InitGame(self):

        # помещаем змейку на поле
        self.snake.spawn(
            ((self.board.verticalLen() // 2), (self.board.horizontalLen() // 2))
        )
        self.apple.spawn(self.board, self.snake)

        self.board.setLvl(0)

    # отрисовка
    def paintEvent(self, e):
        if(self.WIN == 1):
            qp = QPainter()
            qp.begin(self)
            qp.drawText(e.rect(), Qt.AlignCenter, "WIN")
            qp.end()
            return
        # TODO поменять кисти
        qp = QPainter()
        qp.begin(self)

        # рисуем границы уровня
        qp.drawRect(0, 0, self.CELL_SIZE, self.CELL_SIZE *
                    self.board.horizontalLen())
        qp.drawRect(0, 0, self.CELL_SIZE *
                    self.board.verticalLen(), self.CELL_SIZE)
        qp.drawRect(self.CELL_SIZE * self.board.verticalLen(), 0,
                    self.CELL_SIZE - 1, self.CELL_SIZE * self.board.horizontalLen() - 1)
        qp.drawRect(0, self.CELL_SIZE * self.board.horizontalLen() - self.CELL_SIZE, self.CELL_SIZE * self.board.verticalLen(),
                    self.CELL_SIZE - 1)

        apple = self.apple.getPosition()

        # рисуем яблоко
        qp.drawEllipse(apple[0] * self.CELL_SIZE,
                       apple[1] * self.CELL_SIZE,
                       self.CELL_SIZE, self.CELL_SIZE)

        snake = self.snake.getSnakeArray()

        # рисуем голову змейки
        qp.drawRect(snake[0][0] * self.CELL_SIZE, snake[0][1]
                    * self.CELL_SIZE, self.CELL_SIZE, self.CELL_SIZE)

        # рисуем тело змейки
        for i in range(1, len(snake)):
            qp.drawRect(snake[i][0] * self.CELL_SIZE, snake[i][1]
                        * self.CELL_SIZE, self.CELL_SIZE, self.CELL_SIZE)

        # рисуем границы уровня
        for i in self.board.getBorders():
            qp.drawRect(i[0] * self.CELL_SIZE, i[1] *
                        self.CELL_SIZE, self.CELL_SIZE, self.CELL_SIZE)

        qp.end()

    # По таймеру двигаем змейку, проверяем яблоко и проверяем столкновения и самопересечения
    def timerEvent(self, e):
        if (self.game_in_process == 1):
            self.snake.move(self.direction)
            self.CheckApple()
            self.game_over = not self.snake.isCorrect(self.board)
            if self.score == self.POINTS_TO_WIN*(self.curr_level+1):
                self.game_over = 1
                self.curr_level += 1
            if self.curr_level == self.board.levelsCount():
                self.WIN = 1
                self.repaint()
                self.Pause()
                return
            if (self.game_over != 0):
                self.Restart()
                self.game_over = 0
            self.repaint()

    # По нажатию клавиши меняем направление
    def keyPressEvent(self, e):
        if (self.game_in_process == -1):
            self.game_in_process = 1
        key = e.key()

        if key == Qt.Key_Left and self.direction != "Right":
            self.direction = "Left"
        if key == Qt.Key_Right and self.direction != "Left":
            self.direction = "Right"
        if key == Qt.Key_Up and self.direction != "Down":
            self.direction = "Up"
        if key == Qt.Key_Down and self.direction != "Up":
            self.direction = "Down"
        # QWidget.keyPressEvent(e);

    # Проверка столкновения с яблоком
    def CheckApple(self):
        if self.snake.checkApple(self.apple.getPosition()):
            self.apple.spawn(self.board, self.snake)
            self.snake.incLen()
            self.score += 1
            self.score_changed_signal.emit()

    # Пауза
    def Pause(self):
        self.game_in_process = -1

    # Cлот под паузу
    def SetPause(self):
        self.Pause()
        self.setFocus()

    # Рестарт
    def Restart(self):
        self.direction = ""
        self.lives -= 1
        self.lives_changed_signal.emit()
        if self.lives == 0:
            self.game_in_process = 0
            self.repaint()
        self.snake.spawn(
            [(self.board.verticalLen() // 2), (self.board.horizontalLen() // 2)])
        self.apple.spawn(self.board, self.snake)

        self.board.setLvl(self.curr_level)

    # Геттер размера поля
    def GetFieldSize(self):
        return [self.board.verticalLen(), self.board.horizontalLen()]

    # Гетер размера клетки
    def GetCellSize(self):
        return self.CELL_SIZE


class Menu(QWidget):
    def __init__(self, levelsFilename):
        super().__init__()

        # Слева сама змейка, справа в vbox кнопки и очки

        self.snake_game_widg = SnakeGame(
            self, Board(levelsFilename), Snake(), Apple())

        menu_size = 100
        xsz = self.snake_game_widg.GetFieldSize()[
            0] * self.snake_game_widg.GetCellSize() + menu_size + self.snake_game_widg.GetCellSize()
        ysz = self.snake_game_widg.GetFieldSize(
        )[1] * self.snake_game_widg.GetCellSize()

        self.resize(xsz, ysz)

        self.quit_button = QPushButton("Quit", self)
        self.quit_button.clicked.connect(sys.exit)

        self.pause_button = QPushButton("Pause", self)
        self.pause_button.clicked.connect(self.snake_game_widg.SetPause)

        self.score = QLabel("Score: 0", self)

        self.lives = QLabel("Lives: 10", self)

        vbox = QVBoxLayout()

        vbox.addWidget(self.score)
        vbox.addWidget(self.lives)
        vbox.addWidget(self.pause_button)
        vbox.addWidget(self.quit_button)

        # TODO Подключить сигналы к лейблам
        self.snake_game_widg.lives_changed_signal.connect(self.SetLives)
        self.snake_game_widg.score_changed_signal.connect(self.SetScore)
        # TODO Подключить сигналы к лейблам

        vbox.setGeometry(QRect(xsz - menu_size, 0, menu_size, ysz))
        self.snake_game_widg.setGeometry(0, 0, xsz - menu_size, ysz)

        self.show()

    # Слот под установку очков
    def SetScore(self):
        text = "Score: " + str(self.snake_game_widg.score)
        self.score.setText(text)

    # Слот под установку жизней
    def SetLives(self):
        text = "Lives: " + str(self.snake_game_widg.lives)
        self.lives.setText(text)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Menu(sys.argv[1])
    sys.exit(app.exec_())
