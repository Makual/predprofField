# импортируем нужные библиотеки
import csv
import sys, random
import shutil
import os
from zipfile import ZipFile
from PyQt5 import uic, QtCore, QtWidgets
from PyQt5.QtGui import QPen, QPainter, QBrush
from PyQt5.QtWidgets import QApplication, QMessageBox, QMainWindow, QFileDialog
from PyQt5.QtCore import Qt
import numpy as np
import cv2
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

# подстраиваем интерфейс под расширение экрана
if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)


def get_output_layers(net):
    layer_names = net.getLayerNames()
    output_layers = []
    for i in net.getUnconnectedOutLayers():
        output_layers.append(layer_names[i - 1])
    return output_layers


def draw_prediction(img, class_id, confidence, x, y, x_plus_w, y_plus_h):
    color = 0
    cv2.rectangle(img, (x, y), (x_plus_w, y_plus_h), color, 2)


classes = ['BASE']


def predict(path, shet, kol):
    image = cv2.imread('.\\photoes_from_data_546712\\' + path)
    config = './yolov4-tiny-custom.cfg'
    weights = './yolov4-tiny-custom_final.weights'
    Width = image.shape[1]
    Height = image.shape[0]
    scale = 0.00392
    net = cv2.dnn.readNet(weights, config)
    blob = cv2.dnn.blobFromImage(image, scale, (1024, 1024), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(get_output_layers(net))
    class_ids = []
    confidences = []
    boxes = []
    conf_threshold = 0.5
    nms_threshold = 1
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                center_x = int(detection[0] * Width)
                center_y = int(detection[1] * Height)
                w = int(detection[2] * Width)
                h = int(detection[3] * Height)
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                class_ids.append(class_id)
                confidences.append(float(confidence))
                boxes.append((x, y, w + x, h + y))
    indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)
    for i in indices:
        box = boxes[i]
        x = box[0]
        y = box[1]
        w = box[2]
        h = box[3]
        draw_prediction(image, class_ids[i], confidences[i], round(x), round(y), round(w), round(h))
    finBoxes = []
    for i in indices:
        finBoxes.append(boxes[i])
    if kol == -1:
        return image, finBoxes


