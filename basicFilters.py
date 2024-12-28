import sys
import cv2
import numpy as np
import datetime
from scipy.interpolate import UnivariateSpline
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout, QLabel, QVBoxLayout, QMessageBox
from PyQt5.QtGui import QImage, QPixmap, QPainter, QColor
from PyQt5.QtCore import Qt, QRect, QTimer

def verify_alpha_channel(frame):
    try:
        frame.shape[3] # looking for the alpha channel
    except IndexError:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
    return frame

def apply_sketch(image):
    img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    img_gray_blur = cv2.GaussianBlur(img_gray, (5,5), 0)
    canny_edges = cv2.Canny(img_gray_blur, 10, 70)
    ret, mask = cv2.threshold(canny_edges, 70, 255, cv2.THRESH_BINARY_INV)
    return mask

def apply_HSVFilter(image):
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv_image)
    s.fill(199)
    v.fill(255)
    hsv_image = cv2.merge([h, s, v])
    out = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)
    frame = verify_alpha_channel(image)
    out = verify_alpha_channel(out)
    cv2.addWeighted(out, 0.25, frame, 1.0, .23, frame)
    return frame

def apply_sepia(image):
    # Apply sepia filter
    sepia_filter = np.array([[0.272, 0.534, 0.131],[0.349, 0.686, 0.168],[0.393, 0.769, 0.189]])
    filtered_img = cv2.transform(image, sepia_filter)
    filtered_img = np.clip(filtered_img, 0, 255).astype(np.uint8)
    return filtered_img

def apply_color_overlay(image):
    frame = verify_alpha_channel(image)
    intensity=0.5
    blue=0
    green=231
    red=123
    frame_h, frame_w, frame_c = frame.shape
    sepia_bgra = (blue, green, red, 1)
    overlay = np.full((frame_h, frame_w, 4), sepia_bgra, dtype='uint8')
    cv2.addWeighted(overlay, intensity, frame, 1.0, 0, frame)
    return frame

def apply_invert(img):
    return cv2.bitwise_not(img)

def alpha_blend(frame_1, frame_2, mask):
    alpha = mask/255.0 
    blended = cv2.convertScaleAbs(frame_1*(1-alpha) + frame_2*alpha)
    return blended

def apply_blur(image):
    frame = verify_alpha_channel(image)
    frame_h, frame_w, frame_c = frame.shape
    y = int(frame_h/2)
    x = int(frame_w/2)
    intensity=0.2

    mask = np.zeros((frame_h, frame_w, 4), dtype='uint8')
    cv2.circle(mask, (x, y), int(y/2), (255,255,255), -1, cv2.LINE_AA)
    mask = cv2.GaussianBlur(mask, (21,21),11 )

    blured = cv2.GaussianBlur(frame, (21,21), 11)
    blended = alpha_blend(frame, blured, 255-mask)
    frame = cv2.cvtColor(blended, cv2.COLOR_BGRA2BGR)
    return frame

def apply_portrait_mode(image):
    frame = verify_alpha_channel(image)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 120,255,cv2.THRESH_BINARY)

    mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGRA)
    blured = cv2.GaussianBlur(frame, (21,21), 11)
    blended = alpha_blend(frame, blured, mask)
    frame = cv2.cvtColor(blended, cv2.COLOR_BGRA2BGR)
    return frame

def apply_greyscale(image):
    greyscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return greyscale

def apply_brightness(image):
    img_bright = cv2.convertScaleAbs(image, beta=60)
    return img_bright

def apply_sharpen(image):
    kernel = np.array([[-1, -1, -1], [-1, 9.5, -1], [-1, -1, -1]])
    img_sharpen = cv2.filter2D(image, -1, kernel)
    return img_sharpen

def apply_pencil_sketch(image):
    sk_gray, sk_color = cv2.pencilSketch(image, sigma_s=60, sigma_r=0.07, shade_factor=0.1) 
    return  sk_gray

def apply_HDR(image):
    hdr = cv2.detailEnhance(image, sigma_s=12, sigma_r=0.15)
    return  hdr
def LookupTable(x, y):
  spline = UnivariateSpline(x, y)
  return spline(range(256))

def apply_summer(image):
    increaseLookupTable = LookupTable([0, 64, 128, 256], [0, 80, 160, 256])
    decreaseLookupTable = LookupTable([0, 64, 128, 256], [0, 50, 100, 256])
    blue_channel, green_channel,red_channel  = cv2.split(image)
    red_channel = cv2.LUT(red_channel, increaseLookupTable).astype(np.uint8)
    blue_channel = cv2.LUT(blue_channel, decreaseLookupTable).astype(np.uint8)
    sum= cv2.merge((blue_channel, green_channel, red_channel ))
    return sum

def apply_winter(image):
    increaseLookupTable = LookupTable([0, 64, 128, 256], [0, 80, 160, 256])
    decreaseLookupTable = LookupTable([0, 64, 128, 256], [0, 50, 100, 256])
    blue_channel, green_channel,red_channel = cv2.split(image)
    red_channel = cv2.LUT(red_channel, decreaseLookupTable).astype(np.uint8)
    blue_channel = cv2.LUT(blue_channel, increaseLookupTable).astype(np.uint8)
    win= cv2.merge((blue_channel, green_channel, red_channel))
    return win


