from PyQt5.QtCore import Qt, QPointF, QTimer, QVariantAnimation, QRectF
from PyQt5.QtGui import QPen, QBrush
import json
from math import ceil
from PyQt5.QtWidgets import (
    QApplication,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsEllipseItem,
    QSlider,
    QComboBox,
    QLabel,
    QSpinBox,
    QCheckBox
)
import sys, random


class Cabbage(QGraphicsEllipseItem):
    def __init__(self, x, y, r):
        super().__init__(0, 0, r, r)
        self.setPos(x, y)
        self.r = r
        self.setBrush(Qt.darkGreen)
        self.setRect(QRectF(-r, -r, 2 * r, 2 * r))
        self.occupied = False

class Goat(QGraphicsEllipseItem):
    def __init__(self, x, y, r, view, sets):
        super().__init__(0, 0, r, r)
        self.setPos(x, y)
        self.r = r
        self.view = view
        self.setBrush(Qt.black)
        self.setRect(QRectF(-r, -r, 2 * r, 2 * r))
        self.sets = sets
        self.etimer = None
        self.speed, self.endurance, self.fertility, self.eatspeed = sets
        self.def_end = self.endurance
        self.ind = self.view.ind
        self.s = QTimer(self.view)
        self.s.timeout.connect(self.find_next_cab)
        self.eating = False

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
        self.etimer = QTimer(self.view)
        self.etimer.timeout.connect(self.bite)
        self.endurance = self.def_end
        self.etimer.start(1000)


    def bite(self):
        self.cab = self.next_cab
        if self.cab.r - self.eatspeed <= 0:
            self.r += ceil(self.cab.r * self.fertility)
            R = self.r
            self.setRect(QRectF(-R, -R, 2 * R, 2 * R))
            self.scene().removeItem(self.cab)
            self.etimer.stop()
            self.setStartAngle(0)
            self.setSpanAngle(360 * 16)
            print(f'Популяция стада {self.ind}: {R}')
            self.eating = False
            self.find_next_cab()
        else:
            self.cab.r -= self.eatspeed
            R = self.cab.r
            self.cab.setRect(QRectF(-R, -R, 2 * R, 2 * R))
            self.r += ceil(self.eatspeed * self.fertility)
            R = self.r
            self.setRect(QRectF(-R, -R, 2 * R, 2 * R))

    def find_next_cab(self):
        self.mn = 10000
        self.next_cab = None
        for el in self.view.items():
            if isinstance(el, Cabbage):
                if el.occupied == False:
                    dist = (((self.x() - el.x()) ** 2 + (self.y() - el.y()) ** 2) ** 0.5)
                    if dist <= self.mn:
                        self.mn = min(dist, self.mn)
                        self.next_cab = el
        if self.next_cab != None:
            if self.s.isActive: self.s.stop()
            self.next_cab.occupied = True
            self.move_to(self.next_cab.x(), self.next_cab.y())

        else:
            #self.view.spawn_cab()
            if self.s.isActive() == False:
                self.s.start(100)

class GraphicsScene(QGraphicsScene):
    def __init__(self, parent=None):
        QGraphicsScene.__init__(self, parent)
        self.setSceneRect(0, 0, 1200, 600)

    def mousePressEvent(self, event):
        x = event.scenePos().x()
        y = event.scenePos().y()
        if (self.parent().cabcheck.isChecked()):
            if 0 <= x <= 1000:
                self.parent().scene().addItem(Cabbage(*[x, y], self.parent().cabsign.value()))
        else:
            for item in self.items():
                if type(item) == Goat:
                    if (item.x() - item.r <= x <= item.x() + item.r) and (item.y() - item.r <= y <= item.y() + item.r):
                        item.speed = self.parent().stats[0] / 4
                        item.def_end = self.parent().stats[1]
                        item.fertility = self.parent().stats[2] / 4
                        item.eatspeed = self.parent().stats[3]
                        if not item.eating:
                            item._animation.stop()
                            item.move_to(item.next_cab.x(), item.next_cab.y())
                        print(f'новые характеристики: speed:{item.speed}, endurance:{item.endurance}, fertility:{item.fertility}, eatspeed:{item.eatspeed}')
                        break


