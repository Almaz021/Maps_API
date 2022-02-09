import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtWidgets import QLabel, QPushButton
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import requests
from PIL import Image

width, height = 1000, 890


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.image = QLabel(self)
        self.pixmap = None
        self.spn = [0.5, 0.5]
        self.ll = [49.099982, 55.767306]
        self.l = 'map'
        self.initUI()

    def initUI(self):
        self.setGeometry(300, 50, width, height)
        self.setWindowTitle('Map')
        
        self.map_btn = QPushButton('map', self)
        self.map_btn.move(0, 850)
        self.map_btn.resize(100, 40)
        self.map_btn.clicked.connect(self.change_l)
        
        self.sat_btn = QPushButton('sat', self)
        self.sat_btn.move(100, 850)
        self.sat_btn.resize(100, 40)
        self.sat_btn.clicked.connect(self.change_l)
        
        self.gibrid_btn = QPushButton('sat,skl', self)
        self.gibrid_btn.move(200, 850)
        self.gibrid_btn.resize(100, 40)
        self.gibrid_btn.clicked.connect(self.change_l)
        
        self.response()

    def response(self):
        api_server = f"http://static-maps.yandex.ru/1.x/"
        map_params = {'ll': f'{self.ll[0]},{self.ll[1]}',
                      'spn': str(self.spn[0]) + ',' + str(self.spn[1]),
                      'l': self.l}
        response = requests.get(api_server, params=map_params)
        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request + '?' + '&'.join([f'{k}={map_params[k]}' for k in map_params.keys()]))
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)
        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)
        self.ran()

    def ran(self):
        img = Image.open(self.map_file)
        # print(img.size)
        img = img.resize((width, height - 40))
        img.save(self.map_file)
        self.pixmap = QPixmap(self.map_file)
        self.image.move(0, 0)
        self.image.setPixmap(self.pixmap)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp and self.spn[0] > 0.0009765625:
            self.spn[0] /= 2
            self.spn[1] /= 2
            print(self.spn)
        elif event.key() == Qt.Key_PageDown and self.spn[0] < 8:
            self.spn[0] *= 2
            self.spn[1] *= 2
            print(self.spn)
        elif event.key() == Qt.Key_Up and self.ll[1] + self.spn[1] <= 180:
            self.ll[1] += self.spn[1]
        elif event.key() == Qt.Key_Down and self.ll[1] - self.spn[1] >= -180:
            self.ll[1] -= self.spn[1]
        elif event.key() == Qt.Key_Right and self.ll[0] + self.spn[0] <= 180:
            self.ll[0] += self.spn[0]
        elif event.key() == Qt.Key_Left and self.ll[0] - self.spn[0] >= -180:
            self.ll[0] -= self.spn[0]
        print(self.ll)
        self.response()
    
    def change_l(self):
        self.l = self.sender().text()
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
