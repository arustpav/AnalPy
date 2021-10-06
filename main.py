import sys, random, time
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QPushButton, QHBoxLayout, QVBoxLayout, QLabel
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import Qt
from PyQt5 import QtGui, QtCore
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSignal, QObject, QRect
import pyqtgraph as pg
import numpy as np


# Виджет самой игры змейки
class SnakeGame(QWidget):
    # Сигналы смены очков жизней
    score_changed_signal = pyqtSignal()
    lives_changed_signal = pyqtSignal()

    # конструктор
    def __init__(self, parent):
        
        # обращение к родительскому классу и вызов его конструктора
        super().__init__(parent)
        
        # теперь ЭТОТ виджет реагирует на нажатия на клавиатуру
        self.setFocus()

        # размеры виджета
        self.resize(500, 500)
        # отбражение виджета
        self.show()

        # Размеры и задержка таймера
        self.GAME_DELAY = 100
        self.CELL_SIZE = 10
        self.FIELD_SIZE_X = 25
        self.FIELD_SIZE_Y = 25

        # Поля с данными
        self.WIN = 0
        self.POINTS_TO_WIN = 5
        self.game_over = 0
        self.game_in_process = -1
        # направление змейки
        self.direction = ""
        self.snake = [ ]  # тело змеи (первый элемент - голова)
        self.apple = (0, 0)
        self.snake_tail = (0, 0)  # фантомный хвост (место, где был хвост в прошлый ход)
        self.snake_len = 0
        self.score = 0
        self.lives = 10
        self.curr_level = 0

        # Препятствия
        self.borders = []

        self.level_structures =\
        [
        [[2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
         [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
         [2, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
         [2, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
         [2, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
         [2, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
         [2, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
         [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
         [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
         [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
         [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
         [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
         [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
         [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
         [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
         [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
         [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
         [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
         [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
         [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
         [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
         [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
         [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
         [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]],

        [[2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
         [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
         [2, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
         [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
         [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
         [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
         [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
         [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
         [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
         [2, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 2],
         [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
         [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
         [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
         [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
         [2, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 2],
         [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
         [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
         [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
         [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
         [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
         [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
         [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
         [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
         [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]]
        ]

        # Инициализируем игру, запускаем таймер и отрисоввывем
        # вызов метода
        self.InitGame()
        self.timer_id = self.startTimer(self.GAME_DELAY)
        self.repaint()

    # Спавним яблоко, создаём змейку, записываем длинну змейки
    def InitGame(self):

        self.snake.append(
            ((self.FIELD_SIZE_X // 2) * self.CELL_SIZE, (self.FIELD_SIZE_Y // 2) * self.CELL_SIZE))
        self.snake_len = 1
        self.SpawnApple()

        for i in range(len(self.level_structures[0])):
            for j in range(len(self.level_structures[0][0])):
                if self.level_structures[0][i][j] == 1:
                    self.borders.append((j*self.CELL_SIZE, i*self.CELL_SIZE))

    # Спавн яблока
    def SpawnApple(self):
        self.apple = random.randint(self.CELL_SIZE, (self.FIELD_SIZE_X - 1)) * self.CELL_SIZE, random.randint(self.CELL_SIZE, (
                self.FIELD_SIZE_Y - 2)) * self.CELL_SIZE

        while self.AppleOnSnake() or self.appleOnBord():
            self.apple = random.randint(0, (self.FIELD_SIZE_X - 1)) * self.CELL_SIZE, random.randint(0, (
                    self.FIELD_SIZE_Y - 2)) * self.CELL_SIZE

    def appleOnBord(self):
        for i in self.borders:
            if i == self.apple:
                return True
        return False

    # Проверка нахождения яблока на змее
    def AppleOnSnake(self):
        for i in self.snake:
            if i == self.apple:
                return True
        return False

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

        qp.drawRect(0, 0, self.CELL_SIZE, self.CELL_SIZE * self.FIELD_SIZE_Y)
        qp.drawRect(0, 0, self.CELL_SIZE * self.FIELD_SIZE_X, self.CELL_SIZE)
        qp.drawRect(self.CELL_SIZE * self.FIELD_SIZE_X, 0, self.CELL_SIZE - 1, self.CELL_SIZE * self.FIELD_SIZE_Y - 1)
        qp.drawRect(0, self.CELL_SIZE * self.FIELD_SIZE_Y - self.CELL_SIZE, self.CELL_SIZE * self.FIELD_SIZE_X,
                    self.CELL_SIZE - 1)

        qp.drawEllipse(self.apple[ 0 ], self.apple[ 1 ], self.CELL_SIZE, self.CELL_SIZE)

        qp.drawRect(self.snake[ 0 ][ 0 ], self.snake[ 0 ][ 1 ], self.CELL_SIZE, self.CELL_SIZE)

        for i in range(1, self.snake_len):
            qp.drawRect(self.snake[ i ][ 0 ], self.snake[ i ][ 1 ], self.CELL_SIZE, self.CELL_SIZE)

        for i in self.borders:
            qp.drawRect(i[0], i[1], self.CELL_SIZE, self.CELL_SIZE)

        qp.end()

    # По таймеру двигаем змейку, проверяем яблоко и проверяем столкновения и самопересечения
    def timerEvent(self, e):
        if (self.game_in_process == 1):
            self.Move()
            self.CheckApple()
            self.game_over = self.CheckBorders()
            if self.score == self.POINTS_TO_WIN*(self.curr_level+1):
                self.game_over = 1
                self.curr_level += 1
            if self.curr_level == len(self.level_structures):
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

    # Двигаем змейку
    def Move(self):
        self.snake_tail = self.snake[ self.snake_len - 1 ]

        for i in range(self.snake_len - 1, 0, -1):
            self.snake[ i ] = self.snake[ i - 1 ]

        if self.direction == "Up":
            self.snake[ 0 ] = self.snake[ 0 ][ 0 ], self.snake[ 0 ][ 1 ] - self.CELL_SIZE

        if self.direction == "Down":
            self.snake[ 0 ] = self.snake[ 0 ][ 0 ], self.snake[ 0 ][ 1 ] + self.CELL_SIZE

        if self.direction == "Left":
            self.snake[ 0 ] = self.snake[ 0 ][ 0 ] - self.CELL_SIZE, self.snake[ 0 ][ 1 ]

        if self.direction == "Right":
            self.snake[ 0 ] = self.snake[ 0 ][ 0 ] + self.CELL_SIZE, self.snake[ 0 ][ 1 ]

    # Проверка столкновения с границами
    def CheckBorders(self):
        if self.snake[ 0 ][ 0 ] < self.CELL_SIZE or self.snake[ 0 ][ 1 ] < self.CELL_SIZE or self.snake[ 0 ][ 0 ] > (
                self.FIELD_SIZE_X * self.CELL_SIZE - self.CELL_SIZE) or self.snake[ 0 ][ 1 ] > (
                self.FIELD_SIZE_Y * self.CELL_SIZE - self.CELL_SIZE * 2):
            return 1
        for i in range(1, self.snake_len):
            if self.snake[ 0 ] == self.snake[ i ]:
                return 1
        for i in self.borders:
            if self.snake[ 0 ] == i:
                return 1
        return 0

    # Проверка столкновения с яблоком
    def CheckApple(self):
        if self.snake[ 0 ] == self.apple:
            self.SpawnApple()
            self.snake_len += 1
            self.score += 1
            self.snake.append((0, 0))
            self.snake[ self.snake_len - 1 ] = self.snake_tail
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
        self.snake.clear()
        self.snake.append(
            [ (self.FIELD_SIZE_X // 2) * self.CELL_SIZE, (self.FIELD_SIZE_Y // 2) * self.CELL_SIZE ])
        self.snake_len = 1
        self.SpawnApple()

        self.borders.clear()
        for i in range(len(self.level_structures[self.curr_level])):
            for j in range(len(self.level_structures[self.curr_level][0])):
                if self.level_structures[self.curr_level][i][j] == 1:
                    self.borders.append((j*self.CELL_SIZE, i*self.CELL_SIZE))

    # Геттер размера поля
    def GetFieldSize(self):
        return [ self.FIELD_SIZE_X, self.FIELD_SIZE_Y ]

    # Гетер размера клетки
    def GetCellSize(self):
        return self.CELL_SIZE


class Menu(QWidget):
    def __init__(self):
        super().__init__()

        #Слева сама змейка, справа в vbox кнопки и очки

        self.snake_game_widg = SnakeGame(self)

        menu_size = 100
        xsz = self.snake_game_widg.GetFieldSize()[
                  0 ] * self.snake_game_widg.GetCellSize() + menu_size + self.snake_game_widg.GetCellSize()
        ysz = self.snake_game_widg.GetFieldSize()[ 1 ] * self.snake_game_widg.GetCellSize()

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

    #Слот под установку очков
    def SetScore(self):
        text = "Score: " + str(self.snake_game_widg.score)
        self.score.setText(text)

    #Слот под установку жизней
    def SetLives(self):
        text = "Lives: " + str(self.snake_game_widg.lives)
        self.lives.setText(text)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Menu()
    sys.exit(app.exec_())