def apply_filter(img, filter_type):
    if filter_type == "Sepia":
        return apply_sepia(img)
    elif filter_type == "Invert":
        return apply_invert(img)
    elif filter_type == "Sketch":
        return apply_sketch(img.copy())
    elif filter_type == "HSVFilter":
        return apply_HSVFilter(img.copy())
    elif filter_type == "Color OverLay":
        return apply_color_overlay(img.copy())
    elif filter_type == "Blur":
        return apply_blur(img)
    elif filter_type == "Portrait Mode":
        return apply_portrait_mode(img)
    elif filter_type == "Gray Scale":
        return apply_greyscale(img)
    elif filter_type == "Bright":
        return apply_brightness(img)
    elif filter_type == "Sharpen":
        return apply_sharpen(img)
    elif filter_type == "Pencil Sketch":
        return apply_pencil_sketch(img)
    elif filter_type == "HDR":
        return apply_HDR(img)
    elif filter_type == "Summer":
        return apply_summer(img)
    elif filter_type == "Winter":
        return apply_winter(img)
    else:
        return img

class BasicFilterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.cap = cv2.VideoCapture(0)  # Capture from the default camera
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Update every 30 ms

    def init_ui(self):
        self.setWindowTitle('Basic Filters')
        self.setGeometry(100, 100, 1000, 700)

        self.grid = QGridLayout()
        self.setLayout(self.grid)

        # List of filters
        self.filters = ["Original", "Sepia", "Invert", "Sketch", "HSVFilter", 
                        "Color OverLay", "Blur", "Portrait Mode", "Gray Scale", "Bright", 
                        "Sharpen", "Pencil Sketch", "HDR", "Summer", "Winter"]

        # Create labels to display the filters
        self.labels = []
        self.selected_filter_index = 0  # Default selected filter is the first one

        for i in range(15):
            vbox = QVBoxLayout()  # Vertical layout to hold image and text
            label = QLabel(self)
            label.setFixedSize(150, 150)
            label.setStyleSheet("border: 1px solid black;")  # Border for all filters
            label.mousePressEvent = lambda event, idx=i: self.filter_selected(idx)

            # Text below the filter
            filter_text = QLabel(self.filters[i], alignment=Qt.AlignCenter)
            filter_text.setStyleSheet("font-size: 14px; color: white;")

            # Create a widget to hold the layout
            filter_widget = QWidget(self)
            filter_layout = QVBoxLayout(filter_widget)
            filter_layout.addWidget(label)
            filter_layout.addWidget(filter_text)

            self.labels.append(label)
            self.grid.addWidget(filter_widget, i // 5, i % 5)  # Add the widget to the grid layout

        # Create a Save Button
        self.save_button = QPushButton('Save', self)
        self.save_button.clicked.connect(self.save_filter)
        self.grid.addWidget(self.save_button, 3, 2, alignment=Qt.AlignCenter)

        # Highlight the original (first) filter with a green box
        self.update_highlight()

    def update_frame(self):
        """Capture the frame from the camera and display the selected filter."""
        ret, frame = self.cap.read()
        frame = cv2.flip(frame, 1)
        if ret and frame is not None:
            # Resize frame to 200x200 for display in each filter
            frame = cv2.resize(frame, (200, 200))
            
            # Apply the selected filter to the frame
            filtered_frame = apply_filter(frame, self.filters[self.selected_filter_index])

            # Convert to QPixmap for display
            pixmap = self.convert_cv_qt(filtered_frame)

            # Update all labels with filtered images (same filter for now)
            for i, label in enumerate(self.labels):
                filter_frame = apply_filter(frame, self.filters[i])
                pixmap = self.convert_cv_qt(filter_frame)
                label.setPixmap(pixmap)

            # Update the highlight
            self.update_highlight()

    def convert_cv_qt(self, cv_img):
        """Convert from OpenCV image format to QPixmap"""
        if cv_img is not None:
            rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            return QPixmap.fromImage(convert_to_Qt_format)
        return QPixmap()

    def filter_selected(self, index):
        """Handle filter selection and highlight"""
        self.selected_filter_index = index
        self.update_highlight()

    def update_highlight(self):
        """Update the green highlight on the selected filter"""
        for i, label in enumerate(self.labels):
            if i == self.selected_filter_index:
                label.setStyleSheet("border: 3px solid green;")  # Green border for selected
            else:
                label.setStyleSheet("border: 1px solid black;")  # Black border for others

    def save_filter(self):
        """Save the current frame with the selected filter"""
        ret, frame = self.cap.read()
        frame = cv2.flip(frame, 1)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        if ret:
            selected_filter = apply_filter(frame, self.filters[self.selected_filter_index])
            filter_name = self.filters[self.selected_filter_index]
            filename = f"{filter_name}_{timestamp}.png"
            cv2.imwrite(filename, selected_filter)
            QMessageBox.information(self, "Image Saved", f"Image saved as {filename}", QMessageBox.Ok)
            print(f"Filter saved as {filename}")

    def closeEvent(self, event):
        self.cap.release()

def main():
    app = QApplication(sys.argv)
    window = BasicFilterApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
