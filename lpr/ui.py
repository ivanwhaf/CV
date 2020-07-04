# -*- coding: utf-8 -*-

# author:Ivan
# date:2020-07-03

import os
import sys
import cv2
from PIL import Image
import pytesseract
from PyQt5.QtCore import QRect
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QPushButton, QGraphicsView, QMenuBar, \
    QStatusBar, QGraphicsPixmapItem, QGraphicsScene, QFileDialog
from PyQt5.QtGui import QImage, QPixmap, QFont


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        # Configuration
        self.setWindowTitle("Vehicle License Plate Recognition System")
        self.width, self.height = 1450, 880
        self.setFixedSize(self.width, self.height)

        # GraphicsView
        self.gvW, self.gvH = 450, 350
        self.graphicsView = QGraphicsView(self)
        self.graphicsView.setGeometry(QRect(20, 30, self.gvW, self.gvH))
        self.graphicsView_2 = QGraphicsView(self)
        self.graphicsView_2.setGeometry(QRect(500, 30, self.gvW, self.gvH))
        self.graphicsView_3 = QGraphicsView(self)
        self.graphicsView_3.setGeometry(QRect(980, 30, self.gvW, self.gvH))
        self.graphicsView_4 = QGraphicsView(self)
        self.graphicsView_4.setGeometry(QRect(20, 400, self.gvW, self.gvH))
        self.graphicsView_5 = QGraphicsView(self)
        self.graphicsView_5.setGeometry(QRect(500, 400, self.gvW, self.gvH))
        self.graphicsView_6 = QGraphicsView(self)
        self.graphicsView_6.setGeometry(QRect(980, 400, self.gvW, self.gvH))
        self.graphicsView_7 = QGraphicsView(self)
        self.graphicsView_7.setGeometry(QRect(500, 780, 198, 63))
        self.graphicsView_8 = QGraphicsView(self)
        self.graphicsView_8.setGeometry(QRect(720, 780, 198, 63))

        # PushButton
        self.pushButton = QPushButton("Detect", self)
        self.pushButton.setGeometry(QRect(20, 790, 100, 40))
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.detect)

        # Label
        self.label = QLabel(self)
        self.label.setGeometry(QRect(220, 790, 220, 50))
        self.label.setText("vecicle license：")
        self.label.setFont(QFont("Roman times", 18, QFont.Bold))

        # MenuBar
        self.menuBar = QMenuBar()
        menu = self.menuBar.addMenu("Menu")
        self.setMenuBar(self.menuBar)  # 必须加上,不然不显示
        menu.addAction('Open')
        menu.triggered.connect(self.process_trigger)  # 绑定触发函数

        # StatusBar
        self.statusBar = QStatusBar()
        self.statusBar.showMessage("welcome to this lpr demo！")
        self.setStatusBar(self.statusBar)  # 必须加上,不然不显示

        # Image
        self.img = cv2.imread('1.jpg')  # 加载原始图像

    def process_trigger(self, q):
        # 菜单栏触发函数
        if q.text() == "Open":
            file, _ = QFileDialog.getOpenFileName(self, "选择文件", '.', 'Image files (*.jpg *.gif *.png *.jpeg)')
            if not file:
                return
            self.img = cv2.imread(file)  # 更换图像
            self.show_origin_img()
            # 清空剩余gv上显示的图片
            self.graphicsView_2.setScene(QGraphicsScene().addItem(QGraphicsPixmapItem(QPixmap(""))))
            self.graphicsView_3.setScene(QGraphicsScene().addItem(QGraphicsPixmapItem(QPixmap(""))))
            self.graphicsView_4.setScene(QGraphicsScene().addItem(QGraphicsPixmapItem(QPixmap(""))))
            self.graphicsView_5.setScene(QGraphicsScene().addItem(QGraphicsPixmapItem(QPixmap(""))))
            self.graphicsView_6.setScene(QGraphicsScene().addItem(QGraphicsPixmapItem(QPixmap(""))))
            self.graphicsView_7.setScene(QGraphicsScene().addItem(QGraphicsPixmapItem(QPixmap(""))))
            self.graphicsView_8.setScene(QGraphicsScene().addItem(QGraphicsPixmapItem(QPixmap(""))))
            self.label.setText("")
            self.statusBar.showMessage(file)

    def show_origin_img(self):
        # 左窗口显示原始图像
        img = self.img.copy()
        self.show_image_on_gv(img, self.graphicsView, self.gvW, self.gvH, "bgr")

    def show_image_on_gv(self, img, gv, w, h, model):
        # 将图片显示在GraphicsView上
        img = cv2.resize(img, (w - 2, h - 2))  # 调整到和graphicsView差不多长宽，但不能一样，会显示错误
        h, w = img.shape[:2]
        if model == "gray":
            img = QImage(img, w, h, QImage.Format_Grayscale8)
        if model == "bgr":
            img = QImage(img, w, h, QImage.Format_BGR888)
        if model == "rgb":
            img = QImage(img, w, h, QImage.Format_RGB888)

        pix = QPixmap.fromImage(img)
        item = QGraphicsPixmapItem(pix)
        scene = QGraphicsScene()
        scene.addItem(item)
        gv.setScene(scene)

    def detect(self):
        # 点击按钮对原始图像进行相应处理
        img = self.img.copy()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # BGR转GRAY
        gray = cv2.GaussianBlur(gray, (3, 3), 0)  # 高斯模糊去噪
        self.show_image_on_gv(gray, self.graphicsView_2, self.gvW, self.gvH, "gray")

        gray = cv2.Sobel(gray, cv2.CV_16S, 1, 1, 5)  # Sobel算子滤波
        gray = cv2.convertScaleAbs(gray)
        self.show_image_on_gv(gray, self.graphicsView_3, self.gvW, self.gvH, "gray")

        # ret, thresh = cv2.threshold(gray, 110, 255, cv2.THRESH_BINARY)  # 简单阈值
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY)  # Otsu大津算法阈值
        # thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 3, 1)  # 自适应阈值
        # thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 3, 1)  # 自适应阈值
        self.show_image_on_gv(thresh, self.graphicsView_4, self.gvW, self.gvH, "gray")

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))  # 指定形状结构元素作为闭操作的核
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)  # 形态学闭操作
        # th2 = cv2.GaussianBlur(thresh, (3, 3), 0)  # 高斯模糊去噪
        thresh = cv2.medianBlur(thresh, 3)  # 中值模糊去噪
        self.show_image_on_gv(thresh, self.graphicsView_5, self.gvW, self.gvH, "gray")

        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  # 查找轮廓
        print("轮廓数量：", len(contours))
        # img = cv2.drawContours(img, contours, -1, (0, 255, 0), 3)  # 绘制轮廓

        roi = []  # 可能为车牌的区域
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)  # 每一个轮廓的外接矩形
            ratio = 3.1428  # 长/宽比率
            error = 0.3  # 允许的长/宽比率误差
            if (1 - error) * ratio < (w / h) < (1 + error) * ratio:
                if 1000 < w * h < 40000:
                    img_ = img.copy()
                    roi.append(img_[y:y + h, x:x + w])  # 截取矩形框
                    img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)  # 绘制矩形框
        self.show_image_on_gv(img, self.graphicsView_6, self.gvW, self.gvH, "bgr")

        print('共找到', len(roi), '个可能的车牌区域')

        # 未找到车牌退出
        if not roi:
            self.label.setText("未找到可能的车牌!")
            print("未找到可能的车牌!")
            return

        lp = []  # 车牌文字数组
        for roi_img in roi:
            self.show_image_on_gv(roi_img, self.graphicsView_7, 198, 63, "bgr")
            gray = cv2.cvtColor(roi_img, cv2.COLOR_BGR2GRAY)  # 转为灰度图
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)  # Otsu大津算法
            # _, thresh = cv2.threshold(gray, 110, 255, cv2.THRESH_BINARY_INV)  # 简单阈值
            # thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 3, 1)  # 自适应阈值
            # thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 3, 1)  # 自适应阈值

            # thresh = cv2.resize(thresh, (440, 140))
            # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))  # 指定形状结构元素作为闭操作的核
            # thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)  # 形态学闭操作
            thresh = cv2.medianBlur(thresh, 3)
            # thresh = cv2.GaussianBlur(thresh, (3, 3), 0)

            self.show_image_on_gv(thresh, self.graphicsView_8, 198, 63, "gray")
            # testdata_dir_config = '--tessdata-dir "D:\\Tesseract-OCR\\tessdata"'
            # config = '--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789'.strip()
            text = pytesseract.image_to_string(thresh, lang="chi_sim").replace(" ", "")  # 识别文字

            if text != "":
                lp.append(text)
                print('text:', text)
                self.show_image_on_gv(roi_img, self.graphicsView_7, 198, 63, "bgr")
                self.show_image_on_gv(thresh, self.graphicsView_8, 198, 63, "gray")

        if not lp:
            print('未识别出车牌')
            self.label.setText('未识别出车牌')
        else:
            self.label.setText('\n'.join(lp))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    main_window.show_origin_img()
    sys.exit(app.exec_())
