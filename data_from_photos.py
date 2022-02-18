import sys
import shutil
import os
from zipfile import ZipFile
from PyQt5 import uic
from PyQt5.QtGui import QPixmap, QPen, QPainter, QBrush
from PyQt5.QtWidgets import QApplication, QMessageBox, QMainWindow, QFileDialog
from PyQt5.QtCore import Qt
import numpy as np
import cv2


def get_output_layers(net):
    
    layer_names = net.getLayerNames()

    output_layers = []
    
    for i in net.getUnconnectedOutLayers():

        output_layers.append(layer_names[i - 1] )

    return output_layers




def draw_prediction(img, class_id, confidence, x, y, x_plus_w, y_plus_h):

    

    color = 0

    cv2.rectangle(img, (x,y), (x_plus_w,y_plus_h), color, 2)

    


classes = ['BASE']





def predict(path):
    image = cv2.imread(path)



        
    config = './yolov4-tiny-custom.cfg'
    weights = './yolov4-tiny-custom_final.weights'
    classes = './classes.txt'
        
    Width = image.shape[1]
    Height = image.shape[0]
    scale = 0.00392

    net = cv2.dnn.readNet(weights, config)

    blob = cv2.dnn.blobFromImage(image, scale, (1024,1024), (0,0,0), True, crop=False)

    net.setInput(blob)

    outs = net.forward(get_output_layers(net))

    class_ids = []
    confidences = []
    boxes = []
    conf_threshold = 0.5
    nms_threshold = 0.4


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
                boxes.append((x, y, w+x, h+y))


    indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)




    for i in indices:
        box = boxes[i]
        x = box[0]
        y = box[1]
        w = box[2]
        h = box[3]
        draw_prediction(image, class_ids[i], confidences[i], round(x), round(y), round(w), round(h))

    

    ###################Добавить папки и разделить сохранненые текстовые файлы по полям
    cv2.imwrite('./Wheat_Markup/marked_'+path,image)


    
    with open('./Wheat_Boxes/marked_'+path.replace('.png','.txt'),'w',encoding='utf-8') as f:
        for i in boxes:
            for j in i:
                f.write(str(j)+' ')

            f.write('\n')
            
    ####################################
    
    return boxes


class Upload(QMainWindow):
    def __init__(self):
        self.photoes_sp = []
        self.squares_sp = []
        self.coords = []
        super().__init__()
        uic.loadUi('designPredprof.ui', self)
        self.photoes = ''
        self.square = ''
        self.lblSquare.hide()
        self.lblPhoto.hide()
        self.btnRun.clicked.connect(self.run)
        self.btnSquareUpload.clicked.connect(self.add_square)
        self.btnPhotoUpload.clicked.connect(self.add_photo)
        self.comboBox.currentTextChanged.connect(self.change)
        self.btnInfo.clicked.connect(self.info)

    def info(self):
        pass

    def change(self):
        self.photoes = ''
        self.square = ''
        if self.comboBox.currentText() == 'Файл с координатами поля и фото участков поля заргужаются отдельно':
            self.lblSquare.hide()
            self.lblSquare.move(500, 350)
            self.lblSquare_3.show()
            self.lblSquare_3.move(190, 450)
            self.btnPhotoUpload.show()
            self.btnPhotoUpload.move(430, 850)
            self.lblPhoto.hide()
            self.lblPhoto.move(490, 940)
            self.lblSquare_2.resize(1080, 30)
            self.lblSquare_2.setText("Загрузите файл с координатами вершин поля или архив, содержащий "
                                     "файлы с координатами вершин поля (.txt, .zip, .rar, .7zip)")
            self.lblSquare_2.move(110, 220)
            self.btnSquareUpload.move(450, 270)
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
            self.lblSquare_2.move(110, 350)
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
                    if self.photoes_sp == [] or self.squares_sp == []:
                        valid = QMessageBox.warning(self, '', "Пожалуйста загрузите и файлы с координатами поля и "
                                                              "фотографии участков поля",
                                                    QMessageBox.Ok)
                    else:
                        self.res_form = ResWidget(self.squares_sp, self.photoes_sp, self.coords)
                        self.res_form.show()
                        self.hide()
                except Exception as ex:
                    print(ex)
                    self.lblSquare.hide()
                    self.lblPhoto.hide()
        else:
            if self.square == '':
                valid = QMessageBox.warning(self, '', "Пожалуйста загрузите архив с файлами",
                                            QMessageBox.Ok)
            else:
                try:
                    self.raspak_for_one()
                    if self.photoes_sp == [] or self.squares_sp == []:
                        valid = QMessageBox.warning(self, '', "Пожалуйста загрузите и файлы с координатами поля и "
                                                              "фотографии участков поля",
                                                    QMessageBox.Ok)
                    else:
                        self.res_form = ResWidget(self.squares_sp, self.photoes_sp, self.coords)
                        self.res_form.show()
                        self.hide()
                        self.lblSquare.hide()
                except Exception as ex:
                    print(ex)
                    self.lblSquare.hide()

    def raspak_for_two(self):
        self.photoes_sp = []
        self.squares_sp = []
        self.coords = []
        sp = []
        with ZipFile(self.photoes, 'r') as zip_file:
            zip_file.extractall('{}\\photoes_from_data_546712'.format(os.getcwd()))
        file = os.listdir('photoes_from_data_546712')
        for i in file:
            if i[:4] == 'Foto':
                self.photoes_sp.append(i)
        shutil.rmtree('photoes_from_data_546712', ignore_errors=True)
        if self.square[-1] == 'p':
            with ZipFile(self.square, 'r') as zip_file:
                zip_file.extractall('{}\\square_from_data_984601'.format(os.getcwd()))
            file = os.listdir('square_from_data_984601')
            for i in file:
                if i[:5] == 'Field':
                    with open('square_from_data_984601\\{}'.format(i), encoding='utf-8') as f:
                        for j in f:
                            sp.append(j)
            for i in sp:
                p = 0
                h = 0
                k = i[1:len(i) - 1].replace(', (', '*(').split('*')
                spisok = []
                for j in k:
                    f = list(map(int, j.replace('(', '').replace(')', '').split(', ')))
                    spisok.append(f)
                self.coords.append(spisok)
                for j in range(len(spisok) - 1):
                    p += spisok[j][0] * spisok[j + 1][1]
                    h += spisok[j + 1][0] * spisok[j][1]
                p += spisok[-1][0] * spisok[0][1]
                h += spisok[0][0] * spisok[-1][1]
                self.squares_sp.append(abs(p - h) * 0.5)
            shutil.rmtree('square_from_data_984601', ignore_errors=True)
        else:
            with open(self.square, mode="r", encoding='utf-8') as file:
                for i in file:
                    sp.append(i)
                for i in sp:
                    p = 0
                    h = 0
                    k = i[1:len(i) - 1].replace(', (', '*(').split('*')
                    spisok = []
                    for j in k:
                        f = list(map(int, j.replace('(', '').replace(')', '').split(', ')))
                        spisok.append(f)
                    self.coords.append(spisok)
                    for j in range(len(spisok) - 1):
                        p += spisok[j][0] * spisok[j + 1][1]
                        h += spisok[j + 1][0] * spisok[j][1]
                    p += spisok[-1][0] * spisok[0][1]
                    h += spisok[0][0] * spisok[-1][1]
                    self.squares_sp.append(abs(p - h) * 0.5)

    def raspak_for_one(self):
        self.photoes_sp = []
        self.squares_sp = []
        self.coords = []
        sp = []
        with ZipFile(self.square, 'r') as zip_file:
            zip_file.extractall('{}\\list_from_data_592343'.format(os.getcwd()))
            file = os.listdir('list_from_data_592343')
            for i in file:
                if i[:4] == 'Foto':
                    self.photoes_sp.append(i)
                else:
                    with open('list_from_data_592343\\{}'.format(i), mode='r', encoding='utf-8') as f:
                        for j in f:
                            sp.append(j)
            for i in sp:
                p = 0
                h = 0
                k = i[1:len(i) - 1].replace(', (', '*(').split('*')
                spisok = []
                for j in k:
                    f = list(map(int, j.replace('(', '').replace(')', '').split(', ')))
                    spisok.append(f)
                self.coords.append(spisok)
                for j in range(len(spisok) - 1):
                    p += spisok[j][0] * spisok[j + 1][1]
                    h += spisok[j + 1][0] * spisok[j][1]
                p += spisok[-1][0] * spisok[0][1]
                h += spisok[0][0] * spisok[-1][1]
                self.squares_sp.append(abs(p - h) * 0.5)
            shutil.rmtree('list_from_data_592343', ignore_errors=True)


