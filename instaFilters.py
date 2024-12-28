import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer
import datetime

# Filters
def apply_filter(frame, filter_name):
    if filter_name == "Rio de Janeiro":
        return cv2.convertScaleAbs(frame, alpha=1.5, beta=20)
    elif filter_name == "Tokyo":
        return cv2.cvtColor(cv2.addWeighted(frame, 0.5, frame, 0, 10), cv2.COLOR_BGR2GRAY)
    elif filter_name == "Cairo":
        return cv2.convertScaleAbs(frame, alpha=1.2, beta=50)
    elif filter_name == "Jaipur":
        return cv2.convertScaleAbs(frame, alpha=1.1, beta=30)
    elif filter_name == "New York":
        return cv2.convertScaleAbs(frame, alpha=1.5, beta=-30)
    elif filter_name == "Buenos Aires":
        return cv2.convertScaleAbs(frame, alpha=1.3, beta=40)
    elif filter_name == "Abu Dhabi":
        return cv2.convertScaleAbs(frame, alpha=1.5, beta=80)
    elif filter_name == "Jakarta":
        return cv2.convertScaleAbs(frame, alpha=1.8, beta=10)
    elif filter_name == "Melbourne":
        return cv2.convertScaleAbs(frame, alpha=0.9, beta=-20)
    elif filter_name == "Lagos":
        return cv2.convertScaleAbs(frame, alpha=1.7, beta=30)
    elif filter_name == "Oslo":
        return cv2.convertScaleAbs(frame, alpha=0.8, beta=-30)
    elif filter_name == "Los Angeles":
        return cv2.convertScaleAbs(frame, alpha=1.1, beta=30)
    elif filter_name == "Paris":
        return cv2.convertScaleAbs(frame, alpha=1.2, beta=20)
    else:
        return frame

class InstaFilterApp(QWidget):
    def __init__(self):
        super().__init__()

        self.filters = ["Original", "Rio de Janeiro", "Tokyo", "Cairo", "Jaipur", "New York", "Buenos Aires",
                        "Abu Dhabi", "Jakarta", "Melbourne", "Lagos", "Oslo", "Los Angeles", "Paris"]
        self.current_filter_index = 0
        self.cap = cv2.VideoCapture(0)

        self.initUI()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(20)

    def initUI(self):
        self.setWindowTitle('Insta Filters')
        self.setGeometry(100, 100, 500, 500)

        # Layouts
        self.layout = QVBoxLayout()

        # Filter name label
        self.filter_name_label = QLabel(self.filters[self.current_filter_index])
        self.layout.addWidget(self.filter_name_label, alignment=Qt.AlignCenter)

        # Preview label
        self.preview_label = QLabel(self)
        self.layout.addWidget(self.preview_label, alignment=Qt.AlignCenter)

        # Next and Previous buttons
        self.button_layout = QHBoxLayout()

        self.prev_button = QPushButton('Previous')
        self.prev_button.clicked.connect(self.prev_filter)
        self.button_layout.addWidget(self.prev_button)

        self.next_button = QPushButton('Next')
        self.next_button.clicked.connect(self.next_filter)
        self.button_layout.addWidget(self.next_button)

        self.layout.addLayout(self.button_layout)

        # Save button
        self.save_button = QPushButton('Save')
        self.save_button.clicked.connect(self.save_frame)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)

    def update_frame(self):
        ret, frame = self.cap.read()
        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, (800, 500), cv2.INTER_AREA)
        if ret:
            filtered_frame = apply_filter(frame, self.filters[self.current_filter_index])
            frame_rgb = cv2.cvtColor(filtered_frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame_rgb.shape
            bytes_per_line = ch * w
            q_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.preview_label.setPixmap(QPixmap.fromImage(q_image))

    def prev_filter(self):
        self.current_filter_index = (self.current_filter_index - 1) % len(self.filters)
        self.filter_name_label.setText(self.filters[self.current_filter_index])

    def next_filter(self):
        self.current_filter_index = (self.current_filter_index + 1) % len(self.filters)
        self.filter_name_label.setText(self.filters[self.current_filter_index])

    def save_frame(self):
        ret, frame = self.cap.read()
        frame = cv2.flip(frame, 1)
        if ret:
            # Apply the currently selected filter to the frame
            filtered_frame = apply_filter(frame, self.filters[self.current_filter_index])

            # Save the image with the current timestamp as the filename
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'{self.filters[self.current_filter_index]}_{timestamp}.png'
            cv2.imwrite(filename, filtered_frame)

            # Show a message box once the image is saved
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText(f'Image saved as {filename}')
            msg.setWindowTitle('Image Saved')
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

            print(f'Image saved as {filename}')

    def closeEvent(self, event):
        self.cap.release()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = InstaFilterApp()
    window.show()
    sys.exit(app.exec_())

