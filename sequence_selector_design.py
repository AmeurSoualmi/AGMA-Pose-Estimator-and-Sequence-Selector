
from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph

class Ui_MainWindow(object):
    """Sequence Selector GUI design:"""
    def __init__(self,Screen_height, Screen_width):
        self.screen_height = Screen_height
        self.screen_width = Screen_width
    def setupUi(self, MainWindow):
        width_scale = int(self.screen_width / 1920)
        height_scale = int(self.screen_height / 1030)
        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowIcon(QtGui.QIcon('running_files/images/vetruv_ico.ico'))
        MainWindow.resize(1095*width_scale, 805*height_scale)
        MainWindow.setMinimumSize(QtCore.QSize(1095*width_scale, 805*height_scale))
        MainWindow.setMaximumSize(QtCore.QSize(1095*width_scale, 805*height_scale))

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        font = QtGui.QFont()
        font.setFamily("Times New Roman")

        self.groupBox_display = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_display.setEnabled(True)
        self.groupBox_display.setGeometry(
            QtCore.QRect(10 * width_scale, 20 * height_scale, 811 * width_scale, 701 * height_scale))

        font.setPixelSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.groupBox_display.setFont(font)
        self.groupBox_display.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox_display.setFlat(False)
        self.groupBox_display.setObjectName("groupBox_display")

        self.label_display = QtWidgets.QLabel(self.groupBox_display)
        self.label_display.setGeometry(
            QtCore.QRect(20 * width_scale, 35 * height_scale, 770 * width_scale, 434 * height_scale))
        self.label_display.setText("")
        self.label_display.setStyleSheet('color: red')
        self.label_display.setAlignment(QtCore.Qt.AlignCenter)
        self.label_display.setObjectName("label_display")

        self.progressBar = QtWidgets.QProgressBar(self.groupBox_display)
        self.progressBar.setGeometry(
            QtCore.QRect(20 * width_scale, 485 * height_scale, 781 * width_scale, 20 * height_scale))
        font.setPixelSize(16)
        self.progressBar.setFont(font)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")

        self.widget_Plot = QtWidgets.QWidget(self.groupBox_display)
        self.graphWidget = pyqtgraph.PlotWidget(self.groupBox_display)
        self.graphWidget.getPlotItem().hideAxis('left')
        self.graphWidget.getPlotItem().hideAxis('bottom')
        self.graphWidget.setGeometry(
            QtCore.QRect(20 * width_scale, 520 * height_scale, 771 * width_scale, 181 * height_scale))
        self.graphWidget.setBackground("w")
        self.graphWidget.setObjectName("widget_Plot")

        self.groupBox_settings = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_settings.setGeometry(
            QtCore.QRect(830 * width_scale, 20 * height_scale, 251 * width_scale, 701 * height_scale))
        font.setPixelSize(20)
        self.groupBox_settings.setFont(font)
        self.groupBox_settings.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox_settings.setObjectName("groupBox_settings")

        self.lineEdit_number_seq = QtWidgets.QLineEdit(self.groupBox_settings)
        self.lineEdit_number_seq.setGeometry(
            QtCore.QRect(20 * width_scale, 190 * height_scale, 210 * width_scale, 25 * height_scale))
        self.lineEdit_number_seq.setObjectName("lineEdit_number_seq")

        self.pushButton_Load = QtWidgets.QPushButton(self.groupBox_settings)
        self.pushButton_Load.setGeometry(
            QtCore.QRect(20 * width_scale, 60 * height_scale, 210 * width_scale, 50 * height_scale))
        font.setPixelSize(20)
        self.pushButton_Load.setFont(font)
        self.pushButton_Load.setObjectName("pushButton_Load")

        self.pushButton_Dest_folder = QtWidgets.QPushButton(self.groupBox_settings)
        self.pushButton_Dest_folder.setGeometry(
            QtCore.QRect(20 * width_scale, 460 * height_scale, 210 * width_scale, 50 * height_scale))
        self.pushButton_Dest_folder.setFont(font)
        self.pushButton_Dest_folder.setObjectName("pushButton_Dest_folder")

        self.pushButton_Start = QtWidgets.QPushButton(self.groupBox_settings)
        self.pushButton_Start.setGeometry(
            QtCore.QRect(20 * width_scale, 340 * height_scale, 210 * width_scale, 50 * height_scale))
        self.pushButton_Start.setFont(font)
        self.pushButton_Start.setObjectName("pushButton_Start")

        self.pushButton_Stop = QtWidgets.QPushButton(self.groupBox_settings)
        self.pushButton_Stop.setFont(font)
        self.pushButton_Stop.setGeometry(
            QtCore.QRect(20 * width_scale, 400 * height_scale, 210 * width_scale, 50 * height_scale))
        self.pushButton_Stop.setObjectName("pushButton_Stop")

        self.label_number_seq = QtWidgets.QLabel(self.groupBox_settings)
        self.label_number_seq.setGeometry(
            QtCore.QRect(20 * width_scale, 165 * height_scale, 210 * width_scale, 20 * height_scale))
        font.setPixelSize(16)
        # font.setBold(False)
        # font.setWeight(50)
        self.label_number_seq.setFont(font)
        self.label_number_seq.setObjectName("label_number_seq")

        self.label_duration_seq = QtWidgets.QLabel(self.groupBox_settings)
        self.label_duration_seq.setGeometry(
            QtCore.QRect(20 * width_scale, 250 * height_scale, 210 * width_scale, 20 * height_scale))
        self.label_duration_seq.setFont(font)
        self.label_duration_seq.setObjectName("label_duration_seq")

        font.setPixelSize(14)
        self.label_duration_seq_error = QtWidgets.QLabel(self.groupBox_settings)
        self.label_duration_seq_error.setGeometry(
            QtCore.QRect(20 * width_scale, 300 * height_scale, 210 * width_scale, 20 * height_scale))
        self.label_duration_seq_error.setFont(font)
        self.label_duration_seq_error.setStyleSheet('color: red')
        self.label_duration_seq_error.setText("")
        self.label_duration_seq_error.setObjectName("label_duration_seq_error")

        self.label_number_seq_error = QtWidgets.QLabel(self.groupBox_settings)
        self.label_number_seq_error.setGeometry(
            QtCore.QRect(20 * width_scale, 215 * height_scale, 210 * width_scale, 20 * height_scale))
        self.label_number_seq_error.setFont(font)
        self.label_number_seq_error.setStyleSheet('color: red')
        self.label_number_seq_error.setText("")
        self.label_number_seq_error.setObjectName("label_number_seq_error")

        self.label_logo = QtWidgets.QLabel(self.groupBox_settings)
        self.label_logo.setGeometry(
            QtCore.QRect(40 * width_scale, 520 * height_scale, 170 * width_scale, 170 * height_scale))
        self.label_logo.setText("")
        self.label_logo.setPixmap(QtGui.QPixmap("running_files/images/vetruv_png.png"))
        self.label_logo.setScaledContents(True)
        self.label_logo.setObjectName("label_logo")

        self.lineEdit_seq_duration = QtWidgets.QLineEdit(self.groupBox_settings)
        self.lineEdit_seq_duration.setGeometry(
            QtCore.QRect(20 * width_scale, 275 * height_scale, 210 * width_scale, 25 * height_scale))
        self.lineEdit_seq_duration.setText("")
        self.lineEdit_seq_duration.setObjectName("lineEdit_seq_duration")

        self.label_video_name = QtWidgets.QLabel(self.groupBox_settings)
        self.label_video_name.setGeometry(
            QtCore.QRect(20 * width_scale, 115 * height_scale, 210 * width_scale, 20 * height_scale))
        self.label_video_name.setFont(font)
        self.label_video_name.setText("")
        self.label_video_name.setObjectName("label_video_name")

        self.label_video_duration = QtWidgets.QLabel(self.groupBox_settings)
        self.label_video_duration.setGeometry(
            QtCore.QRect(20 * width_scale, 135 * height_scale, 210 * width_scale, 20 * height_scale))
        self.label_video_duration.setFont(font)
        self.label_video_duration.setText("")
        self.label_video_duration.setObjectName("label_video_duration")

        self.label_univ = QtWidgets.QLabel(self.centralwidget)
        self.label_univ.setGeometry(
            QtCore.QRect(30 * width_scale, 730 * height_scale, 131 * width_scale, 61 * height_scale))
        self.label_univ.setText("")
        self.label_univ.setPixmap(QtGui.QPixmap("running_files/images/UJM.png"))
        self.label_univ.setScaledContents(True)
        self.label_univ.setObjectName("label_univ")

        self.label_chu = QtWidgets.QLabel(self.centralwidget)
        self.label_chu.setGeometry(
            QtCore.QRect(300 * width_scale, 730 * height_scale, 144 * width_scale, 61 * height_scale))
        self.label_chu.setText("")
        self.label_chu.setPixmap(QtGui.QPixmap("running_files/images/chu.png"))
        self.label_chu.setScaledContents(True)
        self.label_chu.setObjectName("label_chu")

        self.label_sainbiose = QtWidgets.QLabel(self.centralwidget)
        self.label_sainbiose.setGeometry(
            QtCore.QRect(600 * width_scale, 730 * height_scale, 143 * width_scale, 61 * height_scale))
        self.label_sainbiose.setText("")
        self.label_sainbiose.setPixmap(QtGui.QPixmap("running_files/images/sainbiose.png"))
        self.label_sainbiose.setScaledContents(True)
        self.label_sainbiose.setObjectName("label_sainbiose")

        self.label_hubertcurien = QtWidgets.QLabel(self.centralwidget)
        self.label_hubertcurien.setGeometry(
            QtCore.QRect(870 * width_scale, 730 * height_scale, 186 * width_scale, 51 * height_scale))
        self.label_hubertcurien.setText("")
        self.label_hubertcurien.setPixmap(QtGui.QPixmap("running_files/images/HubertCurien.png"))
        self.label_hubertcurien.setScaledContents(True)
        self.label_hubertcurien.setObjectName("label_hubertcurien")

        self.pushButton_french = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_french.setObjectName("pushButton_french")
        self.pushButton_french.setGeometry(QtCore.QRect(1050*width_scale, 5*height_scale, 30*width_scale, 20*height_scale))
        icon = QtGui.QIcon()
        icon.addFile("running_files/images/french.png", QtCore.QSize(), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_french.setIcon(icon)
        self.pushButton_french.setIconSize(QtCore.QSize(40*height_scale, 30*width_scale))
        self.pushButton_english = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_english.setObjectName("pushButton_english")
        self.pushButton_english.setGeometry(QtCore.QRect(1015*width_scale, 5*height_scale, 30*width_scale, 20*height_scale))
        icon1 = QtGui.QIcon()
        icon1.addFile("running_files/images/english.png", QtCore.QSize(), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_english.setIcon(icon1)
        self.pushButton_english.setIconSize(QtCore.QSize(40*height_scale, 50*width_scale
                                                  ))
        MainWindow.setCentralWidget(self.centralwidget)


        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "AGMA Sequence Selector"))


