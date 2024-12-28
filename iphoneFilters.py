import sys
import cv2
import numpy as np
import datetime
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QScrollArea, QHBoxLayout, QPushButton, QMessageBox, QFileDialog

class IphoneFilterApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Iphone Filters")
        self.setGeometry(100, 100, 1090, 1080)
        self.cap = None  
        self.selected_filter = "Original"
        self.current_image = None  

        # Create layout
        main_layout = QHBoxLayout()

        # Left section with preview, buttons, and save button
        left_layout = QVBoxLayout()

        # Top section: Three buttons for loading, uploading, or opening the camera
        self.load_sample_button = QPushButton("Load Sample Image")
        self.upload_image_button = QPushButton("Upload Image")
        self.open_camera_button = QPushButton("Open Camera")

        self.load_sample_button.clicked.connect(self.load_sample_image)
        self.upload_image_button.clicked.connect(self.upload_image)
        self.open_camera_button.clicked.connect(self.open_camera)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.load_sample_button)
        button_layout.addWidget(self.upload_image_button)
        button_layout.addWidget(self.open_camera_button)

        left_layout.addLayout(button_layout)

        # Middle section: Preview of the selected filter
        self.preview_label = QLabel()
        self.preview_label.setFixedSize(640, 480)
        left_layout.addWidget(self.preview_label, alignment=Qt.AlignCenter)

        # Bottom section: Save button
        self.save_button = QPushButton("Save Filtered Image")
        self.save_button.clicked.connect(self.save_image)
        left_layout.addWidget(self.save_button)

        main_layout.addLayout(left_layout)

        # Right section: Vertical scrollable area with filters
        self.scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        self.frames = {}  # Store filter names and associated QLabel for each filter
        filters = ["Original", "Vivid", "Vivid Warm", "Vivid Cool", "Dramatic", "Dramatic Warm", "Dramatic Cool", "Mono", "Silvertone", "Noir"]
        for filter_name in filters:
            vbox = QVBoxLayout()
            label = QLabel()
            label.setFixedSize(320, 240)
            filter_text = QLabel(filter_name, alignment=Qt.AlignCenter)
            vbox.addWidget(label)
            vbox.addWidget(filter_text)
            scroll_layout.addLayout(vbox)
            self.frames[filter_name] = label

        self.scroll_area.setWidget(scroll_widget)
        self.scroll_area.setWidgetResizable(True)
        main_layout.addWidget(self.scroll_area)

        self.setLayout(main_layout)

        # Timer for capturing frames from the camera (only starts if camera is opened)
        self.timer = QTimer()

    def update_frames(self):
        if self.cap is None:
            return
        
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            frame = cv2.resize(frame, (320, 240), cv2.INTER_AREA)

            # Show original frame
            self.display_frame(frame, "Original")

            # Apply filters and display
            self.display_frame(self.apply_vivid(frame), "Vivid")
            self.display_frame(self.apply_vivid_warm(frame), "Vivid Warm")
            self.display_frame(self.apply_vivid_cool(frame), "Vivid Cool")
            self.display_frame(self.apply_dramatic(frame), "Dramatic")
            self.display_frame(self.apply_dramatic_warm(frame), "Dramatic Warm")
            self.display_frame(self.apply_dramatic_cool(frame), "Dramatic Cool")
            self.display_frame(self.apply_mono(frame), "Mono")
            self.display_frame(self.apply_silvertone(frame), "Silvertone")
            self.display_frame(self.apply_noir(frame), "Noir")

    def display_frame(self, frame, filter_name):
        # Convert to RGB for PyQt
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        q_img = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img)

        # Display in the appropriate label
        self.frames[filter_name].setPixmap(pixmap)

        # If filter is selected, update the preview
        if self.selected_filter == filter_name:
            self.preview_label.setPixmap(pixmap.scaled(640, 480, Qt.KeepAspectRatio))
            self.current_image = pixmap  # Save the current image
    
    def load_sample_image(self):
        # Stop camera and load a sample image
        self.stop_camera()

        # Load a sample image from disk
        sample_image = cv2.imread("sample.jpg")
        # self.display_frame(sample_image, "Original")
        self.update_display_with_image(sample_image)

    def upload_image(self):
        # Stop camera and allow user to upload an image
        self.stop_camera()

        # Open a file dialog to upload image
        file_path, _ = QFileDialog.getOpenFileName(self, "Upload Image", "", "Image Files (*.png *.jpg *.jpeg)")
        if file_path:
            uploaded_image = cv2.imread(file_path)
            self.update_display_with_image(uploaded_image)

    def open_camera(self):
        # Open the camera and start capturing frames
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)
            self.timer.timeout.connect(self.update_frames)
            self.timer.start(30)

    def stop_camera(self):
        # Stop the camera if it's running
        if self.cap:
            self.timer.stop()
            self.cap.release()
            self.cap = None

    
    def update_display_with_image(self,image):
        
        frame = cv2.resize(image, (320, 240), cv2.INTER_AREA)
        self.display_frame(frame, "Original")
        self.display_frame(self.apply_vivid(frame), "Vivid")
        self.display_frame(self.apply_vivid_warm(frame), "Vivid Warm")
        self.display_frame(self.apply_vivid_cool(frame), "Vivid Cool")
        self.display_frame(self.apply_dramatic(frame), "Dramatic")
        self.display_frame(self.apply_dramatic_warm(frame), "Dramatic Warm")
        self.display_frame(self.apply_dramatic_cool(frame), "Dramatic Cool")
        self.display_frame(self.apply_mono(frame), "Mono")
        self.display_frame(self.apply_silvertone(frame), "Silvertone")
        self.display_frame(self.apply_noir(frame), "Noir")


    def apply_vivid(self, img):
        contrast_value = 1.32
        return np.clip(((1.0 + contrast_value - 1.0)) * img, 0, 255).astype(np.uint8)

    def apply_vivid_warm(self, img):
        contrast_value = 0.61
        red_value = 31
        green_value = 11
        img = np.clip(((1.0 + contrast_value - 1.0)) * img, 0, 255).astype(np.uint8)
        img[:, :, 2] = np.clip(img[:, :, 2] + red_value, 0, 255)  # Red channel
        img[:, :, 1] = np.clip(img[:, :, 1] + green_value, 0, 255)  # Green channel
        return img

    def apply_vivid_cool(self, img):
        contrast_value = 0.6
        blue_value = 15
        img = np.clip(((1.0 + contrast_value - 1.0)) * img, 0, 255).astype(np.uint8)
        img[:, :, 0] = np.clip(img[:, :, 0] + blue_value, 0, 255)  # Blue channel
        return img
    
    def apply_dramatic(self,img):
        highlights_value = 25
        shadows_value = 41
        img = img.astype(np.float32)

        # Normalize highlights and shadows values to [0, 1] range
        highlights_factor = highlights_value / 100.0
        shadows_factor = shadows_value / 100.0

        # Apply highlights adjustment
        img = np.clip(img * (1 + highlights_factor), 0, 255)

        # Apply shadows adjustment
        img = np.clip(img * (1 - shadows_factor), 0, 255)

        return img.astype(np.uint8)
    
    def apply_dramatic_warm(self,img):
        highlights_value = 25
        shadows_value = 41
        red_value = 31
        green_value = 11
        img = img.astype(np.float32)

        # Normalize highlights and shadows values to [0, 1] range
        highlights_factor = highlights_value / 100.0
        shadows_factor = shadows_value / 100.0

        # Apply highlights adjustment
        img = np.clip(img * (1 + highlights_factor), 0, 255)

        # Apply shadows adjustment
        img = np.clip(img * (1 - shadows_factor), 0, 255)


        img[:, :, 2] = np.clip(img[:, :, 2] + red_value, 0, 255)  # Red channel
        img[:, :, 1] = np.clip(img[:, :, 1] + green_value, 0, 255)  # Green channel

        return img.astype(np.uint8)
    
    def apply_dramatic_cool(self,img):
        highlights_value = 25
        shadows_value = 41
        blue_value = 15
        img = img.astype(np.float32)

        # Normalize highlights and shadows values to [0, 1] range
        highlights_factor = highlights_value / 100.0
        shadows_factor = shadows_value / 100.0

        # Apply highlights adjustment
        img = np.clip(img * (1 + highlights_factor), 0, 255)

        # Apply shadows adjustment
        img = np.clip(img * (1 - shadows_factor), 0, 255)

        img[:, :, 0] = np.clip(img[:, :, 0] + blue_value, 0, 255)  # Blue channel

        return img.astype(np.uint8)
    
    def apply_mono(self, img):
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return gray_img.astype(np.uint8)
    
    def apply_silvertone(self, img):
        shadows_factor = -0.32
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray_img = gray_img.astype(np.float32)
        gray_img = np.clip(gray_img * (1 - shadows_factor), 0, 255)
        return gray_img.astype(np.uint8)

    def apply_noir(self, img):
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        contrast_value = 1.4
        gray_img = gray_img.astype(np.float32)
        return np.clip(((1.0 + contrast_value - 1.0)) * gray_img, 0, 255).astype(np.uint8)


    def save_image(self):
        # Save the previewed image with the filter name
        if self.selected_filter == "None":
            return

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{self.selected_filter}_{timestamp}.png"
        pixmap = self.preview_label.pixmap()
        if pixmap:
            pixmap.save(file_name)
            print(f"Image saved as {file_name}")
            QMessageBox.information(self, "Image Saved", f"Image saved as {file_name}", QMessageBox.Ok)

    def mousePressEvent(self, event):
        # Detect clicks on the right section to select the filter for preview
        clicked_label = self.childAt(event.pos())
        for filter_name, label in self.frames.items():
            if clicked_label == label:
                self.selected_filter = filter_name
                self.update_preview(filter_name)
                break

    def update_preview(self, filter_name):
        # Display the selected filter's frame in the preview
        pixmap = self.frames[filter_name].pixmap()
        if pixmap:
            self.preview_label.setPixmap(pixmap.scaled(640, 480, Qt.KeepAspectRatio))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IphoneFilterApp()
    window.show()
    sys.exit(app.exec_())
