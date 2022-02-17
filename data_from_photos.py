import sys, zlib
import shutil
import requests
import os
from io import BytesIO, StringIO
from zipfile import ZipFile
from PIL import Image
from PyQt5 import uic
from PyQt5.QtGui import QPixmap, QPen, QPainter
from PyQt5.QtWidgets import QApplication, QMessageBox, QMainWindow, QFileDialog


class Upload(QMainWindow):
    def __init__(self):
        self.photoes_sp = []
        self.squares_sp = []
        self.coords = []
        super().__init__()
        uic.loadUi('designPredprof.ui', self)
        self.photoes = ''
        self.zagruzka = False
        self.square = ''
        self.lblSquare.hide()
        self.lblPhoto.hide()
        self.btnRun.clicked.connect(self.run)
        self.btnSquareUpload.clicked.connect(self.add_square)
        self.btnPhotoUpload.clicked.connect(self.add_photo)
        self.btnZagruz.clicked.connect(self.zagruz)
        self.comboBox.currentTextChanged.connect(self.change)

    def zagruz(self):
        if self.btnZagruz.isChecked():
            self.zagruzka = True
        else:
            self.zagruzka = False

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
                        self.res_form = ResWidget(self.zagruzka, self.squares_sp, self.photoes_sp, self.coords)
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
                        self.res_form = ResWidget(self.zagruzka, self.squares_sp, self.photoes_sp, self.coords)
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
            zip_file.extractall('{}\\photoes'.format(os.getcwd()))
        file = os.listdir('photoes')
        for i in file:
            if i[:4] == 'Foto':
                self.photoes_sp.append(i)
        shutil.rmtree('photoes', ignore_errors=True)
        if self.square[-1] == 'p':
            with ZipFile(self.square, 'r') as zip_file:
                zip_file.extractall('{}\\square'.format(os.getcwd()))
            file = os.listdir('square')
            for i in file:
                if i[:5] == 'Field':
                    with open('square\\{}'.format(i), encoding='utf-8') as f:
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
            shutil.rmtree('square', ignore_errors=True)
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
            zip_file.extractall('{}\\data'.format(os.getcwd()))
            file = os.listdir('data')
            for i in file:
                if i[:4] == 'Foto':
                    self.photoes_sp.append(i)
                else:
                    with open('data\\{}'.format(i), mode='r', encoding='utf-8') as f:
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
            shutil.rmtree('data', ignore_errors=True)


class ResWidget(Upload):
    def __init__(self, zagruzka, squares_sp, photoes_sp, coords):
        super().__init__()
        self.coords = coords
        self.zagruzka = zagruzka
        self.squares_sp = squares_sp
        self.photoes_sp = photoes_sp
        uic.loadUi('ResWidget.ui', self)
        self.risunok()
        for i in range(1, len(squares_sp) + 1):
            self.comboBox.addItem('Поле {}'.format(i))
        self.lblSquares.setText('Площадь поля: ' + self.area() + ' м^2')
        self.lblSrPlot.setText('Cредняя плотность пшеницы на поле: ' + self.sred_plot() + ' шт/метр')
        self.lblKol.setText('Общее число колосьев на поле: ' + self.kol() + ' шт')
        if self.zagruzka:
            self.lblZagruzil.show()
            self.lblZagruzil.setText(self.lblZagruzil.text() + '   ' + self.razmetka())
        else:
            self.lblZagruzil.hide()
        self.comboBox.currentTextChanged.connect(self.remake)
        self.btnReturn.clicked.connect(self.back)

    def back(self):
        self.back_form = Upload()
        self.back_form.show()
        self.hide()

    def risunok(self):
        pass

    def remake(self):
        self.lblSquares.setText('Площадь поля: ' + self.area() + ' м^2')
        self.lblSrPlot.setText('Cредняя плотность пшеницы на поле: ' + self.sred_plot() + ' шт/метр')
        self.lblKol.setText('Общее число колосьев на поле: ' + self.kol() + ' шт')
        self.risunok()

    def razmetka(self):
        """Здесь функция, которая размечает колосья на фотографиях и загружает их в папку.
        Если размеченные фотки не получится добавить, то можно просто в текстовый файл записать координаты рамок"""
        return "{}\\Wheat_Markup".format(os.getcwd())

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
