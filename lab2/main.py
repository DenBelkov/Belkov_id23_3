from PyQt5.QtCore import Qt, QPointF, QTimer, QVariantAnimation, QRectF
from math import ceil
from PyQt5.QtWidgets import (
    QApplication,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsEllipseItem,
)
import sys, random
import json

class Cabbage(QGraphicsEllipseItem):
    def __init__(self, x, y, r):
        super().__init__(0, 0, r, r)
        self.setPos(x, y)
        self.r = r
        self.setBrush(Qt.darkGreen)
        self.setRect(QRectF(-r, -r, 2 * r, 2 * r))


class Goat(QGraphicsEllipseItem):
    def __init__(self, x, y, r, view, sets):
        speed, endurance, fertility = sets
        super().__init__(0, 0, r, r)
        self.setPos(x, y)
        self.r = r
        self.view = view
        self.setBrush(Qt.black)
        self.setRect(QRectF(-r, -r, 2 * r, 2 * r))

        self.speed = speed
        self.endurance = endurance
        self.fertility = fertility

    def move_to(self, x, y):
        dist = (((self.x() - x) ** 2 + (self.y() - y) ** 2) ** 0.5) * 10
        self._animation = QVariantAnimation(duration=int(dist / self.speed))
        self._animation.valueChanged.connect(self.setPos)
        self._animation.finished.connect(self.eat)
        self._animation.setStartValue(self.pos())
        self._animation.setEndValue(QPointF(x, y))
        self._animation.start(100)

    def eat(self):
        self.view.Eat_circle(self.next_cab, self)

    def find_next_cab(self):
        self.mn = 10000
        self.next_cab = None
        for el in self.view.items():
            if isinstance(el, Cabbage):
                dist = (((self.x() - el.x()) ** 2 + (self.y() - el.y()) ** 2) ** 0.5)
                if dist <= self.mn:
                    self.mn = min(dist, self.mn)
                    self.next_cab = el
        self.move_to(self.next_cab.x(), self.next_cab.y())


class GraphicView(QGraphicsView):
    def __init__(self, settings):
        super().__init__()
        scene = QGraphicsScene(self)
        self.setScene(scene)
        self.setSceneRect(0, 0, 1200, 600)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updscene)
        for _ in range(5):
            self.spawn_cab()
        self.goat_settings = settings[:3]
        self.eatspeed, self.hunger_rate = settings[3:]
        self.herd = Goat(300, 600, 10, self, self.goat_settings)
        self.scene().addItem(self.herd)
        self.herd.find_next_cab()
        self.timer.start(1000)
        cabtimer = QTimer(self)
        cabtimer.timeout.connect(self.spawn_cab)
        cabtimer.start(5000)

    def spawn_cab(self):
        dot = random.sample(range(0, 600), 2)
        vol = random.randint(3, 10)
        self.scene().addItem(Cabbage(*dot, vol))

    def updscene(self):
        if self.herd.endurance - self.hunger_rate <= 0:
            self.herd.r -= 1
            R = self.herd.r
            print(f'Популяция стада: {R}')
            self.herd.setRect(QRectF(-R, -R, 2 * R, 2 * R))
            self.herd.endurance = self.goat_settings[1]
        else:
            self.herd.endurance -= self.hunger_rate

    def Eat_circle(self, cabbage, goat):
        self.cab = cabbage
        self.goat = goat
        self.timer.stop()
        cabbage.setStartAngle(0)
        cabbage.setSpanAngle(-180 * 16)
        goat.setStartAngle(0)
        goat.setSpanAngle(180 * 16)
        self.etimer = QTimer(self)
        self.etimer.timeout.connect(self.bite)
        goat.endurance = self.goat_settings[1]
        self.etimer.start(1000)

    def bite(self):
        if self.cab.r - self.eatspeed <= 0:
            self.goat.r += ceil(self.cab.r * self.goat.fertility)
            R = self.goat.r
            self.goat.setRect(QRectF(-R, -R, 2 * R, 2 * R))
            self.scene().removeItem(self.cab)
            self.etimer.stop()
            self.goat.setStartAngle(0)
            self.goat.setSpanAngle(360 * 16)
            print(f'Популяция стада: {R}')
            self.timer.start(1000)
            self.goat.find_next_cab()
        else:
            self.cab.r -= self.eatspeed
            R = self.cab.r
            self.cab.setRect(QRectF(-R, -R, 2 * R, 2 * R))
            self.goat.r += ceil(self.eatspeed * self.goat.fertility)
            R = self.goat.r
            self.goat.setRect(QRectF(-R, -R, 2 * R, 2 * R))


def load_settings():
    try:
        f = open("Ogorod_setting.json")
        print("Файл с настройками открыт")
        data = json.load(f)
        return data
    except FileNotFoundError:
        data = {
            "speed":0.25,
            "self.endurance": 5,
            "self.fertility": 0.25,
            "hunger_rate": 2,
            "eatspeed": 1
        }
        with open("Ogorod_setting.json", 'w') as f:
            print("Файл с настройками создан")
            json.dump(data, f)
        return data

if __name__ == "__main__":
    settings = load_settings()
    print(settings)
    app = QApplication(sys.argv)
    view = GraphicView(list(settings.values()))
    view.show()
    sys.exit(app.exec_())
