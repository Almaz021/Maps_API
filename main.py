import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtWidgets import QLabel, QRadioButton, QPushButton, QInputDialog, QMessageBox, QLabel, QCheckBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import requests
from PIL import Image

width, height = 900, 980

maptypes = {'Схема': 'map',
            'Спутник': 'sat',
            'Гибрид': 'sat,skl'}


class Example(QWidget):
    def __init__(self):
        super(Example, self).__init__()
        self.image = QLabel(self)
        self.pixmap = None
        self.z = 8
        self.ll = [49.106414, 55.796127]
        self.point = []
        self.maptype = 'map'
        self.initUI()

    def setChildrenFocusPolicy(self, policy):  # эта фигня нужна чтобы кнопки работали, не трогайте
        def recursiveSetChildFocusPolicy(parentQWidget):
            for childQWidget in parentQWidget.findChildren(QWidget):
                childQWidget.setFocusPolicy(policy)
                recursiveSetChildFocusPolicy(childQWidget)
        recursiveSetChildFocusPolicy(self)

    def initUI(self):
        self.setGeometry(300, 50, width, height)
        self.setWindowTitle('Map')

        self.mapbtn = QRadioButton("Схема", self)
        self.sat = QRadioButton("Спутник", self)
        self.skl = QRadioButton("Гибрид", self)
        self.mapbtn.setChecked(True)
        self.mapbtn.move(5, height - 60)
        self.sat.move(95, height - 60)
        self.skl.move(185, height - 60)
        self.mapbtn.toggled.connect(self.change_l)
        self.sat.toggled.connect(self.change_l)
        self.skl.toggled.connect(self.change_l)

        self.search = QPushButton("Поиск", self)
        self.search.move(500, height - 60)
        self.search.resize(200, 25)
        self.search.clicked.connect(self.search_dialog)

        self.resetbtn = QPushButton('Сброс поискового результата', self)
        self.resetbtn.move(710, height - 60)
        self.resetbtn.clicked.connect(self.reset_point)
        
        self.postalcodebox = QCheckBox('Почтовый индекс', self)
        self.postalcodebox.move(300, height - 60)
        self.postalcodebox.clicked.connect(self.set_text)

        self.adress = QLabel(self)     # показывает адрес (ч. 8)
        self.adress.move(5, height - 30)
        self.adress.resize(900, 30)

        self.setChildrenFocusPolicy(Qt.NoFocus)   # не трогать, убьёт!!!!!!

        self.response()

    def reset_point(self):
        self.point = []
        self.adress.setText('')
        self.response()

    def search_dialog(self, s):
        text, ok = QInputDialog.getText(self, 'Поиск', 'Введите запрос')
        if not ok:
            return
        api_server = f"https://geocode-maps.yandex.ru/1.x/"
        map_params = {'apikey': '40d1649f-0493-4b70-98ba-98533de7710b',
                      'geocode': text,
                      'format': 'json'}
        response = requests.get(api_server, params=map_params)
        toponym = response.json()['response']['GeoObjectCollection']['featureMember']
        if not toponym:
            msgBox = QMessageBox()
            msgBox.setText('По данному запросу ничего не найдено')
            msgBox.exec()
            return
        toponym = toponym[0]['GeoObject']
        toponym_coords = toponym["Point"]["pos"]
        self.adressTop = toponym['metaDataProperty']['GeocoderMetaData']
        self.set_text()
        self.ll = [float(i) for i in toponym_coords.split()]
        self.point = [float(i) for i in toponym_coords.split()]
        self.response()

    def set_text(self):    # специально для п.9 )
        if self.postalcodebox.checkState():
            self.adress.setText(f"{self.adressTop['text']}, почтовый индекс: {self.adressTop['Address']['postal_code']}")
        else:
            self.adress.setText(self.adressTop['text'])

    def response(self):
        api_server = f"http://static-maps.yandex.ru/1.x/"
        map_params = {'ll': f'{self.ll[0]},{self.ll[1]}',
                      'z': self.z,
                      'l': self.maptype,
                      'size': '450,450'}
        if self.point:
            map_params['pt'] = f'{self.point[0]},{self.point[1]},pm2rdm'
        response = requests.get(api_server, params=map_params)
        if not response:
            print("Ошибка выполнения запроса:")
            print(f"{api_server}?{'&'.join([f'{k}={map_params[k]}' for k in map_params.keys()])}")
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)
        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)
        self.ran()

    def ran(self):
        img = Image.open(self.map_file)
        img = img.resize((900, 900))
        img.save(self.map_file)
        self.pixmap = QPixmap(self.map_file)
        self.image.move(0, 0)
        self.image.setPixmap(self.pixmap)

    def keyPressEvent(self, event):
        delta = 900 * (180 / (2 ** (self.z + 9)))
        if event.key() == Qt.Key_PageUp and self.z < 17:
            self.z += 1
            print(self.z)
        elif event.key() == Qt.Key_PageDown and self.z > 0:
            self.z -= 1
            print(self.z)
        elif event.key() == Qt.Key_Up and self.ll[1] + delta < 90:
            self.ll[1] += delta
        elif event.key() == Qt.Key_Down and self.ll[1] - delta > -90:
            self.ll[1] -= delta
        elif event.key() == Qt.Key_Right:
            self.ll[0] += delta * 2
            while self.ll[0] > 180:
                self.ll[0] -= 360
        elif event.key() == Qt.Key_Left:
            self.ll[0] -= delta * 2
            while self.ll[0] < -180:
                self.ll += 360
        print(self.ll)
        self.response()

    def mousePressEvent(self, event):
        coords = [self.ll[0] + (event.x() - 450) * (180 / (2 ** (self.z + 8))), \
                  self.ll[1] - (event.y() - 450) * (180 / (2 ** (self.z + 8.8)))]
        # https://yandex.ru/dev/maps/jsapi/doc/2.1/theory/index.html
        print(coords)
        self.point = coords
        self.response()
    
    def change_l(self):
        if self.sender().isChecked():
            self.maptype = maptypes[self.sender().text()]
        self.response()
    
    def closeEvent(self, event):
        os.remove(self.map_file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())

# 16777238 Pg_up
# 16777239 Pg_down
