
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from torchvision.models.detection import FasterRCNN
from torchvision.models.detection.backbone_utils import resnet_fpn_backbone

import os
import torch.nn.parallel
import torch.backends.cudnn as cudnn
import torch.optim
import torch.utils.data
import torch.utils.data.distributed
import sys

import lib.models.pose_hrnet as net
from lib.config import update_config


from sequence_selector_design import *
from pose_estimator_design import *
from loading_window_design import *
from image import *

from PyQt5.QtCore import QTranslator
from PyQt5.QtWidgets import QMainWindow,QApplication,QFileDialog
from PyQt5.QtGui import QImage,QPixmap
import pandas as pd
from subprocess import run as RUN

from PyQt5.QtCore import Qt
from PyQt5.QtCore import QThread, pyqtSignal, QTimer


class ModelLoader(QThread):
    """Background thread for loading heavy ML models, this class was added in the second version of AGMA-PESS after feedback from users"""
    # Signals to communicate with main thread
    progress_updated = pyqtSignal(int, str)  # progress percentage, status message
    models_loaded = pyqtSignal(object, object, object)  # CTX, box_model, pose_model
    error_occurred = pyqtSignal(str)  # error message

    def run(self):
        """Execute model loading in background thread"""
        try:
            #Device setup
            self.progress_updated.emit(10, "Setting up device...")
            CTX = self.get_device_with_arch_check()

            cudnn.benchmark = cfg.CUDNN.BENCHMARK
            torch.backends.cudnn.deterministic = cfg.CUDNN.DETERMINISTIC
            torch.backends.cudnn.enabled = cfg.CUDNN.ENABLED

            #Parse arguments and update config
            self.progress_updated.emit(20, "Loading configuration...")
            args = parse_args()
            update_config(cfg, args)

            #Load object detection model
            self.progress_updated.emit(40, "Loading object detection model...")
            backbone = resnet_fpn_backbone('resnet50', pretrained=False)
            box_model = FasterRCNN(backbone, num_classes=91)
            state_dict = torch.load("models/fasterrcnn_resnet50_fpn_coco-258fb6c6.pth")
            box_model.load_state_dict(state_dict)
            box_model.to(CTX)
            box_model.eval()

            #Load pose estimation model
            self.progress_updated.emit(70, "Loading pose estimation model...")
            pose_model = net.get_pose_net(cfg, is_train=False)
            model_file = cfg.TEST.MODEL_FILE
            if CTX.type == 'cuda':
                pose_model.load_state_dict(torch.load(model_file), strict=False)
                pose_model = torch.nn.DataParallel(pose_model, device_ids=cfg.GPUS)
            else:
                pose_model.load_state_dict(torch.load(model_file, map_location=torch.device('cpu')))


            pose_model.to(CTX)
            pose_model.eval()

            self.progress_updated.emit(100, "Models loaded successfully!")
            self.models_loaded.emit(CTX, box_model, pose_model)

        except Exception as e:
            self.error_occurred.emit(f"Error loading models: {str(e)}")

    def get_device_with_arch_check(self):
        if not torch.cuda.is_available():
            return torch.device('cpu')
        try:
            #get the compute capability of GPU
            major, minor = torch.cuda.get_device_capability(0)
            gpu_arch = f"sm_{major}{minor}"

            #get supported architectures
            if hasattr(torch.cuda, 'get_arch_list'):
                supported_archs = torch.cuda.get_arch_list()
                if gpu_arch not in supported_archs and f"compute_{major}{minor}" not in supported_archs:
                    return torch.device('cpu')
            return torch.device('cuda')

        except Exception as e:
            return torch.device('cpu')


