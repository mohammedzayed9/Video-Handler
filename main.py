import sys
import os
import csv
import cv2
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QFileDialog, QHBoxLayout, QComboBox, QCheckBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import VideoFileClip, AudioFileClip


class VideoProcessingThread(QThread):
    processingFinished = pyqtSignal()
    processingError = pyqtSignal(str)
    currentTaskChanged = pyqtSignal(str)

    def __init__(self, folder_path, tasks, extract_metadata):
        super().__init__()
        self.folder_path = folder_path
        self.tasks = tasks
        self.extract_metadata = extract_metadata

    def run(self):
        try:
            # Process videos
            report_data = []
            total_files = len([file for file in os.listdir(self.folder_path) if
                              file.lower().endswith(
                                  (".mp4", ".avi", ".mkv", ".3gp", ".wmv", ".flv", ".mov", ".m4v", ".mpeg", ".mpg"))])
            file_number = 1
            for file_name in os.listdir(self.folder_path):
                if file_name.lower().endswith(
                        (".mp4", ".avi", ".mkv", ".3gp", ".wmv", ".flv", ".mov", ".m4v", ".mpeg", ".mpg")):
                    video_path = os.path.join(self.folder_path, file_name)
                    video = VideoFileClip(video_path)
                    duration = video.duration

                    # Create separate folders for each task
                    for task in self.tasks:
                        task_folder = os.path.join(self.folder_path, task)
                        os.makedirs(task_folder, exist_ok=True)

                    video_report = {
                        "File Name": file_name,
                        "Tasks": [],
                    }

                    # Perform selected tasks
                    for task in self.tasks:
                        self.currentTaskChanged.emit(task)  # Emit signal for current task
                        if task == "segmented":
                            segment_ratio = 0.5
                            start_time = 0
                            end_time = duration * segment_ratio
                            segment = video.subclip(start_time, end_time)
                            segment_name = f"{file_name}_segment_{segment_ratio}.mp4"
                            segment_path = os.path.join(self.folder_path, task, segment_name)
                            segment.write_videofile(segment_path)
                            video_report["Tasks"].append("Segmented")
                        elif task == "converted":
                            new_format = "avi"
                            new_path = os.path.join(self.folder_path, task, f"converted_{file_name}.{new_format}")
                            video.write_videofile(new_path, codec="libx264")
                            video_report["Tasks"].append("Converted")
                        elif task == "audio":
                            audio_path = os.path.join(self.folder_path, task, f"audio_{file_name}.mp3")
                            audio = video.audio
                            audio.write_audiofile(audio_path)
                            video_report["Tasks"].append("Extracted Audio")
                        elif task == "resized":
                            resize_option = "360p"
                            resized_path = os.path.join(self.folder_path, task, f"resized_{file_name}")
                            if resize_option == "Original":
                                resized_video = video
                            elif resize_option == "144p":
                                resized_video = video.resize(height=144)
                            elif resize_option == "240p":
                                resized_video = video.resize(height=240)
                            elif resize_option == "360p":
                                resized_video = video.resize(height=360)
                            elif resize_option == "480p":
                                resized_video = video.resize(height=480)
                            elif resize_option == "720p":
                                resized_video = video.resize(height=720)
                            elif resize_option == "1080p":
                                resized_video = video.resize(height=1080)
                            else:
                                error_message = "Invalid resize option"
                                self.processingError.emit(error_message)
                                return
                            resized_video.write_videofile(resized_path)
                            video_report["Tasks"].append("Resized")
                        elif task == "frames":
                            frame_folder = os.path.join(self.folder_path, task, f"frames_{file_name}")
                            os.makedirs(frame_folder, exist_ok=True)
                            frame_count = 0
                            for t in range(int(duration)):
                                frame = video.get_frame(t)
                                frame_name = f"frame_{t}.jpg"
                                frame_path = os.path.join(frame_folder, frame_name)
                                cv2.imwrite(frame_path, frame)
                                frame_count += 1
                            print(f"{frame_count} frames extracted for {file_name}")
                            video_report["Tasks"].append("Extracted Frames")
                        elif task == "thumbnail":
                            thumbnail_folder = os.path.join(self.folder_path, task)
                            os.makedirs(thumbnail_folder, exist_ok=True)
                            thumbnail_name = f"thumbnail_{file_name}.jpg"
                            thumbnail_path = os.path.join(thumbnail_folder, thumbnail_name)
                            generate_thumbnail(video_path, thumbnail_path)
                            video_report["Tasks"].append("Thumbnail Generated")

                    if self.extract_metadata:
                        video_metadata = extract_video_metadata(video_path)
                        video_report["Metadata"] = video_metadata

                    report_data.append(video_report)

                    # Emit signal with progress information
                    progress_info = f"Processing: File {file_number}/{total_files}"
                    self.currentTaskChanged.emit(progress_info)
                    file_number += 1

            # Generate report CSV file
            report_folder = os.path.join(self.folder_path, "report")
            os.makedirs(report_folder, exist_ok=True)
            report_path = os.path.join(report_folder, "videos_report.csv")

            with open(report_path, mode="w", newline="") as file:
                fieldnames = ["File Name", "Tasks"]
                if self.extract_metadata:
                    fieldnames.append("Metadata")
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(report_data)

            self.processingFinished.emit()

        except Exception as e:
            error_message = str(e)
            self.processingError.emit(error_message)


