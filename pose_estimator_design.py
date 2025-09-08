
from PyQt5 import QtCore, QtGui, QtWidgets

class Pose_design_window(object):
    """Pose estimator GUI design:"""

    def __init__(self, screen_height=None, screen_width=None):
        # Get screen dimensions if not provided
        if screen_height is None or screen_width is None:
            screen = QtWidgets.QApplication.primaryScreen()
            screen_geometry = screen.geometry()
            self.screen_height = screen_geometry.height()
            self.screen_width = screen_geometry.width()
        else:
            self.screen_height = screen_height
            self.screen_width = screen_width

    def setupUi(self, MainWindow):
        # Calculate responsive window size (about 60% of screen width, 62% of height)
        window_width = max(1000, int(self.screen_width * 0.6))
        window_height = max(660, int(self.screen_height * 0.70))

        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowIcon(QtGui.QIcon('running_files/images/vetruv_ico.ico'))
        MainWindow.resize(window_width, window_height)
        MainWindow.setMinimumSize(QtCore.QSize(1000, 660))

        # Create central widget
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # Create main layout
        main_layout = QtWidgets.QVBoxLayout(self.centralwidget)
        main_layout.setContentsMargins(10, 5, 10, 10)
        main_layout.setSpacing(10)

        # Language selection layout (top right)
        self._setup_language_buttons(main_layout)

        # Main content layout (horizontal split)
        content_layout = QtWidgets.QHBoxLayout()
        content_layout.setSpacing(10)

        # Display area (left side - takes most space)
        self._setup_display_area(content_layout)

        # Settings panel (right side - fixed width)
        self._setup_settings_panel(content_layout)

        main_layout.addLayout(content_layout, 1)  # Give most space to content

        # Logo footer
        self._setup_logo_footer(main_layout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def _setup_language_buttons(self, main_layout):
        """Setup language selection buttons at the top right"""
        language_layout = QtWidgets.QHBoxLayout()
        language_layout.addStretch()  # Push buttons to the right

        # English button
        self.pushButton_english = QtWidgets.QPushButton()
        self.pushButton_english.setFixedSize(30, 20)
        self.pushButton_english.setObjectName("pushButton_english")
        icon1 = QtGui.QIcon()
        icon1.addFile("running_files/images/english.png", QtCore.QSize(), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_english.setIcon(icon1)
        self.pushButton_english.setIconSize(QtCore.QSize(25, 18))

        # French button
        self.pushButton_french = QtWidgets.QPushButton()
        self.pushButton_french.setFixedSize(30, 20)
        self.pushButton_french.setObjectName("pushButton_french")
        icon = QtGui.QIcon()
        icon.addFile("running_files/images/french.png", QtCore.QSize(), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_french.setIcon(icon)
        self.pushButton_french.setIconSize(QtCore.QSize(25, 18))

        language_layout.addWidget(self.pushButton_english)
        language_layout.addWidget(self.pushButton_french)

        main_layout.addLayout(language_layout)

    def _setup_display_area(self, content_layout):
        """Setup the main display area with video/image display and progress bar"""
        # Display group box
        self.groupBox_display = QtWidgets.QGroupBox()
        self.groupBox_display.setEnabled(True)

        # Set font for group box
        font = QtGui.QFont("Tahoma", 14, QtGui.QFont.Bold)
        self.groupBox_display.setFont(font)
        self.groupBox_display.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox_display.setObjectName("groupBox_display")

        # Display group layout
        display_layout = QtWidgets.QVBoxLayout(self.groupBox_display)
        display_layout.setContentsMargins(15, 20, 15, 15)
        display_layout.setSpacing(10)

        # Main display label for video/image
        self.label_display = QtWidgets.QLabel()
        self.label_display.setText("")
        self.label_display.setStyleSheet('color: red; border: 1px solid #ccc;')
        self.label_display.setAlignment(QtCore.Qt.AlignCenter)
        self.label_display.setMinimumSize(700, 400)
        self.label_display.setObjectName("label_display")

        # Progress bar
        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setMinimumHeight(25)
        progress_font = QtGui.QFont("Tahoma", 12, QtGui.QFont.Bold)
        self.progressBar.setFont(progress_font)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")

        # Add to display layout
        display_layout.addWidget(self.label_display, 1)  # Takes most space
        display_layout.addWidget(self.progressBar)

        # Add display area to content (takes 75% of horizontal space)
        content_layout.addWidget(self.groupBox_display, 3)

    def _setup_settings_panel(self, content_layout):
        """Setup the settings panel on the right side"""
        # Settings group box
        self.groupBox_settings = QtWidgets.QGroupBox()
        self.groupBox_settings.setMaximumWidth(280)
        self.groupBox_settings.setMinimumWidth(250)

        font = QtGui.QFont("Tahoma", 14, QtGui.QFont.Bold)
        self.groupBox_settings.setFont(font)
        self.groupBox_settings.setAlignment(QtCore.Qt.AlignCenter)
        self.groupBox_settings.setObjectName("groupBox_settings")

        # Settings layout
        settings_layout = QtWidgets.QVBoxLayout(self.groupBox_settings)
        settings_layout.setContentsMargins(15, 20, 15, 15)
        settings_layout.setSpacing(15)

        # Load button
        self.pushButton_Load = QtWidgets.QPushButton()
        self.pushButton_Load.setMinimumHeight(40)
        button_font = QtGui.QFont("Tahoma", 10, QtGui.QFont.Bold)
        self.pushButton_Load.setFont(button_font)
        self.pushButton_Load.adjustSize()
        self.pushButton_Load.setObjectName("pushButton_Load")
        settings_layout.addWidget(self.pushButton_Load)

        # Video information labels
        self.label_video_number = QtWidgets.QLabel()
        label_font = QtGui.QFont("Tahoma", 10)
        self.label_video_number.setFont(label_font)
        self.label_video_number.setText("")
        self.label_video_number.setObjectName("label_video_name")
        settings_layout.addWidget(self.label_video_number)

        # FPS input section
        fps_layout = QtWidgets.QHBoxLayout()

        self.label_number_fps = QtWidgets.QLabel()
        fps_label_font = QtGui.QFont("Tahoma", 12, QtGui.QFont.Bold)
        self.label_number_fps.setFont(fps_label_font)
        self.label_number_fps.setObjectName("label_number_seq")

        # Help button for FPS
        self.pushButton_help = QtWidgets.QPushButton()
        self.pushButton_help.setFixedSize(20, 20)
        self.pushButton_help.setObjectName("help")
        self.pushButton_help.setStyleSheet("border: none;")
        icon = QtGui.QIcon()
        icon.addFile("running_files/images/help.png", QtCore.QSize(), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton_help.setIcon(icon)
        self.pushButton_help.setIconSize(QtCore.QSize(16, 16))

        fps_layout.addWidget(self.label_number_fps)
        fps_layout.addWidget(self.pushButton_help)
        fps_layout.addStretch()

        settings_layout.addLayout(fps_layout)

        # FPS input field
        self.lineEdit_number_fps = QtWidgets.QLineEdit()
        self.lineEdit_number_fps.setMinimumHeight(25)
        self.lineEdit_number_fps.setObjectName("lineEdit_number_fps")
        settings_layout.addWidget(self.lineEdit_number_fps)

        # Error label for FPS
        self.label_number_fps_error = QtWidgets.QLabel()
        self.label_number_fps_error.setFont(label_font)
        self.label_number_fps_error.setStyleSheet('color: red')
        self.label_number_fps_error.setText("")
        self.label_number_fps_error.setObjectName("label_number_fps_error")
        settings_layout.addWidget(self.label_number_fps_error)

        # Save option radio button
        self.radioButton_save = QtWidgets.QRadioButton()
        radio_font = QtGui.QFont("Tahoma", 11)
        self.radioButton_save.setFont(radio_font)
        self.radioButton_save.setText("Save processed images")
        self.radioButton_save.setObjectName("radioButton_save")
        settings_layout.addWidget(self.radioButton_save)

        # Control buttons
        self.pushButton_Start = QtWidgets.QPushButton()
        self.pushButton_Start.setMinimumHeight(40)
        self.pushButton_Start.setFont(button_font)
        self.pushButton_Start.setObjectName("pushButton_Start")
        settings_layout.addWidget(self.pushButton_Start)

        self.pushButton_Stop = QtWidgets.QPushButton()
        self.pushButton_Stop.setMinimumHeight(40)
        self.pushButton_Stop.setFont(button_font)
        self.pushButton_Stop.setObjectName("pushButton_Stop")
        settings_layout.addWidget(self.pushButton_Stop)

        self.pushButton_Dest_folder = QtWidgets.QPushButton()
        self.pushButton_Dest_folder.setMinimumHeight(40)
        self.pushButton_Dest_folder.setFont(button_font)
        self.pushButton_Dest_folder.setObjectName("pushButton_Dest_folder")
        settings_layout.addWidget(self.pushButton_Dest_folder)

        # Logo in settings panel
        settings_layout.addStretch()  # Push logo to bottom

        self.label_logo = QtWidgets.QLabel()
        self.label_logo.setText("")
        self.label_logo.setFixedSize(150, 150)
        pixmap = QtGui.QPixmap("running_files/images/vetruv_png.png")
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(150, 150, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            self.label_logo.setPixmap(scaled_pixmap)
        self.label_logo.setAlignment(QtCore.Qt.AlignCenter)
        self.label_logo.setObjectName("label_logo")
        settings_layout.addWidget(self.label_logo, 0, QtCore.Qt.AlignCenter)

        # Add settings panel to content (takes 25% of horizontal space)
        content_layout.addWidget(self.groupBox_settings, 1)

    def _setup_logo_footer(self, main_layout):
        """Setup the footer with organization logos"""
        footer_layout = QtWidgets.QHBoxLayout()
        footer_layout.setSpacing(20)
        footer_layout.setContentsMargins(20, 5, 20, 5)

        # University logo
        self.label_univ = QtWidgets.QLabel()
        self.label_univ.setFixedSize(100, 50)
        self.label_univ.setText("")
        pixmap_univ = QtGui.QPixmap("running_files/images/UJM.png")
        if not pixmap_univ.isNull():
            scaled_pixmap = pixmap_univ.scaled(100, 50, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            self.label_univ.setPixmap(scaled_pixmap)
        self.label_univ.setObjectName("label_univ")

        # CHU logo
        self.label_chu = QtWidgets.QLabel()
        self.label_chu.setFixedSize(110, 50)
        self.label_chu.setText("")
        pixmap_chu = QtGui.QPixmap("running_files/images/chu.png")
        if not pixmap_chu.isNull():
            scaled_pixmap = pixmap_chu.scaled(110, 50, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            self.label_chu.setPixmap(scaled_pixmap)
        self.label_chu.setObjectName("label_chu")

        # Sainbiose logo
        self.label_sainbiose = QtWidgets.QLabel()
        self.label_sainbiose.setFixedSize(110, 50)
        self.label_sainbiose.setText("")
        pixmap_sainbiose = QtGui.QPixmap("running_files/images/sainbiose.png")
        if not pixmap_sainbiose.isNull():
            scaled_pixmap = pixmap_sainbiose.scaled(110, 50, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            self.label_sainbiose.setPixmap(scaled_pixmap)
        self.label_sainbiose.setObjectName("label_sainbiose")

        # Hubert Curien logo
        self.label_hubertcurien = QtWidgets.QLabel()
        self.label_hubertcurien.setFixedSize(140, 50)
        self.label_hubertcurien.setText("")
        pixmap_hc = QtGui.QPixmap("running_files/images/HubertCurien.png")
        if not pixmap_hc.isNull():
            scaled_pixmap = pixmap_hc.scaled(140, 50, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            self.label_hubertcurien.setPixmap(scaled_pixmap)
        self.label_hubertcurien.setObjectName("label_hubertcurien")

        # Add logos to footer with proper spacing
        footer_layout.addWidget(self.label_univ)
        footer_layout.addStretch()
        footer_layout.addWidget(self.label_chu)
        footer_layout.addStretch()
        footer_layout.addWidget(self.label_sainbiose)
        footer_layout.addStretch()
        footer_layout.addWidget(self.label_hubertcurien)

        main_layout.addLayout(footer_layout)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "AGMA Pose Estimator"))