class First_window(QMainWindow):
    def __init__(self, Screen_height, Screen_width):
        super().__init__()
        self.counter = 0
        self.closed_manually = True
        self.ui = Ui_loading_window(Screen_height, Screen_width)

        # Initialize model loader thread
        self.model_loader = ModelLoader()
        self.setup_ui()
        self.show()
        self.setup_connections()
        self.retranslateUi()
        self.setup_model_loading()
        # Start loading models asynchronously
        self.start_model_loading()

    def setup_ui(self):
        """Configure and set up UI elements"""
        self.ui.setupUi(self)
        self.ui.groupBox.setTitle(self.tr("AGMA Pose Estimator && Sequence Selector"))
        self.ui.pushButton_start.setText(self.tr("Start"))
        self.ui.radioButton_pose_estimator.setText(self.tr("Pose Estimator"))
        self.ui.radioButton_sequence_selector.setText(self.tr("Sequence Selector"))

        # Hide program selection until models are loaded
        self.ui.radioButton_pose_estimator.hide()
        self.ui.radioButton_sequence_selector.hide()
        self.ui.pushButton_start.hide()

        # Update progress
        self.ui.progressBar.setValue(0)
        self.ui.progressBar.show()

    def setup_model_loading(self):
        """Connect model loader signals to UI update methods"""
        self.model_loader.progress_updated.connect(self.update_loading_progress)
        self.model_loader.models_loaded.connect(self.on_models_loaded)
        self.model_loader.error_occurred.connect(self.on_loading_error)

    def start_model_loading(self):
        """Start the model loading process in background thread"""
        self.ui.label_loading_language.setText("Loading models...")
        self.model_loader.start()

    def update_loading_progress(self, progress, message):
        """Update UI with loading progress"""
        self.ui.progressBar.setValue(progress)
        self.ui.label_loading_language.setText(message)
        # Process events to keep UI responsive
        QApplication.processEvents()

    def on_models_loaded(self, device_ctx, loaded_box_model, loaded_pose_model):
        """Called when models are successfully loaded"""
        global CTX, box_model, pose_model
        CTX = device_ctx
        box_model = loaded_box_model
        pose_model = loaded_pose_model
        # Show UI elements for program selection
        self.show_ui_elements()

    def on_loading_error(self, error_message):
        """Handle model loading errors"""
        self.ui.label_loading_language.setStyleSheet('color: red')
        QtWidgets.QMessageBox.critical(self, "Loading Error", error_message)

    def show_ui_elements(self):
        """Show program selection UI after models are loaded"""
        self.ui.label_loading_language.setText(self.tr("Choose a program:"))
        self.ui.label_loading_language.setStyleSheet('')  # Reset error styling
        self.ui.radioButton_pose_estimator.show()
        self.ui.radioButton_sequence_selector.show()
        self.ui.pushButton_start.show()
        self.ui.pushButton_english.setEnabled(False)

        # Hide progress bar if it exists
        if hasattr(self.ui, 'progressBar'):
            self.ui.progressBar.hide()

    def setup_connections(self):
        """Establish connections between buttons and their respective functions"""
        self.ui.pushButton_start.clicked.connect(self.start)
        self.ui.pushButton_french.clicked.connect(self.lang_fr)
        self.ui.pushButton_english.clicked.connect(self.lang_en)

    def retranslateUi(self):
        """Set text for UI elements to reflect the current language"""
        self.ui.groupBox.setTitle(self.tr("AGMA Pose Estimator && Sequence Selector"))
        self.ui.pushButton_start.setText(self.tr("Start"))
        self.ui.radioButton_pose_estimator.setText(self.tr("Pose Estimator"))
        self.ui.radioButton_sequence_selector.setText(self.tr("Sequence Selector"))
        if (hasattr(self.ui, 'label_loading_language') and
                hasattr(self, 'model_loader') and
                not self.model_loader.isRunning()):
            self.ui.label_loading_language.setText(self.tr("Choose a program:"))

    def lang_fr(self):
        """Switch the application language to French"""
        global language
        language = "fr"
        translator.load("running_files/translations/translati.qm")
        app.installTranslator(translator)
        self.ui.pushButton_english.setEnabled(True)
        self.ui.pushButton_french.setEnabled(False)
        self.retranslateUi()

    def lang_en(self):
        """Switch the application language to English"""
        global language
        language = "en"
        app.removeTranslator(translator)
        self.ui.pushButton_english.setEnabled(False)
        self.ui.pushButton_french.setEnabled(True)
        self.retranslateUi()

    def start(self):
        """Determine the selected program and store it"""
        global program
        if self.ui.radioButton_pose_estimator.isChecked():
            program = 'pose_estimator'
            self.closed_manually = False
        elif self.ui.radioButton_sequence_selector.isChecked():
            program = 'sequence_selector'
            self.closed_manually = False
        else:
            self.ui.label_loading_language.setStyleSheet('color: red')
            return
        self.close()

    def closeEvent(self, event):
        """Ensure background thread is properly terminated"""
        if self.model_loader.isRunning():
            self.model_loader.quit()
            self.model_loader.wait()
        super().closeEvent(event)


