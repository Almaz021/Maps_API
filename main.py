import sys

from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap
import requests
from PIL import Image

width, height = 1000, 850
map_request = "http://static-maps.yandex.ru/1.x/?ll=49.099982%2C55.767306&spn=0.5,0.5&l=map"
response = requests.get(map_request)
map_file = "map.png"
with open(map_file, "wb") as file:
    file.write(response.content)
if not response:
    print("Ошибка выполнения запроса:")
    print(map_request)
    print("Http статус:", response.status_code, "(", response.reason, ")")
    sys.exit(1)


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, width, height)
        self.setWindowTitle('Map')
        self.ran()

    def ran(self):
        img = Image.open(map_file)
        print(img.size)
        img = img.resize((width, height))
        img.save(map_file)
        self.pixmap = QPixmap(map_file)
        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.setPixmap(self.pixmap)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())