class ResWidget(Upload):
    def __init__(self, squares_sp, photoes_sp, coords):
        super().__init__()
        self.coords = coords
        self.squares_sp = squares_sp
        self.photoes_sp = photoes_sp
        uic.loadUi('ResWidget.ui', self)
        for i in range(1, len(squares_sp) + 1):
            self.comboBox.addItem('Поле {}'.format(i))
        self.lblSquares.setText('Площадь поля: ' + self.area() + ' м^2')
        self.lblSrPlot.setText('Cредняя плотность пшеницы на поле: ' + self.sred_plot() + ' шт/метр')
        self.lblKol.setText('Общее число колосьев на поле: ' + self.kol() + ' шт')
        self.comboBox.currentTextChanged.connect(self.remake)
        self.btnReturn.clicked.connect(self.back)
        self.btnZagruzka.clicked.connect(self.razmetka)

    def back(self):
        self.back_form = Upload()
        self.back_form.show()
        self.hide()

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.drawLines(qp)
        qp.end()

    def drawLines(self, qp):
        brush = QBrush(Qt.white)
        qp.setBrush(brush)
        qp.drawRect(10, 250, 1230, 460)
        pen = QPen(Qt.black, 2)
        qp.setPen(pen)
        k = self.coords[int(self.comboBox.currentText()[-1]) - 1]
        for i in range(len(self.coords[int(self.comboBox.currentText()[-1]) - 1]) - 1):
            qp.drawLine(int(k[i][0] * 1.23 + 10), int(k[i][1] * 0.47 + 250),
                        int(k[i + 1][0] * 1.23 + 10), int(k[i + 1][1] * 0.47 + 250))
        qp.drawLine(int(k[-1][0] * 1.23 + 10), int(k[-1][1] * 0.47 + 250),
                    int(k[0][0] * 1.23 + 10), int(k[0][1] * 0.47 + 250))

    def remake(self):
        self.lblSquares.setText('Площадь поля: ' + self.area() + ' м^2')
        self.lblSrPlot.setText('Cредняя плотность пшеницы на поле: ' + self.sred_plot() + ' шт/метр')
        self.lblKol.setText('Общее число колосьев на поле: ' + self.kol() + ' шт')
        self.update()

    def razmetka(self):
        paths = self.photoes_sp

        boxes = []
         
        for path in paths:
            boxes.append(predict(path))

        return boxes

    def area(self):
        return str(self.squares_sp[int(self.comboBox.currentText()[-1]) - 1])

    def sred_plot(self):
        """Здесь нужна функция, которая будет вычислять среднюю плостность пшеницы на поле"""
        return ''

    def kol(self):
        """Здесь нужна функция, которая будет общее количество колосьев на поле"""
        return ''


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Upload()
    ex.show()
    sys.exit(app.exec_())
