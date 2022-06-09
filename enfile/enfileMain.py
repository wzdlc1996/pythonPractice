# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'enfileMain.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from enfileUtils import *


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 200)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(20, 160, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.label_pass = QtWidgets.QLabel(Dialog)
        self.label_pass.setGeometry(QtCore.QRect(30, 20, 81, 21))
        self.label_pass.setObjectName("label_pass")

        self.label_from = QtWidgets.QLabel(Dialog)
        self.label_from.setGeometry(QtCore.QRect(30, 60, 81, 21))
        self.label_from.setObjectName("label_from")

        self.label_to = QtWidgets.QLabel(Dialog)
        self.label_to.setGeometry(QtCore.QRect(30, 100, 81, 20))
        self.label_to.setObjectName("label_to")

        self.toolButton_pass = QtWidgets.QToolButton(Dialog)
        self.toolButton_pass.setGeometry(QtCore.QRect(310, 20, 24, 23))
        self.toolButton_pass.setObjectName("toolButton_pass")

        self.toolButton_from = QtWidgets.QToolButton(Dialog)
        self.toolButton_from.setGeometry(QtCore.QRect(310, 60, 24, 23))
        self.toolButton_from.setObjectName("toolButton_from")

        self.toolButton_to = QtWidgets.QToolButton(Dialog)
        self.toolButton_to.setGeometry(QtCore.QRect(310, 100, 24, 23))
        self.toolButton_to.setObjectName("toolButton_to")

        self.toolButton_pass.clicked.connect(self.open_file_pass)
        self.toolButton_from.clicked.connect(self.open_file_from)
        self.toolButton_to.clicked.connect(self.open_file_to)

        self.lineEdit_pass = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_pass.setGeometry(QtCore.QRect(120, 20, 181, 24))
        self.lineEdit_pass.setObjectName("lineEdit_pass")
        self.lineEdit_from = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_from.setGeometry(QtCore.QRect(120, 60, 181, 24))
        self.lineEdit_from.setObjectName("lineEdit_from")
        self.lineEdit_to = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_to.setGeometry(QtCore.QRect(120, 100, 181, 24))
        self.lineEdit_to.setObjectName("lineEdit_to")

        self.retranslateUi(Dialog)
        # self.buttonBox.accepted.connect(Dialog.accept) # type: ignore
        self.buttonBox.accepted.connect(self.run)
        self.buttonBox.rejected.connect(Dialog.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label_from.setText(_translate("Dialog", "压缩包路径:"))
        self.label_to.setText(_translate("Dialog", "解压到:"))
        self.label_pass.setText(_translate("Dialog", "密码路径"))
        self.toolButton_from.setText(_translate("Dialog", "..."))
        self.toolButton_to.setText(_translate("Dialog", "..."))
        self.toolButton_pass.setText(_translate("Dialog", "..."))

    def _open_file(self, wid):
        filename = QtWidgets.QFileDialog.getOpenFileName(None, "Open", "")
        if filename[0] != '':
            wid.setText(filename[0])

    def _open_folder(self, wid):
        filename = QtWidgets.QFileDialog.getExistingDirectory(None, "Open")
        if filename != '':
            wid.setText(filename)

    def open_file_pass(self):
        self._open_file(self.lineEdit_pass)

    def open_file_from(self):
        self._open_folder(self.lineEdit_from)

    def open_file_to(self):
        self._open_folder(self.lineEdit_to)

    def run(self):
        pwd_path = self.lineEdit_pass.text() # "/Users/leonard/Documents/Projects/Temp/enfiles/测试1/密码.txt"
        old_path = self.lineEdit_from.text() # "/Users/leonard/Documents/Projects/Temp/enfiles/测试1/"
        new_path = self.lineEdit_to.text() # "/Users/leonard/Documents/Projects/Temp/enfiles/2/"
        if not makeTempDir(new_path):
            print("已存在success/failed文件夹, 其中文件可能被覆盖")
            pass

        passwords = getPasswordList(pwd_path)

        failed_files = each_file(old_path, new_path, passwords)
        print("\n失败文件列表:")
        for x in failed_files:
            print("\t", x)