class GraphicView(QGraphicsView):
    def __init__(self, sets):
        super().__init__()
        self.stats = sets[:-1]
        self.hunger_rate = sets[-1]
        self.ind = 0
        scene = GraphicsScene(self)
        self.UiComponents()
        self.setScene(scene)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updscene)
        for _ in range(5):
            self.spawn_cab()
        self.herds = []
        herd = Goat(300, 600, 10, self, self.stats)
        self.herds.append(herd)
        self.scene().addItem(herd)
        self.ind += 1
        herd.find_next_cab()

        self.timer.start(1000)
        cabtimer = QTimer(self)
        cabtimer.timeout.connect(self.spawn_cab)
        cabtimer.start(5000)
        self.show()

    def spawn_herd(self):
        sets = [self.stats[0]/4,self.stats[1], self.stats[2]/4, self.stats[3]]
        goat = Goat(random.randint(0,1000), random.randint(0,600), 10, self, sets)
        self.ind += 1
        self.herds.append(goat)
        self.scene().addItem(goat)
        goat.find_next_cab()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_H:
           self.spawn_herd()

    def UiComponents(self):
        self.combbox = QComboBox(self)
        self.combbox.addItems(['SPEED','ENDURANCE', 'FERTILITY', 'EATSPEED'])
        self.combbox.setStyleSheet("border: 1px solid black;")
        self.combbox.setFixedSize(80, 20)
        self.combbox.move(1120, 380)
        self.combbox.currentIndexChanged.connect(self.load_scroll)

        self.scroll = QSlider(self)
        self.cur_stat = 0

        self.scroll.setGeometry(1150, 400, 50, 200)
        self.scroll.setStyleSheet("background : lightblue;")
        self.scroll.setMinimum(1)
        self.scroll.setMaximum(20)
        self.scroll.setTickInterval(1)
        self.scroll.valueChanged.connect(self.scroll_update)
        self.scroll.setSliderPosition(1)

        self.scroll_name = QLabel(self)
        self.scroll_name.setText('0.25')
        self.scroll_name.move(1120, 400)
        self.scroll_name.setFixedSize(30, 20)
        self.scroll_name.setStyleSheet("border: 1px solid black;")

        self.cabsign = QSpinBox(self)
        self.cabcheck = QCheckBox("Spawn Cabbage", self)
        self.cabname = QLabel(self)

        self.cabcheck.setStyleSheet("border: 1px solid black;")
        self.cabcheck.move(1100, 60)

        self.cabname.setText('Cabbage_Volume')
        self.cabname.setStyleSheet("border: 1px solid black;")
        self.cabname.move(1100, 80)

        self.cabsign.setMinimum(2)
        self.cabsign.setMaximum(30)
        self.cabsign.setFixedSize(30, 20)
        self.cabsign.setStyleSheet("border: 1px solid black;")
        self.cabsign.move(1100, 100)

    def load_scroll(self, opt):
        self.cur_stat = opt
        if opt not in [1,3]:
            self.scroll_name.setText(str(self.stats[self.cur_stat] / 4))
        else:
            self.scroll_name.setText(str(self.stats[self.cur_stat]))
        self.scroll.setSliderPosition(self.stats[opt])

    def scroll_update(self, value):
        self.stats[self.cur_stat] = value
        if self.cur_stat not in [1,3]:
            self.scroll_name.setText(str(self.stats[self.cur_stat] / 4))
        else:
            self.scroll_name.setText(str(self.stats[self.cur_stat]))


    def spawn_cab(self):
        dot = [random.randint(0, 1000), random.randint(0, 600)]
        vol = random.randint(3, 10)
        self.scene().addItem(Cabbage(*dot, vol))

    def updscene(self):
        for herd in self.herds:
            if herd.eating == False:
                if herd.endurance - self.hunger_rate <= 0:
                    herd.r -= 1
                    R = herd.r
                    if R == 0:
                        print(f'Стадо {herd.ind} вымерло :(')
                        herd._animation.stop()
                        self.scene().removeItem(herd)
                        self.herds.remove(herd)
                    print(f'Популяция стада {herd.ind}: {R}')
                    herd.setRect(QRectF(-R, -R, 2 * R, 2 * R))
                    herd.endurance = herd.def_end
                else:
                    herd.endurance -= self.hunger_rate

    def Eat_circle(self, cabbage, goat):
        goat.eating = True
        cabbage.setStartAngle(0)
        cabbage.setSpanAngle(-180 * 16)
        goat.setStartAngle(0)
        goat.setSpanAngle(180 * 16)

def load_settings():
    try:
        f = open("Ogorod_setting.json")
        print("Файл с настройками открыт")
        data = json.load(f)
        print(data)
        return data

    except FileNotFoundError:
        data = {
            "speed": 1,
            "endurance": 5,
            "fertility": 1,
            "eatspeed": 1,
            "hunger_rate": 5

        }
        with open("Ogorod_setting.json", 'w') as f:
            print("Файл с настройками создан")
            json.dump(data, f)
        return data

if __name__ == "__main__":
    settings = load_settings()
    app = QApplication(sys.argv)
    view = GraphicView(list(settings.values()))
    view.show()
    sys.exit(app.exec_())