def generate_thumbnail(video_path, thumbnail_path):
    video = cv2.VideoCapture(video_path)
    success, frame = video.read()
    if success:
        cv2.imwrite(thumbnail_path, frame)
    video.release()


def extract_video_metadata(video_path):
    video = cv2.VideoCapture(video_path)
    frame_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_rate = int(video.get(cv2.CAP_PROP_FPS))
    duration = int(video.get(cv2.CAP_PROP_FRAME_COUNT)) // frame_rate
    codec = video.get(cv2.CAP_PROP_FOURCC)
    video.release()

    metadata = {
        "Resolution": f"{frame_width}x{frame_height}",
        "Frame Rate": f"{frame_rate} fps",
        "Duration": f"{duration} seconds",
        "Codec": codec,
    }
    return metadata


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create UI elements
        self.setWindowTitle("Video Automation App")
        self.setGeometry(200, 200, 400, 250)

        self.folder_button = QPushButton("Select Folder", self)
        self.folder_button.clicked.connect(self.select_folder)

        self.process_button = QPushButton("Process Videos", self)
        self.process_button.clicked.connect(self.process_videos)

        self.status_label = QLabel("Select a folder to begin", self)
        self.status_label.setAlignment(Qt.AlignCenter)

        self.processing_label = QLabel("Processing: None", self)
        self.processing_label.setAlignment(Qt.AlignCenter)

        self.segment_checkbox = QCheckBox("Segment Videos", self)
        self.segment_ratio_combo = QComboBox(self)
        self.segment_ratio_combo.addItems(["25%", "30%", "50%"])

        self.format_checkbox = QCheckBox("Convert Format", self)
        self.format_combo = QComboBox(self)
        self.format_combo.addItems(["avi", "mp4", "mov"])

        self.audio_checkbox = QCheckBox("Extract Audio", self)

        self.resize_checkbox = QCheckBox("Resize Videos", self)
        self.resize_combo = QComboBox(self)
        self.resize_combo.addItems(["Original", "144p", "240p", "360p", "480p", "720p", "1080p"])

        self.frames_checkbox = QCheckBox("Extract Frames", self)

        self.thumbnail_checkbox = QCheckBox("Generate Thumbnails", self)

        self.metadata_checkbox = QCheckBox("Extract Metadata", self)

        layout = QVBoxLayout()
        layout.addWidget(self.folder_button)
        layout.addWidget(self.process_button)
        layout.addWidget(self.status_label)
        layout.addWidget(self.processing_label)

        tasks_layout = QHBoxLayout()
        tasks_layout.addWidget(self.segment_checkbox)
        tasks_layout.addWidget(self.segment_ratio_combo)
        tasks_layout.addWidget(self.format_checkbox)
        tasks_layout.addWidget(self.format_combo)
        tasks_layout.addWidget(self.audio_checkbox)
        tasks_layout.addWidget(self.resize_checkbox)
        tasks_layout.addWidget(self.resize_combo)
        tasks_layout.addWidget(self.frames_checkbox)
        tasks_layout.addWidget(self.thumbnail_checkbox)
        tasks_layout.addWidget(self.metadata_checkbox)
        layout.addLayout(tasks_layout)

        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.folder_path = None
        self.extract_metadata = False

    def select_folder(self):
        self.folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if self.folder_path:
            self.status_label.setText("Folder selected: " + self.folder_path)
        else:
            self.status_label.setText("Select a folder to begin")

    def process_videos(self):
        if self.folder_path is None:
            self.status_label.setText("Please select a folder first")
            return

        # Get selected tasks
        tasks = []
        if self.segment_checkbox.isChecked():
            tasks.append("segmented")
        if self.format_checkbox.isChecked():
            tasks.append("converted")
        if self.audio_checkbox.isChecked():
            tasks.append("audio")
        if self.resize_checkbox.isChecked():
            tasks.append("resized")
        if self.frames_checkbox.isChecked():
            tasks.append("frames")
        if self.thumbnail_checkbox.isChecked():
            tasks.append("thumbnail")

        self.extract_metadata = self.metadata_checkbox.isChecked()

        # Start video processing thread
        self.process_button.setEnabled(False)
        self.status_label.setText("Processing videos...")
        self.video_processing_thread = VideoProcessingThread(self.folder_path, tasks, self.extract_metadata)
        self.video_processing_thread.processingFinished.connect(self.processing_finished)
        self.video_processing_thread.processingError.connect(self.processing_error)
        self.video_processing_thread.currentTaskChanged.connect(self.update_processing_label)
        self.video_processing_thread.start()

    def processing_finished(self):
        self.process_button.setEnabled(True)
        self.status_label.setText("Videos processed successfully")

    def processing_error(self, error_message):
        self.process_button.setEnabled(True)
        self.status_label.setText("Error occurred: " + error_message)

    def update_processing_label(self, task):
        self.processing_label.setText(task)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
