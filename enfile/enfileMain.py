# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'enfileMain.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from time import sleep
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication
from enfileUtils import *


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 250)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(20, 200, 341, 32))
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

        # progress bar
        self.progressBar = QtWidgets.QProgressBar(Dialog)
        self.progressBar.setGeometry(QtCore.QRect(120, 160, 181, 24))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(30, 160, 181, 24))
        self.label.setObjectName("label")

        self.retranslateUi(Dialog)
        # self.buttonBox.accepted.connect(Dialog.accept) # type: ignore
        self.buttonBox.accepted.connect(self.run_enfile)
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

        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "等待进程..."))

        self.lineEdit_pass.setText("/home/leonard/Documents/Projects/pythonPractice/enfile/test/pass.txt")
        self.lineEdit_from.setText("/home/leonard/Documents/Projects/pythonPractice/enfile/test/in")
        self.lineEdit_to.setText("/home/leonard/Documents/Projects/pythonPractice/enfile/test/out")

    def _open_file(self, wid):
        filename = QtWidgets.QFileDialog.getOpenFileName(None, "Open", "")
        if filename[0] != '':
            wid.setText(filename[0])

    def _open_folder(self, wid):
        filename = QtWidgets.QFileDialog.getExistingDirectory(None, "Open")
        if filename != '':
            wid.setText(filename)

    def setPrgbarVal(self, val: int):
        self.progressBar.setValue(val)

    def open_file_pass(self):
        self._open_file(self.lineEdit_pass)

    def open_file_from(self):
        self._open_folder(self.lineEdit_from)

    def open_file_to(self):
        self._open_folder(self.lineEdit_to)

    def run_enfile(self):
        pwd_path = self.lineEdit_pass.text() # "/Users/leonard/Documents/Projects/Temp/enfiles/测试1/密码.txt"
        old_path = self.lineEdit_from.text() # "/Users/leonard/Documents/Projects/Temp/enfiles/测试1/"
        new_path = self.lineEdit_to.text() # "/Users/leonard/Documents/Projects/Temp/enfiles/2/"
        
        passwords = getPasswordList(pwd_path)
        
        proj_list = os.listdir(old_path)
        failed_files = []

        # for proj_dir in os.listdir(old_path): # ProgressBarIter(os.listdir(old_path)):
        for i, proj_dir in enumerate(proj_list):
            ori_dir = path.join(old_path, proj_dir)
            if not path.isdir(ori_dir):
                continue
            tar_dir = path.join(new_path, proj_dir)
            try:
                os.makedirs(tar_dir)
            except FileExistsError:
                print(f"已存在{proj_dir}同名文件夹, 其中文件可能被覆盖")

            print(f"from {ori_dir} to {tar_dir}")
            failed_files.append(each_file(
                ori_dir, 
                tar_dir, 
                passwords
            ))

            self.setPrgbarVal(int(100 * i / (len(proj_list) - 1)))
            QApplication.processEvents()
        
        sepr = "-----------"
        logf = open(path.join(new_path, "failed_files.txt"), "w")
        # print("\n失败文件列表:")
        logf.write("失败文件列表:\n\n")
        logf.write(sepr + "\n")
        for par, x in zip(proj_list, failed_files):
            # print(f"In\t{par}")
            logf.write(f"In dir\t{par}\n\n")
            for z in x:
                #print("\t", z)
                logf.write("\t" + z + "\n")
            # print(sepr)
            logf.write(sepr + "\n")