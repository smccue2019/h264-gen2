# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'HyperdeckRecUI.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(876, 780)
        MainWindow.setAutoFillBackground(False)
        MainWindow.setStyleSheet("background-color: rgb(0, 0, 0);")
        MainWindow.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.quitButton = QtWidgets.QPushButton(self.centralwidget)
        self.quitButton.setGeometry(QtCore.QRect(690, 700, 89, 25))
        self.quitButton.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.quitButton.setObjectName("quitButton")
        self.startButton = QtWidgets.QPushButton(self.centralwidget)
        self.startButton.setGeometry(QtCore.QRect(690, 30, 89, 25))
        self.startButton.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.startButton.setObjectName("startButton")
        self.stopButton = QtWidgets.QPushButton(self.centralwidget)
        self.stopButton.setGeometry(QtCore.QRect(690, 70, 89, 25))
        self.stopButton.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.stopButton.setObjectName("stopButton")
        self.DateTimeDisp = QtWidgets.QLabel(self.centralwidget)
        self.DateTimeDisp.setGeometry(QtCore.QRect(60, 30, 150, 30))
        self.DateTimeDisp.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.DateTimeDisp.setFrameShape(QtWidgets.QFrame.Box)
        self.DateTimeDisp.setObjectName("DateTimeDisp")
        self.JDSflash = QtWidgets.QLabel(self.centralwidget)
        self.JDSflash.setGeometry(QtCore.QRect(400, 30, 30, 30))
        self.JDSflash.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.JDSflash.setFrameShape(QtWidgets.QFrame.Box)
        self.JDSflash.setScaledContents(True)
        self.JDSflash.setAlignment(QtCore.Qt.AlignCenter)
        self.JDSflash.setObjectName("JDSflash")
        self.ODRflash = QtWidgets.QLabel(self.centralwidget)
        self.ODRflash.setGeometry(QtCore.QRect(460, 30, 30, 30))
        self.ODRflash.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.ODRflash.setFrameShape(QtWidgets.QFrame.Box)
        self.ODRflash.setScaledContents(False)
        self.ODRflash.setAlignment(QtCore.Qt.AlignCenter)
        self.ODRflash.setObjectName("ODRflash")
        self.clipGB = QtWidgets.QGroupBox(self.centralwidget)
        self.clipGB.setGeometry(QtCore.QRect(60, 80, 520, 140))
        self.clipGB.setStyleSheet("background-color: rgb(128, 128, 128);")
        self.clipGB.setObjectName("clipGB")
        self.clipGB_pte = QtWidgets.QPlainTextEdit(self.clipGB)
        self.clipGB_pte.setGeometry(QtCore.QRect(10, 30, 500, 100))
        font = QtGui.QFont()
        font.setItalic(True)
        self.clipGB_pte.setFont(font)
        self.clipGB_pte.setAutoFillBackground(True)
        self.clipGB_pte.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.clipGB_pte.setReadOnly(False)
        self.clipGB_pte.setPlaceholderText("")
        self.clipGB_pte.setObjectName("clipGB_pte")
        self.clipGB_2 = QtWidgets.QGroupBox(self.centralwidget)
        self.clipGB_2.setGeometry(QtCore.QRect(60, 235, 520, 140))
        self.clipGB_2.setStyleSheet("background-color: rgb(128, 128, 128);")
        self.clipGB_2.setObjectName("clipGB_2")
        self.clipGB_2pte = QtWidgets.QPlainTextEdit(self.clipGB_2)
        self.clipGB_2pte.setGeometry(QtCore.QRect(10, 30, 500, 100))
        font = QtGui.QFont()
        font.setItalic(True)
        self.clipGB_2pte.setFont(font)
        self.clipGB_2pte.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.clipGB_2pte.setObjectName("clipGB_2pte")
        self.clipGB_3 = QtWidgets.QGroupBox(self.centralwidget)
        self.clipGB_3.setGeometry(QtCore.QRect(60, 390, 520, 140))
        self.clipGB_3.setStyleSheet("background-color: rgb(128, 128, 128);")
        self.clipGB_3.setObjectName("clipGB_3")
        self.clipGB_3pte = QtWidgets.QPlainTextEdit(self.clipGB_3)
        self.clipGB_3pte.setGeometry(QtCore.QRect(10, 30, 500, 100))
        font = QtGui.QFont()
        font.setItalic(True)
        self.clipGB_3pte.setFont(font)
        self.clipGB_3pte.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.clipGB_3pte.setObjectName("clipGB_3pte")
        self.idleIcon = QtWidgets.QGroupBox(self.centralwidget)
        self.idleIcon.setGeometry(QtCore.QRect(600, 15, 40, 40))
        self.idleIcon.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.idleIcon.setObjectName("idleIcon")
        self.recIconLabel = QtWidgets.QLabel(self.idleIcon)
        self.recIconLabel.setGeometry(QtCore.QRect(5, 20, 30, 15))
        self.recIconLabel.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.recIconLabel.setText("")
        self.recIconLabel.setObjectName("recIconLabel")
        self.LowIDlabel = QtWidgets.QLabel(self.centralwidget)
        self.LowIDlabel.setGeometry(QtCore.QRect(270, 30, 60, 30))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.LowIDlabel.setFont(font)
        self.LowIDlabel.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.LowIDlabel.setFrameShape(QtWidgets.QFrame.Box)
        self.LowIDlabel.setAlignment(QtCore.Qt.AlignCenter)
        self.LowIDlabel.setObjectName("LowIDlabel")
        self.DPAflash = QtWidgets.QLabel(self.centralwidget)
        self.DPAflash.setGeometry(QtCore.QRect(520, 30, 30, 30))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.DPAflash.setFont(font)
        self.DPAflash.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.DPAflash.setFrameShape(QtWidgets.QFrame.Box)
        self.DPAflash.setAlignment(QtCore.Qt.AlignCenter)
        self.DPAflash.setObjectName("DPAflash")
        self.srtGB = QtWidgets.QGroupBox(self.centralwidget)
        self.srtGB.setGeometry(QtCore.QRect(60, 545, 520, 140))
        self.srtGB.setStyleSheet("background-color: rgb(128, 128, 128);")
        self.srtGB.setObjectName("srtGB")
        self.srtGB_pte = QtWidgets.QPlainTextEdit(self.srtGB)
        self.srtGB_pte.setGeometry(QtCore.QRect(10, 30, 500, 100))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setItalic(True)
        self.srtGB_pte.setFont(font)
        self.srtGB_pte.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.srtGB_pte.setObjectName("srtGB_pte")
        self.clipTimeGB = QtWidgets.QGroupBox(self.centralwidget)
        self.clipTimeGB.setGeometry(QtCore.QRect(660, 570, 120, 80))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.clipTimeGB.setFont(font)
        self.clipTimeGB.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.clipTimeGB.setObjectName("clipTimeGB")
        self.clipTimeLabel = QtWidgets.QLabel(self.clipTimeGB)
        self.clipTimeLabel.setGeometry(QtCore.QRect(0, 30, 89, 30))
        self.clipTimeLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.clipTimeLabel.setObjectName("clipTimeLabel")
        self.deck1_status_pte = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.deck1_status_pte.setGeometry(QtCore.QRect(610, 105, 170, 110))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setItalic(True)
        self.deck1_status_pte.setFont(font)
        self.deck1_status_pte.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.deck1_status_pte.setReadOnly(True)
        self.deck1_status_pte.setOverwriteMode(True)
        self.deck1_status_pte.setPlaceholderText("")
        self.deck1_status_pte.setObjectName("deck1_status_pte")
        self.deck2_status_pte = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.deck2_status_pte.setGeometry(QtCore.QRect(610, 260, 170, 110))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setItalic(True)
        self.deck2_status_pte.setFont(font)
        self.deck2_status_pte.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.deck2_status_pte.setPlaceholderText("")
        self.deck2_status_pte.setObjectName("deck2_status_pte")
        self.deck3_status_pte = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.deck3_status_pte.setGeometry(QtCore.QRect(610, 415, 170, 110))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setItalic(True)
        self.deck3_status_pte.setFont(font)
        self.deck3_status_pte.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.deck3_status_pte.setReadOnly(True)
        self.deck3_status_pte.setOverwriteMode(True)
        self.deck3_status_pte.setPlaceholderText("")
        self.deck3_status_pte.setObjectName("deck3_status_pte")
        self.estopButton = QtWidgets.QPushButton(self.centralwidget)
        self.estopButton.setGeometry(QtCore.QRect(60, 700, 89, 25))
        self.estopButton.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.estopButton.setObjectName("estopButton")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 876, 20))
        self.menuBar.setObjectName("menuBar")
        MainWindow.setMenuBar(self.menuBar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "HyperdeckRecorderUI"))
        self.quitButton.setText(_translate("MainWindow", "Quit"))
        self.startButton.setText(_translate("MainWindow", "Start"))
        self.stopButton.setText(_translate("MainWindow", "Stop"))
        self.DateTimeDisp.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\"><span style=\" font-size:14pt; font-weight:600;\">DateTimeDisp</span></p></body></html>"))
        self.JDSflash.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\"><span style=\" font-size:12pt; font-weight:600;\">J</span></p></body></html>"))
        self.ODRflash.setText(_translate("MainWindow", "<html><head/><body><p align=\"center\"><span style=\" font-size:12pt; font-weight:600;\">O</span></p></body></html>"))
        self.clipGB.setTitle(_translate("MainWindow", "clipGB"))
        self.clipGB_2.setTitle(_translate("MainWindow", "clipGB_2"))
        self.clipGB_3.setTitle(_translate("MainWindow", "clipGB_3"))
        self.idleIcon.setTitle(_translate("MainWindow", "Rec"))
        self.LowIDlabel.setText(_translate("MainWindow", "LowID"))
        self.DPAflash.setText(_translate("MainWindow", "D"))
        self.srtGB.setTitle(_translate("MainWindow", "Subtitle Files Log"))
        self.clipTimeGB.setTitle(_translate("MainWindow", "Remaining Clip Time"))
        self.clipTimeLabel.setText(_translate("MainWindow", "clipTime"))
        self.deck1_status_pte.setDocumentTitle(_translate("MainWindow", "Deck1 Status"))
        self.deck2_status_pte.setDocumentTitle(_translate("MainWindow", "Deck2 Status"))
        self.deck3_status_pte.setDocumentTitle(_translate("MainWindow", "Deck3 Status"))
        self.estopButton.setText(_translate("MainWindow", "ESTOP"))