class Upload(QMainWindow):
    def __init__(self):
        self.photoes_sp = {}
        self.squares_sp = {}
        self.coords = {}
        self.fields = []
        super().__init__()
        uic.loadUi('designPredprof.ui', self)
        self.photoes = ''
        self.square = ''
        self.shet = 1
        self.lblSquare.hide()
        self.lblPhoto.hide()
        self.btnRun.clicked.connect(self.run)
        self.btnSquareUpload.clicked.connect(self.add_square)
        self.btnPhotoUpload.clicked.connect(self.add_photo)
        self.comboBox.currentTextChanged.connect(self.change)

    def change(self):
        self.photoes = ''
        self.square = ''
        if self.comboBox.currentText() == 'Файл с координатами поля и фото участков поля заргужаются отдельно':
            self.lblSquare.hide()
            self.lblSquare.move(500, 355)
            self.lblSquare_3.show()
            self.lblSquare_3.move(215, 400)
            self.btnPhotoUpload.show()
            self.btnPhotoUpload.move(450, 780)
            self.lblPhoto.hide()
            self.lblPhoto.move(500, 860)
            self.lblSquare_2.resize(1000, 30)
            self.lblSquare_2.setText("Загрузите файл с координатами вершин поля или архив, содержащий "
                                     "файлы с координатами вершин поля (.txt, .zip)")
            self.lblSquare_2.move(125, 200)
            self.btnSquareUpload.move(450, 265)
        else:
            self.lblSquare.hide()
            self.lblSquare_3.hide()
            self.btnPhotoUpload.hide()
            self.lblPhoto.hide()
            self.lblSquare_2.resize(1000, 300)
            self.lblSquare_2.setText("Загрузите архив с данными (.zip, .rar, .7zip)\n\n"
                                     "Имена загружаемых фото должны быть составлены по следующему принципу:\n"
                                     "Foto_..._..._..._..._... (возможные форматы фото: .png, .jpg)\n"
                                     "Первое число - номер поля, к которому относится эта фотография\n"
                                     "Второе число - номер фотографии (для каждого поля нумерация начинается с 1)\n"
                                     "Третье число - координата Х точки, в которой сделано фото. Дана в метрах.\n"
                                     "Четвёртое число - координата Y точки, в которой сделано фото. Дана в метрах.\n"
                                     "Пятое число - высота квадрокоптера над землёй в момент фотографирования. "
                                     "Дана в САНТИМЕТРАХ.\n\nПример: Foto_1_4_202_330_223.png")
            self.lblSquare_2.move(125, 350)
            self.lblSquare.move(500, 750)
            self.btnSquareUpload.move(450, 670)

    def add_square(self):
        self.lblSquare.hide()
        self.square = QFileDialog.getOpenFileName(self, 'Выбрать файл', '')[0]
        if self.square != '':
            self.lblSquare.show()

    def add_photo(self):
        self.lblPhoto.hide()
        self.photoes = QFileDialog.getOpenFileName(self, 'Выбрать файл', '')[0]
        if self.photoes != '':
            self.lblPhoto.show()

    def run(self):
        if self.comboBox.currentText() == 'Файл с координатами поля и фото участков поля заргужаются отдельно':
            if self.square == '':
                valid = QMessageBox.warning(self, '', "Пожалуйста загрузите файл с координатами площади поля",
                                            QMessageBox.Ok)
            elif self.photoes == '':
                valid = QMessageBox.warning(self, '', "Пожалуйста загрузите фотографии участков поля",
                                            QMessageBox.Ok)
            else:
                try:
                    self.raspak_for_two()
                    if self.photoes_sp == {} or self.squares_sp == {}:
                        valid = QMessageBox.warning(self, '', "Пожалуйста загрузите и файлы с координатами поля и "
                                                              "фотографии участков поля",
                                                    QMessageBox.Ok)
                        self.lblSquare.hide()
                        self.lblPhoto.hide()
                        shutil.rmtree('photoes_from_data_546712', ignore_errors=True)
                    else:
                        self.res_form = ResWidget(self.squares_sp, self.photoes_sp, self.coords, self.fields)
                        self.res_form.show()
                        self.hide()
                except Exception as ex:
                    print(ex)
                    valid = QMessageBox.warning(self, '', "Файлы поврежденны или загруженны в неправильном формате",
                                                QMessageBox.Ok)
                    self.lblSquare.hide()
                    self.lblPhoto.hide()
        else:
            if self.square == '':
                valid = QMessageBox.warning(self, '', "Пожалуйста загрузите архив с файлами",
                                            QMessageBox.Ok)
            else:
                try:
                    self.raspak_for_one()
                    if self.photoes_sp == {} or self.squares_sp == {}:
                        valid = QMessageBox.warning(self, '', "Пожалуйста загрузите и файлы с координатами поля и "
                                                              "фотографии участков поля",
                                                    QMessageBox.Ok)
                        self.lblSquare.hide()
                        self.lblPhoto.hide()
                        shutil.rmtree('photoes_from_data_546712', ignore_errors=True)
                    else:
                        self.res_form = ResWidget(self.squares_sp, self.photoes_sp, self.coords, self.fields)
                        self.res_form.show()
                        self.hide()
                        self.lblSquare.hide()
                except Exception as ex:
                    valid = QMessageBox.warning(self, '', "Файлы поврежденны или загруженны в неправильном формате",
                                                QMessageBox.Ok)
                    self.lblSquare.hide()

    def raspak_for_two(self):
        self.photoes_sp = {}
        self.squares_sp = {}
        self.coords = {}
        self.fields = []
        sp = {}
        with ZipFile(self.photoes, 'r') as zip_file:
            zip_file.extractall('{}\\photoes_from_data_546712'.format(os.getcwd()))
        file = os.listdir('photoes_from_data_546712')
        for i in file:
            if i[:4] == 'Foto':
                t = i[i.index('_') + 1:]
                t = int(t[:t.index('_')])
                if t in self.photoes_sp.keys():
                    self.photoes_sp[t].append(i)
                else:
                    self.photoes_sp[t] = []
                    self.photoes_sp[t].append(i)
        if self.square[-1] == 'p':
            with ZipFile(self.square, 'r') as zip_file:
                zip_file.extractall('{}\\square_from_data_984601'.format(os.getcwd()))
            file = os.listdir('square_from_data_984601')
            self.fields = file
            for i in file:
                if i[:5] == 'Field':
                    with open('square_from_data_984601\\{}'.format(i), encoding='utf-8') as f:
                        for j in f:
                            n = int(i[5:i.index('.')])
                            if n in sp.keys():
                                sp[n].append(j)
                            else:
                                sp[n] = []
                                sp[n].append(j)
            for u in sp.keys():
                i = sp[u][0]
                p = 0
                h = 0
                k = i[1:len(i) - 1].replace(', (', '*(').split('*')
                spisok = []
                for j in k:
                    f = list(map(int, j.replace('(', '').replace(')', '').split(', ')))
                    spisok.append(f)
                if u in self.coords.keys():
                    self.coords[u].append(spisok)
                else:
                    self.coords[u] = []
                    self.coords[u].append(spisok)
                for j in range(len(spisok) - 1):
                    p += spisok[j][0] * spisok[j + 1][1]
                    h += spisok[j + 1][0] * spisok[j][1]
                p += spisok[-1][0] * spisok[0][1]
                h += spisok[0][0] * spisok[-1][1]
                if u in self.squares_sp.keys():
                    self.squares_sp[u].append(abs(p - h) * 0.5)
                else:
                    self.squares_sp[u] = []
                    self.squares_sp[u].append(abs(p - h) * 0.5)
            shutil.rmtree('square_from_data_984601', ignore_errors=True)
        else:
            self.fields.append(self.square.split('/')[-1])
            with open(self.square, mode="r", encoding='utf-8') as file:
                for i in file:
                    n = int(self.square.split('/')[-1][5:self.square.split('/')[-1].index('.')])
                    if n in sp.keys():
                        sp[n].append(i)
                    else:
                        sp[n] = []
                        sp[n].append(i)
                for u in sp.keys():
                    i = sp[u][0]
                    p = 0
                    h = 0
                    k = i[1:len(i) - 1].replace(', (', '*(').split('*')
                    spisok = []
                    for j in k:
                        f = list(map(int, j.replace('(', '').replace(')', '').split(', ')))
                        spisok.append(f)
                    if u in self.coords.keys():
                        self.coords[u].append(spisok)
                    else:
                        self.coords[u] = []
                        self.coords[u].append(spisok)
                    for j in range(len(spisok) - 1):
                        p += spisok[j][0] * spisok[j + 1][1]
                        h += spisok[j + 1][0] * spisok[j][1]
                    p += spisok[-1][0] * spisok[0][1]
                    h += spisok[0][0] * spisok[-1][1]
                    if u in self.squares_sp.keys():
                        self.squares_sp[u].append(abs(p - h) * 0.5)
                    else:
                        self.squares_sp[u] = []
                        self.squares_sp[u].append(abs(p - h) * 0.5)
                shutil.rmtree('square_from_data_984601', ignore_errors=True)

    def raspak_for_one(self):
        self.photoes_sp = {}
        self.squares_sp = {}
        self.coords = {}
        self.fields = []
        sp = {}
        with ZipFile(self.square, 'r') as zip_file:
            zip_file.extractall('{}\\photoes_from_data_546712'.format(os.getcwd()))
            file = os.listdir('photoes_from_data_546712')
            for i in file:
                if i[:4] == 'Foto':
                    t = i[i.index('_') + 1:]
                    t = int(t[:t.index('_')])
                    if t in self.photoes_sp.keys():
                        self.photoes_sp[t].append(i)
                    else:
                        self.photoes_sp[t] = []
                        self.photoes_sp[t].append(i)
                else:
                    self.fields.append(i)
                    with open('photoes_from_data_546712\\{}'.format(i), mode='r', encoding='utf-8') as f:
                        for j in f:
                            n = int(i[5:i.index('.')])
                            if n in sp.keys():
                                sp[n].append(j)
                            else:
                                sp[n] = []
                                sp[n].append(j)
            for u in sp.keys():
                i = sp[u][0]
                p = 0
                h = 0
                k = i[1:len(i) - 1].replace(', (', '*(').split('*')
                spisok = []
                for j in k:
                    f = list(map(int, j.replace('(', '').replace(')', '').split(', ')))
                    spisok.append(f)
                if u in self.coords.keys():
                    self.coords[u].append(spisok)
                else:
                    self.coords[u] = []
                    self.coords[u].append(spisok)
                for j in range(len(spisok) - 1):
                    p += spisok[j][0] * spisok[j + 1][1]
                    h += spisok[j + 1][0] * spisok[j][1]
                p += spisok[-1][0] * spisok[0][1]
                h += spisok[0][0] * spisok[-1][1]
                if u in self.squares_sp.keys():
                    self.squares_sp[u].append(abs(p - h) * 0.5)
                else:
                    self.squares_sp[u] = []
                    self.squares_sp[u].append(abs(p - h) * 0.5)