class Sequence_selector(QMainWindow):
    def __init__(self,Screen_height, Screen_width):
        super().__init__()
        self.counter = 0
        self.ui = Ui_MainWindow(Screen_height, Screen_width)
        self.ui.setupUi(self)

        self.initialize_ui()
        self.connect_signals()
        self.initialize_flags()

    def initialize_ui(self):
        """set lebels text"""
        self.ui.groupBox_display.setTitle(self.tr("Display"))
        self.ui.groupBox_settings.setTitle(self.tr("Settings"))
        self.ui.lineEdit_number_seq.setText("")
        self.ui.pushButton_Load.setText(self.tr("Load Video"))
        self.ui.label_number_seq.setText(self.tr("Number of sequences:"))
        self.ui.label_duration_seq.setText(self.tr("Sequences duration (minutes):"))
        self.ui.pushButton_Dest_folder.setText(self.tr("Destination Folder"))
        self.ui.pushButton_Start.setText(self.tr("Start"))
        self.ui.pushButton_Stop.setText(self.tr("Stop"))
        self.ui.lineEdit_seq_duration.setText("")

    def connect_signals(self):
        """set pushbutton events"""
        self.ui.pushButton_Load.clicked.connect(self.open)
        self.ui.pushButton_Start.clicked.connect(self.run)
        self.ui.pushButton_Stop.clicked.connect(self.stop)
        self.ui.pushButton_Dest_folder.clicked.connect(self.dest)
        self.ui.pushButton_french.clicked.connect(self.lang_fr)
        self.ui.pushButton_english.clicked.connect(self.lang_en)

        self.ui.pushButton_Load.blockSignals(False)
        self.ui.pushButton_Start.blockSignals(False)
        self.ui.pushButton_Dest_folder.setEnabled(False)

        if language == "en":
            self.ui.pushButton_english.setEnabled(False)
        if language == "fr":
            self.ui.pushButton_french.setEnabled(False)

    def initialize_flags(self):
        self.v_flage = False  # video presence flag
        self.s_flage = False  # sequences number flag
        self.d_flage = False  # duration flag
        self.stop_flag = False
        self.end_flag = False  # video is processed flag


    def retranslateUi(self):
        self.ui.groupBox_display.setTitle(self.tr("Display"))
        self.ui.groupBox_settings.setTitle(self.tr("Settings"))
        self.ui.pushButton_Load.setText(self.tr("Load Video"))
        self.ui.label_number_seq.setText(self.tr("Number of sequences:"))
        self.ui.label_duration_seq.setText(self.tr("Sequences duration (minutes):"))
        self.ui.pushButton_Dest_folder.setText(self.tr("Destination Folder"))
        self.ui.pushButton_Start.setText(self.tr("Start"))
        self.ui.pushButton_Stop.setText(self.tr("Stop"))

    def lang_fr(self):
        global language
        language = "fr"
        translator.load("running_files/translations/translati.qm")
        app.installTranslator(translator)
        self.ui.pushButton_english.setEnabled(True)
        self.ui.pushButton_french.setEnabled(False)
        self.retranslateUi()

    def lang_en(self):
        global language
        language = "en"
        app.removeTranslator(translator)
        self.ui.pushButton_english.setEnabled(False)
        self.ui.pushButton_french.setEnabled(True)
        self.retranslateUi()

    def stop(self):
        self.stop_flag=True
        self.ui.pushButton_Load.blockSignals(False)
        self.ui.pushButton_Start.blockSignals(False)

    def open(self):
        """Open a video file."""
        self.video_path = QFileDialog.getOpenFileName(self, self.tr('Select your video'), '.',
                                                      "Video files (*.webm *.mkv *.vob *.avi *.MTS *.mov *.wmv *.mp4 *.mpg *.mpeg *.3gp *.flv)")[
            0]

        if self.video_path:
            self.initialize_video()

    def initialize_video(self):
        """Initialize video settings and display the first frame."""
        self.video = cv2.VideoCapture(self.video_path)
        self.video_length = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
        self.video_fps = int(self.video.get(cv2.CAP_PROP_FPS))
        ret, frame = self.video.read()
        self.ui.label_video_name.setText(self.tr('Selected video: ') + os.path.basename(self.video_path))
        self.ui.label_video_duration.setText(
            self.tr("Duration: ") + str(int(self.video_length / (self.video_fps * 60))) + " minutes")
        self.display_frame(frame)
        self.ui.progressBar.setValue(0)
        self.ui.progressBar.setMaximum(self.video_length)
        self.ui.graphWidget.clear()
        self.v_flage = True
        self.stop_flag = False
        self.ui.pushButton_Dest_folder.setEnabled(False)

    def dest(self):
        """Open the destination folder."""
        os.startfile(self.video_path[:-4] + "_Sequences")

    def display_frame(self, frame):
        """Display a video frame in the QLabel."""
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_qimage = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_RGB888)
        pix = QPixmap.fromImage(frame_qimage)
        self.ui.label_display.setAlignment(Qt.AlignCenter)
        self.ui.label_display.setPixmap(
            pix.scaled(self.ui.label_display.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def run(self):
        """Run the video processing."""
        self.ui.graphWidget.clear()
        if not self.v_flage:
            self.ui.label_display.setText(self.tr("Please choose a video to analyze!"))
            return

        if not self.validate_inputs():
            return

        self.ui.label_duration_seq_error.setText("")
        self.ui.pushButton_Load.blockSignals(True)
        self.ui.pushButton_Start.blockSignals(True)

        movs = self.process_video()
        if not movs:
            return

        starts = self.calculate_sequence_starts(self.duration, self.number_sequences, movs)

        self.cut_video(starts)

        self.ui.pushButton_Load.blockSignals(False)
        self.ui.pushButton_Start.blockSignals(False)
        self.ui.pushButton_Dest_folder.setEnabled(True)

    def validate_inputs(self):
        """Validate the user inputs for number of sequences and duration."""
        try:
            self.number_sequences = int(self.ui.lineEdit_number_seq.text())
            if self.number_sequences==0:
                self.ui.label_number_seq_error.setText(self.tr("Please choose a valid number!"))
                self.s_flage = False
            else:
                self.s_flage = True
                self.ui.label_number_seq_error.setText("")
        except ValueError:
            self.ui.label_number_seq_error.setText(self.tr("Please choose a valid number!"))
            self.s_flage = False

        if self.s_flage:
            try:
                duration_text = self.ui.lineEdit_seq_duration.text()
                self.duration = float(duration_text.replace(',', '.'))
                self.duration = int(self.duration * 60)
                self.d_flage = True
            except ValueError:
                self.ui.label_duration_seq_error.setText(self.tr("Please choose a valid duration!"))

            if self.d_flage:
                if self.duration == 0 or (self.number_sequences * self.duration * self.video_fps) > self.video_length:
                    self.ui.label_duration_seq_error.setText(self.tr("Please choose a valid duration!"))
                    return False

        return self.s_flage and self.d_flage

    def process_video(self):
        """Process the video to detect movements and plot the graph."""
        pr = 0
        prev_pred = 0
        movs = [0]
        self.video = cv2.VideoCapture(self.video_path)
        self.video_resolution = (
        int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        counter = 0

        while counter * self.video_fps <= self.video_length:
            frame_nbr = counter * self.video_fps
            self.video.set(cv2.CAP_PROP_POS_FRAMES, frame_nbr)
            ret, frame = self.video.read()
            if ret:
                self.ui.progressBar.setValue(frame_nbr)
                img_tensor = self.prepare_frame_for_model(frame)
                pred_boxes = get_person_detection_boxes(box_model, [img_tensor], threshold=0.9)
                pr, movs, prev_pred = self.update_movements(frame, pred_boxes, pr, movs, prev_pred)
                self.update_graph(movs)
                self.display_frame(frame)
            counter += 1
            QApplication.processEvents()
            if self.stop_flag:
                return None
        return movs

    def prepare_frame_for_model(self, frame):
        """Convert frame to tensor for model prediction."""
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_tensor = torch.from_numpy(img / 255.).permute(2, 0, 1).float().to(CTX)
        return img_tensor

    def update_movements(self, frame, pred_boxes, pr, movs, prev_pred):
        """Update movement list based on pose estimation predictions."""
        if len(pred_boxes) == 1:
            pr += 1
            for box in pred_boxes:
                center, scale = box_to_center_scale(box, cfg.MODEL.IMAGE_SIZE[0], cfg.MODEL.IMAGE_SIZE[1])
                image_pose = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).copy()
                pose_preds, _ = get_pose_estimation_prediction(pose_model, image_pose, center, scale)
                if len(pose_preds) == 1:
                    if pr > 1:
                        movs.append(sum(np.sqrt([sum(l) for l in np.square(np.subtract(pose_preds[0], prev_pred[0]))])))
                    prev_pred = pose_preds
        else:
            movs.append(0)
        return pr, movs, prev_pred

    def update_graph(self, movs):
        """Update the movement graph with new data."""
        self.ui.graphWidget.plot([self.video_fps * i for i in range(len(movs))], movs)

    def calculate_sequence_starts(self, duration, sequences_nbr, signal):
        """Calculate the start frames for each sequence based on the movement signal."""
        corr_array = [(a, sum(signal[a:(a + duration)])) for a in range(len(signal) - duration)]
        corr_array_sorted = sorted(corr_array, key=lambda x: x[1], reverse=True)
        sequences_start = []

        for i, (start, _) in enumerate(corr_array_sorted):
            if not sequences_start or all(abs(start - s) > duration for s in sequences_start):
                sequences_start.append(start)
                if len(sequences_start) == sequences_nbr:
                    break

        if len(sequences_start) < self.number_sequences:
            self.ui.label_number_seq_error.setText(
                self.tr("Only ") + str(len(sequences_start)) + self.tr(" sequences were found"))

        return sequences_start

    def cut_video(self, starts):
        """Cut the video into sequences and save them."""
        path = self.video_path[:-4] + "_Sequences"
        if not os.path.exists(path):
            os.makedirs(path)

        for cntr, start in enumerate(starts, 1):
            self.save_sequence(path, cntr, start)

        self.ui.progressBar.setValue(self.video_length)
        self.ui.pushButton_Dest_folder.setEnabled(True)

    def save_sequence(self, path, cntr, start):

        ffmpeg_path = os.path.join(os.path.dirname(__file__),"lib", "ffmpeg", "bin", "ffmpeg.exe")

        command = [
            ffmpeg_path,
            "-i", self.video_path,  # Input video file
            "-ss", self.seconds_to_ffmpeg_time(start),  # Start time (in seconds)
            "-t", str(self.duration),  # Duration of the sequence
            "-c", "copy",  # Copy codec to avoid re-encoding
            os.path.join(path, f'sequence_{cntr}.mp4')  # Output file path
        ]

        RUN(command, check=True)

    def seconds_to_ffmpeg_time(self,seconds):
        """Convert time in seconds to FFmpeg's timestamp format (HH:MM:SS.mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60  # Remaining seconds, including fractions
        return f"{hours:02}:{minutes:02}:{secs:06.3f}"  # Format as HH:MM:SS.mmm


class Pose_estimator(QMainWindow):
    def __init__(self,Screen_height, Screen_width):
        super().__init__()
        self.counter = 0
        self.ui = Pose_design_window(Screen_height, Screen_width)
        self.ui.setupUi(self)

        self.initialize_ui()
        self.connect_signals()
        self.initialize_flags()

    def initialize_ui(self):
        """set lebels text"""
        self.ui.groupBox_display.setTitle(self.tr("Display"))
        self.ui.groupBox_settings.setTitle(self.tr("Settings"))
        self.ui.lineEdit_number_fps.setText("")
        self.ui.pushButton_Load.setText(self.tr("Load Video"))
        self.ui.label_number_fps.setText(self.tr("Number of FPS:"))
        self.ui.pushButton_Dest_folder.setText(self.tr("Destination Folder"))
        self.ui.pushButton_Start.setText(self.tr("Start"))
        self.ui.pushButton_Stop.setText(self.tr("Stop"))
        self.ui.radioButton_save.setText(self.tr("Save processed images"))

    def connect_signals(self):
        """Establish connections between buttons and their respective functions"""
        self.ui.pushButton_Load.clicked.connect(self.open)
        self.ui.pushButton_Start.clicked.connect(self.run)
        self.ui.pushButton_Stop.clicked.connect(self.stop)
        self.ui.pushButton_Dest_folder.clicked.connect(self.dest)
        self.ui.pushButton_english.clicked.connect(self.lang_en)
        self.ui.pushButton_french.clicked.connect(self.lang_fr)
        self.ui.pushButton_help.clicked.connect(self.help_click)

        self.ui.pushButton_Load.blockSignals(False)
        self.ui.pushButton_Start.blockSignals(False)
        self.ui.pushButton_Dest_folder.setEnabled(False)
        if language == "en":
            self.ui.pushButton_english.setEnabled(False)
        if language == "fr":
            self.ui.pushButton_french.setEnabled(False)

    def initialize_flags(self):
        """Initialize flags used to track video processing state."""
        self.v_flag = False  # video presence flag
        self.fps_flag = False  # sequences number flag
        self.stop_flag = False
        self.end_flag = False  # video is processed flag

    def retranslateUi(self):
        """Update UI text based on the current language setting."""
        self.ui.groupBox_display.setTitle(self.tr("Display"))
        self.ui.groupBox_settings.setTitle(self.tr("Settings"))
        self.ui.pushButton_Load.setText(self.tr("Load Video"))
        self.ui.label_number_fps.setText(self.tr("Number of FPS:"))
        self.ui.pushButton_Dest_folder.setText(
            self.tr("Destination Folder"))
        self.ui.pushButton_Start.setText(self.tr("Start"))
        self.ui.pushButton_Stop.setText(self.tr("Stop"))
        self.ui.radioButton_save.setText(self.tr("Save processed images"))

    def lang_fr(self):
        """Switch the application's language to French."""
        global language
        language = "fr"
        translator.load("running_files/translations/translati.qm")
        app.installTranslator(translator)
        self.ui.pushButton_english.setEnabled(True)
        self.ui.pushButton_french.setEnabled(False)
        self.retranslateUi()

    def lang_en(self):
        """Switch the application's language to English """
        global language
        language = "en"
        app.removeTranslator(translator)
        self.ui.pushButton_english.setEnabled(False)
        self.ui.pushButton_french.setEnabled(True)
        self.retranslateUi()

    def stop(self):
        """Stop the video processing and enable loading and start buttons."""
        self.stop_flag=True
        self.ui.pushButton_Load.blockSignals(False)
        self.ui.pushButton_Start.blockSignals(False)

    def help_click (self):
        """Show help information about the FPS field based on the current language."""
        info_fr = "Le FPS représente le nombre d'images à analyser par seconde. Vous pouvez choisir un nombre spécifique ou mettre 0 pour analyser toutes les images de la vidéo."
        info_en = "The FPS represents the number of frames to be analyzed per second. You can choose a specific number or enter 0 to analyze all the video frames."
        global language
        QtWidgets.QMessageBox.information(self, 'Information', info_fr if language=="fr" else info_en)

    def open(self):
        """Open a file dialog to select video files and prepare the first frame for display."""
        self.videos_paths = QFileDialog.getOpenFileNames(self, self.tr('Select your videos'), '.',
                                                         "Video files (*.webm *.mkv *.vob *.avi *.MTS *.mov *.wmv *.mp4 *.mpg *.mpeg *.3gp *.flv)")[0]
        if self.videos_paths:
            self.ui.label_video_number.setText(self.tr('Video ') + '1/' + str(len(self.videos_paths)))
            self.video = cv2.VideoCapture(self.videos_paths[0])
            ret, frame = self.video.read()
            self.video_length = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
            self.display(frame, self.ui.label_display)
            self.ui.progressBar.setValue(0)
            self.ui.progressBar.setMaximum(self.video_length)

            self.v_flag = True
            self.stop_flag = False
            self.ui.pushButton_Dest_folder.setEnabled(False)

    def dest(self):
        """Open the folder where pose estimation results are saved."""
        os.startfile(self.path() + "/Pose_estimations")

    def path(self):
        """Return the directory path of the selected video."""
        head, _ = os.path.split(self.videos_paths[0])
        return head

    def display(self, frame, label):
        """Display the current video frame on the provided label widget."""
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frameb = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_RGB888)
        pix = QPixmap.fromImage(frameb)
        label.setAlignment(Qt.AlignCenter)
        label.setPixmap(pix.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def run(self):
        """Run video analysis, processing each selected video in turn."""
        if not self.v_flag:
            self.ui.label_display.setText(self.tr("Please choose a video to analyze!"))
            return

        for idx, video_path in enumerate(self.videos_paths):
            self.ui.label_video_number.setText(self.tr('Video ') + str(idx + 1) + '/' + str(len(self.videos_paths)))
            self.video_path = video_path
            self.process_video(self.video_path)

        self.ui.pushButton_Dest_folder.setEnabled(True)

    def process_video(self, video_path):
        """Process an individual video file, performing pose estimation on each frame."""
        self.video = cv2.VideoCapture(video_path)
        self.video_fps = int(self.video.get(cv2.CAP_PROP_FPS))
        if not self.set_fps():
            return
        self.detections = pd.DataFrame(columns=dataframe_columns)
        self.ui.radioButton_save.blockSignals(True)
        self.ui.pushButton_Load.blockSignals(True)
        self.ui.pushButton_Start.blockSignals(True)
        self.video_resolution = (int(self.video.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self.video.get(cv2.CAP_PROP_FRAME_HEIGHT)))

        if self.number_fps == 0:
            self.analyze_all_frames()
        else:
            self.analyze_selected_frames()

        self.ui.progressBar.setValue(self.video_length)
        self.save_detections(video_path)
        self.ui.radioButton_save.blockSignals(False)
        self.ui.pushButton_Load.blockSignals(False)
        self.ui.pushButton_Start.blockSignals(False)

    def set_fps(self):
        """Set the desired FPS for video analysis and handle invalid inputs."""
        try:
            self.number_fps = int(self.ui.lineEdit_number_fps.text())
            if self.number_fps < 0 or self.number_fps > self.video_fps:
                raise ValueError
            self.ui.label_number_fps_error.setText("")
            self.fps_flag = True
            return True
        except ValueError:
            self.ui.label_number_fps_error.setText(self.tr("Please choose a valid FPS!"))
            self.fps_flag = False
            return False

    def analyze_all_frames(self):
        """Process every frame of the video for pose estimation."""
        for i in range(self.video_length):
            if self.stop_flag:
                return
            ret, frame = self.video.read()
            if ret:
                if self.ui.radioButton_save.isChecked(): # Check if processed images saving is activated
                    if i == 0:
                        self.save_directory = os.path.join(self.path(), "Pose_estimations", os.path.basename(self.video_path)[:-4] + "_images")
                        if not os.path.exists(self.save_directory):
                            os.makedirs(self.save_directory)

                self.ui.progressBar.setValue(i + 1)
                self.process_frame(frame,i)

    def analyze_selected_frames(self):
        """Process selected frames at specified intervals based on the desired FPS."""
        frame_interval = self.video_fps // self.number_fps
        frame_counter = 0
        for frame_nbr in range(0, self.video_length, frame_interval):
            if self.stop_flag:
                return
            self.video.set(cv2.CAP_PROP_POS_FRAMES, frame_nbr)
            ret, frame = self.video.read()
            if ret:
                if self.ui.radioButton_save.isChecked(): # Check if processed images saving is activated
                    if frame_nbr == 0:
                        self.save_directory = self.path() + "/Pose_estimations/" + os.path.basename(self.video_path)[:-4] + "_images"
                        if not os.path.exists(self.save_directory):
                            os.makedirs(self.save_directory)

                self.ui.progressBar.setValue(frame_nbr + 1)
                self.process_frame(frame,frame_counter)
                frame_counter += 1

    def process_frame(self, frame , frame_number):
        """Perform pose estimation on a single video frame."""
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_tensor = torch.from_numpy(img / 255.).permute(2, 0, 1).float().to(CTX)
        input = [img_tensor]
        pred_boxes = get_person_detection_boxes(box_model, input, threshold=0.9)
        if len(pred_boxes) == 1:
            center, scale = box_to_center_scale(pred_boxes[0], cfg.MODEL.IMAGE_SIZE[0], cfg.MODEL.IMAGE_SIZE[1])
            image_pose = img.copy()
            pose_preds,scores = get_pose_estimation_prediction(pose_model, image_pose, center, scale)

            frame_pose = draw_pose(pose_preds[0], frame)
            self.display(frame_pose, self.ui.label_display)
            self.detections.loc[len(self.detections)] = [[round(triple[0][0]), round(triple[0][1]), round(triple[1][0],2)] for triple in zip(pose_preds[0].tolist(), scores[0].tolist())]
            if self.ui.radioButton_save.isChecked():
                cv2.imwrite(os.path.join(self.save_directory, str(frame_number) + ".jpg"), frame)
            QApplication.processEvents()




    def save_detections(self, video_path):
        """Save the pose detection data to an Excel file in the Pose_estimations directory."""
        if not os.path.isdir(self.path() + "/Pose_estimations"):
            os.mkdir(self.path() + "/Pose_estimations")
        video_name = os.path.basename(video_path)[:-4]
        output_path = os.path.join(self.path(), "Pose_estimations", f"{video_name}.xlsx")
        self.detections.to_excel(output_path, index=True)



if __name__ == "__main__":
    language = "en"
    app = QApplication(sys.argv)
    translator = QTranslator()
    app.installTranslator(translator)
    ScreenSize = QtGui.QGuiApplication.primaryScreen().availableGeometry()
    window = First_window(ScreenSize.height(),ScreenSize.width())
    window.show()
    app.exec_()
    if not window.closed_manually:
        if program == "sequence_selector":
            w = Sequence_selector(ScreenSize.height(),ScreenSize.width())
        else:
            w = Pose_estimator(ScreenSize.height(), ScreenSize.width())
        w.show()
        sys.exit(app.exec_())