class ResWidget(Upload):
    def __init__(self, squares_sp, photoes_sp, coords, fields):
        super().__init__()
        self.flag = True
        self.coords = coords
        self.fields = fields
        self.squares_sp = squares_sp
        self.photoes_sp = photoes_sp
        self.list = {}
        self.boxes = {}
        self.dic = {}
        uic.loadUi('ResWidget.ui', self)
        self.lblDownload.hide()
        for paths in self.photoes_sp.keys():
            for path in self.photoes_sp[paths]:
                k = path[path.index('_') + 1:]
                shet = k[:k.index('_')]
                h, t = predict(path, shet, -1)
                if int(shet) in self.list.keys():
                    self.list[int(shet)].append(h)
                else:
                    self.list[int(shet)] = []
                    self.list[int(shet)].append(h)
                if int(shet) in self.boxes.keys():
                    self.boxes[int(shet)].append(t)
                else:
                    self.boxes[int(shet)] = []
                    self.boxes[int(shet)].append(t)
                if int(shet) in self.dic.keys():
                    self.dic[int(shet)].append(t)
                else:
                    self.dic[int(shet)] = []
                    self.dic[int(shet)].append(t)
        sp = []
        for i in self.fields:
            i = i[5:i.index('.')]
            sp.append(int(i))
        k = sorted(sp)
        for i in k:
            self.comboBox.addItem('Поле {}'.format(i))
        self.lblSquares.setText('Площадь поля: ' + self.area() + ' м^2')
        self.lblSrPlot.setText('Cредняя плотность пшеницы на поле: ' + self.sred_plot() + ' шт/метр')
        self.lblKol.setText('Общее число колосьев на поле: ' + self.kol() + ' шт')
        self.comboBox.currentTextChanged.connect(self.remake)
        self.btnReturn.clicked.connect(self.back)
        self.btnZagruzka.clicked.connect(self.razmetka)

    def back(self):
        self.flag = True
        shutil.rmtree('photoes_from_data_546712', ignore_errors=True)
        self.back_form = Upload()
        self.back_form.show()
        self.hide()

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.drawLines(qp)
        qp.end()

    def drawLines(self, qp):
        pen = QPen(Qt.darkGreen, 4)
        qp.setPen(pen)
        brush = QBrush(Qt.darkGreen)
        qp.setBrush(brush)
        qp.drawRect(10, 250, 1230, 340)
        

        
            
        pen = QPen(Qt.red, 10)
        qp.setPen(pen)
        g = self.comboBox.currentText()
        g = int(g[g.index(' ') + 1:])
        for i in self.photoes_sp[g]:
            k = i[i.index('_') + 1:]
            if int(k[:k.index('_')]) == g:
                k = k[k.index('_') + 1:]
                k = k[k.index('_') + 1:]
                x = int(float(k[:k.index('_')]) * 1.23 + 10)
                k = k[k.index('_') + 1:]
                y = int(float(k[:k.index('_')]) * 0.34 + 250)
                qp.drawPoint(x, y)
        pen = QPen(Qt.red, 4)
        qp.setPen(pen)
        k = self.comboBox.currentText()
        k = int(k[k.index(' ') + 1:])
        for i in self.coords[k]:
            for j in range(len(i) - 1):
                qp.drawLine(int(i[j][0] * 1.23 + 10), int(i[j][1] * 0.34 + 250),
                            int(i[j + 1][0] * 1.23 + 10), int(i[j + 1][1] * 0.34 + 250))
            qp.drawLine(int(i[-1][0] * 1.23 + 10), int(i[-1][1] * 0.34 + 250),
                        int(i[0][0] * 1.23 + 10), int(i[0][1] * 0.34 + 250))


        newPolygon = []
        for i in range(len(self.coords[k][0])):
            newPolygon.append([0,0])
            newPolygon[i][0] = self.coords[k][0][i][0] * 1.23 + 10
            newPolygon[i][1] = self.coords[k][0][i][1]* 0.34 + 250

        
            
        polygon  = Polygon(newPolygon)


        pen = QPen(Qt.darkYellow, 4)
        qp.setPen(pen)
        k = int(500 * float(self.sred_plot()))
        for i in range(k):
            x = random.randint(10, 1240)
            y = random.randint(250, 590)
            if polygon.contains(Point(x,y)):
                qp.drawPoint(x, y)

    def closeEvent(self, event):
        shutil.rmtree('photoes_from_data_546712', ignore_errors=True)
        event.accept()

    def remake(self):
        self.lblSquares.setText('Площадь поля: ' + self.area() + ' м^2')
        self.lblSrPlot.setText('Cредняя плотность пшеницы на поле: ' + self.sred_plot() + ' шт/метр')
        self.lblKol.setText('Общее число колосьев на поле: ' + self.kol() + ' шт')
        self.update()

    def razmetka(self):
        if self.flag:
            kol = 1
            while os.path.exists('./Wheat_Markup_{}'.format(kol)):
                kol += 1
            os.mkdir('./Wheat_Markup_{}'.format(kol))
            os.mkdir('./Wheat_Boxes_{}'.format(kol))
            for i in self.photoes_sp.keys():
                paths = self.photoes_sp[i]
                k = paths[0][paths[0].index('_') + 1:]
                shet = k[:k.index('_')]
                if not os.path.exists('./Wheat_Markup_{}/Field_{}'.format(kol, shet)):
                    os.mkdir('./Wheat_Markup_{}/Field_{}'.format(kol, shet))
                if not os.path.exists('./Wheat_Boxes_{}/Field_{}'.format(kol, shet)):
                    os.mkdir('./Wheat_Boxes_{}/Field_{}'.format(kol, shet))
                for path in paths:
                    k = path[path.index('_') + 1:]
                    num = k[:k.index('_')]
                    k = k[k.index('_') + 1:]
                    num_of = k[:k.index('_')]
                    cv2.imwrite('./Wheat_Markup_{}/Field_{}/Marked_Field_{}_{}.png'.format(kol, shet, num, num_of),
                                self.list[int(num)][int(num_of) - 1])
                    with open('./Wheat_Boxes_{}/Field_{}/MarkedCoords_Field_{}_{}.csv'.format(kol, shet, num, num_of),
                              'w', encoding='utf-8', newline='') as f:
                        writer = csv.DictWriter(f, delimiter=';', quotechar='"',
                                                fieldnames=['x_min', 'y_min', 'x_max', 'y_max'],
                                                quoting=csv.QUOTE_MINIMAL)
                        data = []
                        for i in self.boxes[int(num)][int(num_of) - 1]:
                            k = {}
                            k['x_min'] = i[0]
                            k['y_min'] = i[1]
                            k['x_max'] = i[2]
                            k['y_max'] = i[3]
                            data.append(k)
                        writer.writeheader()
                        for i in data:
                            writer.writerow(i)
            self.lblDownload.show()
            self.flag = False
        else:
            self.lblDownload.hide()
            valid = QMessageBox.warning(self, '', "Эти данные уже были загружены",
                                        QMessageBox.Ok)

    # рассчитываем площадь поля
    def area(self):
        g = self.comboBox.currentText()
        g = int(g[g.index(' ') + 1:])
        return str(self.squares_sp[g][0])

    # вычисляем среднюю плотность пшеницы на поле
    def sred_plot(self):
        s = 0
        summa = 0
        kol = 0
        g = self.comboBox.currentText()
        g = int(g[g.index(' ') + 1:])
        if g in sorted(self.dic.keys()):  # если для выбранного поля загруженны фото, то вычисляем
            for j in range(len(self.dic[g])):
                i = self.photoes_sp[g][j]
                k = i[5:]
                k = k[k.index('_') + 1:]
                k = k[k.index('_') + 1:]
                k = k[k.index('_') + 1:]
                k = k[k.index('_') + 1:]
                a = int(k[:k.index('.')]) / 100 - 1.05
                f = len(self.dic[g][j])
                p = len(self.dic[g][j]) / (((1.73205 * a) * 2) * ((0.70020 * a) * 2))
                summa += p
                kol += 1
            plot = round(summa / kol, 3)
            return str(plot)
        else:  # иначе
            return '0'  # возвращаем 0

    # рассчитываем количество колосков на всем поле
    def kol(self):
        g = self.comboBox.currentText()
        g = int(g[g.index(' ') + 1:])
        if int(g) in self.dic.keys():  # если для выбранного поля загруженны фото, то вычисляем
            k = self.lblSrPlot.text()[self.lblSrPlot.text().index(':') + 2:]
            k = float(k[:k.index(' ')])
            p = self.squares_sp[g][0]
            sq = k * self.squares_sp[g][0]
            return str(round(sq))
        else:
            return '0'  # возвращаем 0


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Upload()
    ex.show()
    sys.exit(app.exec_())
